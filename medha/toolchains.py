"""
MEDHĀ IDE — toolchains.py
=========================

WHAT:  Finds every external tool MEDHĀ drives (gcc, g++, gdb, make, javac, java,
       python, clangd, git, cppcheck) and reports its REAL version by running it.
WHY:   v1 called bare names like "gcc" and "python3" and hoped they were on PATH.
       On a fresh Windows PC nothing is on PATH, and C-Lite IDE wins there only
       because it ships its own compiler. MEDHĀ now looks in this order:
         1. settings  — a path the user picked in Tools → Toolchains (explicit choice wins)
         2. bundled   — <app>/toolchains/... shipped inside the MSIX (offline)
         3. PATH      — whatever the system already has
         4. common install folders (MSYS2, WinLibs, TDM-GCC, Adoptium JDK, ...)
       A tool only counts as found if `<tool> --version` actually runs — so a
       broken PATH entry or the Microsoft Store "python.exe" stub is not used.
USED BY: runner.py (compile/run), turbo/builder.py (Turbo C build),
       debugger.py (gdb), lsp.py (clangd), toolchains_dialog.py (shows the table).
FLOW:  find("gcc") → Tool(path, version, source) or Tool(path=None) →
       runner shows a clear "install / bundle" message when a tool is missing.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass

from medha import settings
from medha.platform_info import EXE, IS_FROZEN, IS_WINDOWS, bundled_toolchains_dir


@dataclass
class Tool:
    """Result of a lookup. path=None means "not found anywhere"."""
    name: str
    path: str = None
    version: str = ""
    source: str = ""        # "bundled" | "settings" | "PATH" | "common" | "python-runtime"

    @property
    def found(self) -> bool:
        return bool(self.path)


# ---------------------------------------------------------------------------
# What each logical tool is called on disk, and how to ask for its version.
# "names": candidate executable names (first match wins).
# "bundled": sub-folders of <app>/toolchains/ that may contain it (Windows MSIX).
# "version_args": java/javac print version with -version (to stderr).
# ---------------------------------------------------------------------------
TOOLS = {
    "gcc":      {"names": ["gcc"],                 "bundled": ["mingw64/bin"], "version_args": ["--version"]},
    "g++":      {"names": ["g++"],                 "bundled": ["mingw64/bin"], "version_args": ["--version"]},
    "gdb":      {"names": ["gdb"],                 "bundled": ["mingw64/bin"], "version_args": ["--version"]},
    "make":     {"names": ["make", "mingw32-make"], "bundled": ["mingw64/bin"], "version_args": ["--version"]},
    "javac":    {"names": ["javac"],               "bundled": ["jdk/bin"],     "version_args": ["-version"]},
    "java":     {"names": ["java"],                "bundled": ["jdk/bin"],     "version_args": ["-version"]},
    "python":   {"names": ["python3", "python", "py"], "bundled": ["python"],  "version_args": ["--version"]},
    "clangd":   {"names": ["clangd"],              "bundled": ["clangd/bin"],  "version_args": ["--version"]},
    "git":      {"names": ["git"],                 "bundled": [],              "version_args": ["--version"]},
    "cppcheck": {"names": ["cppcheck"],            "bundled": [],              "version_args": ["--version"]},
}

# Typical Windows install locations used when the tool is not on PATH.
# Glob patterns are allowed (version numbers in folder names change).
WINDOWS_COMMON = {
    "mingw": [r"C:\msys64\ucrt64\bin", r"C:\msys64\mingw64\bin", r"C:\mingw64\bin",
              r"C:\MinGW\bin", r"C:\TDM-GCC-64\bin", r"C:\Program Files\mingw-w64\*\mingw64\bin",
              r"C:\Program Files (x86)\Dev-Cpp\MinGW64\bin", r"C:\Program Files\CodeBlocks\MinGW\bin"],
    "jdk":   [r"C:\Program Files\Eclipse Adoptium\jdk-*\bin", r"C:\Program Files\Java\jdk-*\bin",
              r"C:\Program Files\Microsoft\jdk-*\bin"],
    "python": [os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python3*")],
    "clangd": [r"C:\Program Files\LLVM\bin"],
    "git":   [r"C:\Program Files\Git\cmd"],
    "cppcheck": [r"C:\Program Files\Cppcheck"],
}
COMMON_GROUP = {"gcc": "mingw", "g++": "mingw", "gdb": "mingw", "make": "mingw",
                "javac": "jdk", "java": "jdk", "python": "python", "clangd": "clangd",
                "git": "git", "cppcheck": "cppcheck"}

_cache = {}


def clear_cache():
    """Forget previous lookups (called after the user edits a path in Settings)."""
    _cache.clear()


def _probe_version(path, args):
    """Run `<path> --version` and return its first non-empty line, or None if it fails.

    WHY run it instead of trusting the file exists: Windows ships a fake
    `python.exe` in WindowsApps that only opens the Store, and a half-deleted
    MinGW leaves gcc.exe that cannot start. Only a tool that really runs counts.
    """
    try:
        kwargs = {}
        if IS_WINDOWS:
            # do not flash a console window for every probe
            kwargs["creationflags"] = 0x08000000   # CREATE_NO_WINDOW
        r = subprocess.run([path] + list(args), capture_output=True, text=True,
                           timeout=8, errors="replace", **kwargs)
    except (OSError, subprocess.SubprocessError):
        return None
    text = (r.stdout or "") + "\n" + (r.stderr or "")
    if r.returncode != 0 and not text.strip():
        return None
    for line in text.splitlines():
        # The JVM prints "Picked up JAVA_TOOL_OPTIONS: ..." before the version when
        # that variable is set (common on lab PCs and CI) — it is not the version.
        if line.strip() and not line.startswith("Picked up "):
            return line.strip()
    return None


def _candidates_in(folder, names):
    for n in names:
        p = os.path.join(folder, n + EXE)
        if os.path.isfile(p):
            yield p


def find(name, refresh=False) -> Tool:
    """Locate one tool. Results are cached until clear_cache()."""
    if name in _cache and not refresh:
        return _cache[name]
    spec = TOOLS[name]
    names, vargs = spec["names"], spec["version_args"]
    tried = []   # (path, source) in priority order

    # 0) explicit user choice from Settings → Toolchains always wins — the student
    #    (or lab admin) picked it on purpose. If it no longer runs, we fall through.
    custom = (settings.get("tool_paths") or {}).get(name)
    if custom:
        tried.append((custom, "settings"))

    # 1) bundled offline toolchain inside the app
    root = bundled_toolchains_dir()
    for sub in spec["bundled"]:
        for p in _candidates_in(str(root / sub), names):
            tried.append((p, "bundled"))

    # 2) system PATH
    for n in names:
        p = shutil.which(n)
        if p:
            tried.append((p, "PATH"))

    # 3) well-known install folders (Windows)
    if IS_WINDOWS:
        for pattern in WINDOWS_COMMON.get(COMMON_GROUP.get(name, ""), []):
            for folder in sorted(glob.glob(pattern), reverse=True):   # newest version first
                for p in _candidates_in(folder, names):
                    tried.append((p, "common"))

    seen = set()
    for path, source in tried:
        key = os.path.normcase(os.path.abspath(path))
        if key in seen:
            continue
        seen.add(key)
        version = _probe_version(path, vargs)
        if version:
            tool = Tool(name, path, version, source)
            _cache[name] = tool
            return tool

    # 4) Python only: MEDHĀ itself runs on Python, so in a source checkout the
    #    interpreter running the IDE can run student scripts too. Never in a frozen
    #    build — there sys.executable is MEDHA.exe, not a Python interpreter.
    if name == "python" and not IS_FROZEN and sys.executable:
        version = _probe_version(sys.executable, vargs)
        if version:
            tool = Tool(name, sys.executable, version, "python-runtime")
            _cache[name] = tool
            return tool

    tool = Tool(name)
    _cache[name] = tool
    return tool


def require(name):
    """Return the tool path or raise ToolMissing with a student-friendly message."""
    tool = find(name)
    if not tool.found:
        raise ToolMissing(name)
    return tool.path


class ToolMissing(RuntimeError):
    """Raised when a tool is needed but not installed/bundled — runner shows .hint."""

    HINTS_WINDOWS = {
        "gcc": "MEDHĀ's Store build ships GCC in its toolchains folder. If you run from source, "
               "install MSYS2/WinLibs MinGW-w64 or set the path in Tools → Toolchains.",
        "javac": "Install a JDK (Eclipse Temurin 25 LTS) or set the javac path in Tools → Toolchains.",
        "python": "Install Python 3 from python.org (tick 'Add to PATH') or set its path in Tools → Toolchains.",
    }
    HINTS_LINUX = {
        "gcc": "Install it: sudo apt install build-essential   (Fedora: sudo dnf install gcc gcc-c++)",
        "g++": "Install it: sudo apt install g++",
        "gdb": "Install it: sudo apt install gdb",
        "javac": "Install a JDK: sudo apt install openjdk-25-jdk  (or openjdk-21-jdk)",
        "java": "Install a JDK: sudo apt install openjdk-25-jdk  (or openjdk-21-jdk)",
        "python": "Install it: sudo apt install python3",
        "clangd": "Install it: sudo apt install clangd",
        "cppcheck": "Install it: sudo apt install cppcheck",
    }

    def __init__(self, name):
        self.tool = name
        table = self.HINTS_WINDOWS if IS_WINDOWS else self.HINTS_LINUX
        base = name if name not in ("g++", "gdb", "make") or not IS_WINDOWS else "gcc"
        self.hint = table.get(name) or table.get(base) or "Set its path in Tools → Toolchains."
        super().__init__(f"'{name}' was not found. {self.hint}")


# ---------------------------------------------------------------------------
# Language standards: offer only what the detected compiler really supports.
# GCC added -std=c2x in 9, c23 in 14; -std=c++2a in 8, c++20 in 10, c++23 in 11
# (spelled c++2b before 14). We read the major version from `gcc --version`.
# ---------------------------------------------------------------------------
def gcc_major(tool: Tool):
    m = re.search(r"(\d+)\.\d+(\.\d+)?", tool.version or "")
    return int(m.group(1)) if m else None


def supported_c_standards():
    major = gcc_major(find("gcc")) or 0
    stds = ["c89", "c99", "c11", "c17", "gnu89", "gnu99", "gnu11", "gnu17"]
    if major >= 14:
        stds += ["c23", "gnu23"]
    elif major >= 9:
        stds += ["c2x", "gnu2x"]
    return stds


def supported_cpp_standards():
    major = gcc_major(find("g++")) or 0
    stds = ["c++98", "c++11", "c++14", "c++17", "gnu++11", "gnu++14", "gnu++17"]
    if major >= 10:
        stds += ["c++20", "gnu++20"]
    if major >= 14:
        stds += ["c++23", "gnu++23"]
    elif major >= 11:
        stds += ["c++2b", "gnu++2b"]
    return stds


def report():
    """[(name, Tool)] for every known tool — used by the Toolchains page and tests."""
    return [(n, find(n)) for n in TOOLS]


if __name__ == "__main__":
    # `python -m medha.toolchains` prints the real table — handy on a lab PC.
    for n, t in report():
        print(f"{n:9} {t.source or '-':15} {t.path or 'NOT FOUND'}  {t.version}")
