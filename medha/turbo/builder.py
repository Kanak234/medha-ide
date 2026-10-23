"""
MEDHĀ IDE — turbo/builder.py
============================

WHAT:  Plans how to compile a C/C++ program that needs Turbo mode:
         step 1 (once per compiler): compile runtime/prabha_core.c → cached .o
         step 2: compile the (adapted temp copy of the) student file + core.o → exe
       Returns a BuildPlan: a list of (program, args, cwd) commands the runner
       executes one after another with QProcess (non-blocking UI).
WHY:   Port of PRABHA's lib/build.js rules so MEDHĀ and PRABHA build identically:
       -std=gnu99 for C, -std=gnu++14 -fpermissive + compat headers for Turbo C++,
       -lm for math, -static on Windows (no missing-DLL errors on lab PCs),
       unbuffered stdout for console programs, ASCII work folder for Hindi paths.
USED BY: runner.py when turbo.adapt.needs_turbo(source) is True.
FLOW:  plan(file, gcc, gxx, debug) → BuildPlan → runner runs steps → plan.binary
       → runner starts it with PRABHA_PROTO_FD=1 → protocol.py decodes the screen.
"""

import hashlib
import os
import tempfile
from dataclasses import dataclass, field

from medha import platform_info as P
from medha.turbo.adapt import adapt, uses_panel

RUNTIME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime")


@dataclass
class BuildPlan:
    steps: list = field(default_factory=list)   # [(program, [args], cwd, label)]
    binary: str = ""                             # program to run after a successful build
    source_map: dict = field(default_factory=dict)  # temp path → user's real file
    uses_panel: bool = False                     # graphics.h / conio.h → show the 640×480 screen
    is_cpp: bool = False
    notes: list = field(default_factory=list)    # "void main() adapted ..." shown in the terminal
    work_dir: str = ""


def _ascii_runtime():
    """MinGW cannot open non-ASCII paths: copy the runtime to an ASCII folder if needed."""
    if not P.IS_WINDOWS or RUNTIME_DIR.isascii():
        return RUNTIME_DIR
    import shutil
    dst = os.path.join(str(P.ascii_work_dir()), "turbo-runtime")
    if not os.path.isdir(dst):
        shutil.copytree(RUNTIME_DIR, dst)
    return dst


def core_object_path(cc_path: str, debug: bool) -> str:
    """Where the compiled runtime for THIS compiler + mode is cached.

    The key includes the compiler path, runtime source hash and debug flag, so a
    new GCC or an updated prabha_core.c automatically triggers a rebuild.
    """
    with open(os.path.join(RUNTIME_DIR, "prabha_core.c"), "rb") as f:
        src_hash = hashlib.sha256(f.read()).hexdigest()[:12]
    key = hashlib.sha256(f"{cc_path}|{debug}|{src_hash}".encode()).hexdigest()[:16]
    folder = os.path.join(str(P.ascii_work_dir()), "turbo-core")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"prabha_core_{key}.o")


def plan(file_path: str, cc: str, cxx: str, debug: bool = False) -> BuildPlan:
    # absolute path: the compiler runs with cwd = the file's folder, so a relative
    # path like "examples/a.c" would be looked up twice ("examples/examples/a.c")
    file_path = os.path.abspath(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    is_cpp = ext != ".c"
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    rt = _ascii_runtime()
    bp = BuildPlan(is_cpp=is_cpp, uses_panel=uses_panel(raw))

    # every build gets its own work folder (two runs never overwrite each other)
    work = tempfile.mkdtemp(prefix="turbo-", dir=str(P.ascii_work_dir()))
    bp.work_dir = work
    bp.binary = os.path.join(work, "program" + P.EXE)

    # 1) runtime object, compiled once and cached
    core = core_object_path(cc, debug)
    if not os.path.isfile(core):
        bp.steps.append((cc, ["-std=c99", "-g" if debug else "-O2", "-I", rt, "-c",
                              os.path.join(rt, "prabha_core.c"), "-o", core],
                         work, "Compiling Turbo C runtime (one time)"))

    # 2) adapted temp copy — the user's file itself is never touched
    code, changed = adapt(raw)
    bp.notes.extend(changed)
    src = file_path
    copy_needed = P.IS_WINDOWS and not file_path.isascii()
    if code != raw or copy_needed:
        name = os.path.basename(file_path) if os.path.basename(file_path).isascii() else "main" + ext
        src = os.path.join(work, name)
        with open(src, "w", encoding="utf-8", newline="") as f:
            f.write(code)
        bp.source_map[os.path.normcase(os.path.abspath(src))] = file_path

    args = ["-std=gnu++14" if is_cpp else "-std=gnu99", "-Wall"]
    args += ["-g", "-O0"] if debug else ["-O2"]
    if is_cpp:
        # Turbo C++: <iostream.h>, cout without std::, old casts → accepted, with warnings
        args += ["-fpermissive", "-I", os.path.join(rt, "compat"),
                 "-include", os.path.join(rt, "compat", "prabha_cpp_prelude.h")]
    if not bp.uses_panel or debug:
        # console program: printf("Enter a: ") must show before scanf waits
        args += ["-include", os.path.join(rt, "prabha_unbuffered.h")]
    if debug and src != file_path and not copy_needed:
        # debug info names the user's folder, so breakpoints match the real file
        args.append(f"-fdebug-prefix-map={work}={os.path.dirname(os.path.abspath(file_path))}")
    # local headers ("myheader.h") still resolve from the student's own folder
    args += ["-I", os.path.dirname(os.path.abspath(file_path)), "-I", rt, src, core, "-o", bp.binary, "-lm"]
    if P.IS_WINDOWS:
        args.append("-static")   # no libgcc/libstdc++ DLL needed on the lab PC
    bp.steps.append((cxx if is_cpp else cc, args, os.path.dirname(os.path.abspath(file_path)),
                     "Compiling (Turbo mode)"))
    return bp


def run_env(base_env=None):
    """Environment for running a Turbo program: protocol on stdout (fd 1).

    Windows has no fd 3 pipe in QProcess, so MEDHĀ always uses stdout and the
    decoder separates `##PRABHA##` lines from printf text.
    """
    env = dict(base_env or os.environ)
    env["PRABHA_PROTO_FD"] = "1"
    return env
