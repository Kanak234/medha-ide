"""
MEDHĀ IDE — platform_info.py
============================

WHAT:  One small place that answers "which OS am I on, and where do things live?"
       Every other module asks this file instead of hardcoding Linux paths.
WHY:   MEDHĀ v1 assumed Linux everywhere (`/bin/bash`, `~/.local/bin`, binaries
       without `.exe`). That is exactly what breaks on Windows / Microsoft Store.
       Keeping all OS decisions here means the rest of the code stays the same on
       Linux and Windows.
USED BY: toolchains.py (where compilers are), terminal.py (which shell),
       runner.py (`.exe` suffix, build folder), settings.py (where config lives),
       turbo/builder.py (runtime cache folder).
FLOW:  module import → constants computed once → other modules read them.
"""

import os
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# 1) Which operating system?
#    sys.platform is "win32" on every Windows (32 and 64 bit), "linux" on Linux,
#    "darwin" on macOS. We only need these three answers.
# ---------------------------------------------------------------------------
IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

# Executables on Windows end in ".exe" — gcc writes `program.exe`, and we must
# look for `gcc.exe` on disk. On Linux/macOS there is no suffix.
EXE = ".exe" if IS_WINDOWS else ""

# ---------------------------------------------------------------------------
# 2) Is this a packaged build (PyInstaller / MSIX / snap) or a source checkout?
#    PyInstaller sets sys.frozen and unpacks data next to the exe (sys._MEIPASS).
#    WHY it matters: in a frozen build sys.executable is MEDHA.exe, NOT python,
#    so we must never use it to run the student's .py files.
# ---------------------------------------------------------------------------
IS_FROZEN = bool(getattr(sys, "frozen", False))


def app_root() -> Path:
    """Folder that holds MEDHĀ's own read-only files (runtime, examples, toolchains).

    Source checkout → the repository root (parent of the `medha/` package).
    PyInstaller     → the unpack folder (sys._MEIPASS), where the .spec copies data.
    Snap            → $SNAP/app (see snap/snapcraft.yaml).
    """
    if IS_FROZEN and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    snap = os.environ.get("SNAP")
    if snap and (Path(snap) / "app").is_dir():
        return Path(snap) / "app"
    return Path(__file__).resolve().parent.parent


def package_dir() -> Path:
    """The `medha/` package folder itself (holds turbo/runtime etc.)."""
    return Path(__file__).resolve().parent


def bundled_toolchains_dir() -> Path:
    """Where an offline toolchain bundle (MinGW-w64, JDK, Python) is shipped.

    The Windows MSIX build places compilers in `<app>/toolchains/`. On Linux this
    folder normally does not exist and MEDHĀ uses the system compilers instead.
    """
    return app_root() / "toolchains"


def user_data_dir() -> Path:
    """Writable per-user folder for settings, caches and logs.

    Windows → %LOCALAPPDATA%\\MEDHA   (MSIX virtualises this per package — good)
    macOS   → ~/Library/Application Support/MEDHA
    Linux   → $XDG_DATA_HOME/medha or ~/.local/share/medha
    WHY not the install folder: MSIX installs are read-only, and Program Files
    is not writable without admin rights.
    """
    if IS_WINDOWS:
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        path = base / "MEDHA"
    elif IS_MAC:
        path = Path.home() / "Library" / "Application Support" / "MEDHA"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
        path = base / "medha"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> Path:
    """Writable cache (compiled Turbo C runtime objects, build outputs)."""
    path = user_data_dir() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ascii_work_dir() -> Path:
    """A temp folder whose path is plain ASCII.

    WHY: MinGW's gcc/ld cannot open paths with Hindi (or any non-ASCII) letters —
    a student whose Windows username is in Devanagari gets
    `ld: cannot open output file`. PRABHA solved this the same way; we reuse the idea.
    FLOW: runner.py / turbo/builder.py put temporary build files here.
    """
    t = Path(tempfile.gettempdir())
    if not IS_WINDOWS or str(t).isascii():
        work = t / "medha-work"
    else:
        work = Path(os.environ.get("PUBLIC") or r"C:\Users\Public") / "medha-work"
    work.mkdir(parents=True, exist_ok=True)
    return work


def default_shell() -> tuple:
    """Program + arguments for the integrated terminal.

    Windows → cmd.exe in quiet mode. cmd reads commands from a pipe line by line,
    which is exactly how QProcess feeds it. (PowerShell buffers piped input until
    EOF, so typed commands would not run one by one.)
    Linux/macOS → the user's $SHELL in interactive mode (bash -i shows a prompt).
    FLOW: terminal.py → QProcess.start(program, args)
    """
    if IS_WINDOWS:
        comspec = os.environ.get("COMSPEC") or r"C:\Windows\System32\cmd.exe"
        return comspec, ["/Q"]
    shell = os.environ.get("SHELL") or "/bin/bash"
    return shell, ["-i"]


def extend_path(dirs) -> None:
    """Prepend folders to PATH using the OS's own separator (';' on Windows, ':' elsewhere).

    WHY: v1 did `f"{dir}:{PATH}"`, which corrupts PATH on Windows (C:\\ has a colon).
    """
    current = os.environ.get("PATH", "")
    parts = current.split(os.pathsep) if current else []
    for d in reversed([str(x) for x in dirs if x]):
        if d not in parts and os.path.isdir(d):
            parts.insert(0, d)
    os.environ["PATH"] = os.pathsep.join(parts)
