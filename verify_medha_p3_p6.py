#!/usr/bin/env python3
"""
MEDHĀ IDE — ADVERSARIAL VALIDATOR, PHASES P3–P6
===============================================

Same referee rules as verify_medha.py: every check uses a value generated
fresh at run time, so hardcoded output and mocked behaviour cannot pass.

This file is also the API CONTRACT. The classes and method names it imports
are the ones you must build. Do not rename them to match whatever you wrote —
write what this file expects.

    medha/lsp.py
        class LspClient(language: str, root: str)
            start() -> None
            definition(file: str, line: int, col: int) -> (file, line, col) | None
            completions(file: str, line: int, col: int) -> list[str]
            shutdown() -> None
        (line/col are 1-based, as shown to the user)

    medha/debugger.py
        class DebugSession(target: str, kind: str)      # kind: "gdb" | "debugpy"
            start() -> None
            set_breakpoint(file: str, line: int) -> bool
            run() -> None
            wait_for_stop(timeout: float = 30) -> bool
            evaluate(expr: str) -> str
            continue_() -> None
            terminate() -> None

    medha/git_backend.py
        class GitBackend(repo_path: str)
            init() -> None
            status() -> list                # any iterable of changed paths
            stage(paths: list[str]) -> None
            commit(message: str) -> str     # returns commit sha
            log(n: int = 10) -> list        # newest first; str or objects w/ .message
            diff(path: str) -> str

    medha/build.py
        class BuildSystem(project_dir: str)
            detect() -> str | None          # "cmake" | "make" | None
            configure() -> tuple[int, str]  # (exit_code, output)
            build() -> tuple[int, str, str] # (exit_code, output, artifact_path)

Usage:
    python3 verify_medha_p3_p6.py
    python3 verify_medha_p3_p6.py --only C8

Exit code 0 = all passed.
"""

import os
import sys
import re
import time
import random
import shutil
import hashlib
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.pop("QT_QPA_PLATFORM", None)

RESULTS = []
SEED = random.randint(10**6, 10**7 - 1)
TAG = hashlib.sha256(f"{SEED}{time.time()}".encode()).hexdigest()[:8]


def report(cid, name, ok, detail=""):
    RESULTS.append((cid, name, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {cid} — {name}")
    for line in str(detail).rstrip().split("\n"):
        if line.strip():
            print(f"       {line}")
    print()
    return ok


def have(binary):
    return shutil.which(binary) is not None


def tmpdir(prefix):
    return Path(tempfile.mkdtemp(prefix=f"medha_{prefix}_"))


# ============================================================ P3 — LSP

def c6_lsp_definition():
    """clangd resolves a function name that did not exist until this run."""
    if not have("clangd"):
        return report("C6", "LSP go-to-definition (clangd)", False,
                      "clangd not installed. Install: sudo apt install -y clangd")

    fn = f"compute_{TAG}"
    work = tmpdir("lsp")
    src = work / "prog.c"
    body = [
        "#include <stdio.h>",
        "",
        f"int {fn}(int x) {{",          # definition line = 3
        "    return x * 2 + 1;",
        "}",
        "",
        "int main(void) {",
        f"    printf(\"%d\\n\", {fn}(21));",   # call site line = 8
        "    return 0;",
        "}",
        "",
    ]
    src.write_text("\n".join(body))
    def_line, call_line = 3, 8
    call_col = body[call_line - 1].index(fn) + 1

    try:
        from medha.lsp import LspClient
        client = LspClient("c", str(work))
        client.start()
        time.sleep(3)
        result = client.definition(str(src), call_line, call_col)
        client.shutdown()

        got_line = None
        if result:
            got_line = result[1] if isinstance(result, (list, tuple)) else getattr(result, "line", None)
        ok = got_line == def_line
        detail = (f"symbol generated this run : {fn}\n"
                  f"call site                 : line {call_line}, col {call_col}\n"
                  f"definition expected at    : line {def_line}\n"
                  f"LspClient returned        : {result}")
        if not result:
            detail += "\nNo definition returned — clangd is not actually being queried."
    except ImportError as e:
        ok, detail = False, f"medha/lsp.py missing or LspClient not defined: {e}"
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C6", "LSP go-to-definition (clangd)", ok, detail)


def c7_lsp_completion():
    """Completion must offer a symbol invented this run."""
    if not have("pylsp") and not have("pylsp-server"):
        return report("C7", "LSP completion (pylsp)", False,
                      "pylsp not installed. Install: "
                      "python3 -m pip install python-lsp-server --break-system-packages")

    sym = f"velocity_{TAG}"
    work = tmpdir("lspc")
    src = work / "mod.py"
    lines = [
        f"{sym} = 42",
        "",
        "def main():",
        "    print(vel",     # line 4 — completion requested at end
        "",
    ]
    src.write_text("\n".join(lines))
    req_line, req_col = 4, len(lines[3]) + 1

    try:
        from medha.lsp import LspClient
        client = LspClient("python", str(work))
        client.start()
        time.sleep(3)
        items = client.completions(str(src), req_line, req_col) or []
        client.shutdown()

        flat = " ".join(str(i) for i in items)
        ok = sym in flat
        detail = (f"symbol generated this run : {sym}\n"
                  f"completion items returned : {len(items)}\n"
                  f"sample                    : {str(items[:12])[:300]}")
        if not items:
            detail += "\nEmpty list — pylsp is not actually being queried."
    except ImportError as e:
        ok, detail = False, f"medha/lsp.py missing or LspClient not defined: {e}"
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C7", "LSP completion (pylsp)", ok, detail)


# ======================================================= P4 — DEBUGGER

def c8_gdb_breakpoint():
    """Stop at a breakpoint and read a variable computed at run time."""
    if not have("gdb"):
        return report("C8", "GDB breakpoint and variable inspection", False,
                      "gdb not installed. Install: sudo apt install -y gdb")

    n = SEED % 400 + 60
    expected = 0
    for i in range(1, n + 1):
        expected = (expected * 7 + i) % 100003

    work = tmpdir("gdb")
    src = work / "dbg.c"
    src.write_text(
        "#include <stdio.h>\n"
        "int main(void) {\n"
        "    long acc = 0;\n"
        f"    for (int i = 1; i <= {n}; i++) acc = (acc * 7 + i) % 100003;\n"
        "    printf(\"done %ld\\n\", acc);\n"     # breakpoint here = line 5
        "    return 0;\n"
        "}\n"
    )
    binary = work / "dbg"
    r = subprocess.run(["gcc", "-g", "-O0", str(src), "-o", str(binary)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        shutil.rmtree(work, ignore_errors=True)
        return report("C8", "GDB breakpoint and variable inspection", False,
                      f"validator could not build the fixture: {r.stderr}")

    try:
        from medha.debugger import DebugSession
        s = DebugSession(str(binary), kind="gdb")
        s.start()
        placed = s.set_breakpoint(str(src), 5)
        s.run()
        stopped = s.wait_for_stop(timeout=30)
        value = s.evaluate("acc") if stopped else None
        s.terminate()

        got = None
        if value is not None:
            m = re.search(r"(-?\d+)", str(value))
            got = int(m.group(1)) if m else None
        ok = got == expected
        detail = (f"loop bound generated this run : {n}\n"
                  f"breakpoint placed             : {placed}\n"
                  f"stopped at breakpoint         : {stopped}\n"
                  f"expected acc                  : {expected}\n"
                  f"evaluate('acc') returned      : {value!r} -> {got}")
        if not stopped:
            detail += "\nNever stopped — gdb is not actually controlling the process."
    except ImportError as e:
        ok, detail = False, f"medha/debugger.py missing or DebugSession not defined: {e}"
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C8", "GDB breakpoint and variable inspection", ok, detail)


def c9_debugpy_breakpoint():
    """Same for Python via debugpy."""
    try:
        import debugpy  # noqa: F401
    except ImportError:
        return report("C9", "Python breakpoint and variable inspection", False,
                      "debugpy not installed. Install: "
                      "python3 -m pip install debugpy --break-system-packages")

    n = SEED % 300 + 40
    expected = sum(i * i for i in range(1, n + 1)) % 99991

    work = tmpdir("dbgpy")
    src = work / "dbg.py"
    src.write_text(
        "def main():\n"
        "    total = 0\n"
        f"    for i in range(1, {n} + 1):\n"
        "        total = (total + i * i) % 99991\n"
        "    print('done', total)\n"     # breakpoint = line 5
        "\n"
        "main()\n"
    )

    try:
        from medha.debugger import DebugSession
        s = DebugSession(str(src), kind="debugpy")
        s.start()
        placed = s.set_breakpoint(str(src), 5)
        s.run()
        stopped = s.wait_for_stop(timeout=30)
        value = s.evaluate("total") if stopped else None
        s.terminate()

        got = None
        if value is not None:
            m = re.search(r"(-?\d+)", str(value))
            got = int(m.group(1)) if m else None
        ok = got == expected
        detail = (f"loop bound generated this run : {n}\n"
                  f"breakpoint placed             : {placed}\n"
                  f"stopped at breakpoint         : {stopped}\n"
                  f"expected total                : {expected}\n"
                  f"evaluate('total') returned    : {value!r} -> {got}")
    except ImportError as e:
        ok, detail = False, f"medha/debugger.py missing or DebugSession not defined: {e}"
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C9", "Python breakpoint and variable inspection", ok, detail)


# =========================================================== P5 — GIT

def c10_git_commit():
    """Commit through MEDHĀ, then verify with the real git binary."""
    if not have("git"):
        return report("C10", "Git stage and commit", False, "git not installed")

    work = tmpdir("git")
    marker = f"marker_{TAG}"
    msg = f"MEDHA commit {TAG}"
    (work / "note.txt").write_text(f"{marker}\n")

    try:
        from medha.git_backend import GitBackend
        g = GitBackend(str(work))
        g.init()
        subprocess.run(["git", "config", "user.email", "medha@local"], cwd=work,
                       capture_output=True)
        subprocess.run(["git", "config", "user.name", "MEDHA"], cwd=work,
                       capture_output=True)

        status_before = list(g.status() or [])
        g.stage(["note.txt"])
        sha = g.commit(msg)

        real_log = subprocess.run(["git", "log", "--oneline", "-n", "5"],
                                  cwd=work, capture_output=True, text=True).stdout
        real_show = subprocess.run(["git", "show", "--stat", "--format=%s", "-n", "1"],
                                   cwd=work, capture_output=True, text=True).stdout

        ok = TAG in real_log and TAG in real_show
        detail = (f"marker generated this run : {marker}\n"
                  f"status() before staging   : {status_before}\n"
                  f"commit() returned sha     : {sha}\n"
                  f"real `git log --oneline`  : {real_log.strip() or '(empty)'}")
        if not ok:
            detail += "\nThe real git repository has no such commit — nothing was actually committed."
    except ImportError as e:
        ok, detail = False, f"medha/git_backend.py missing or GitBackend not defined: {e}"
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C10", "Git stage and commit", ok, detail)


# ================================================= P6 — BUILD SYSTEMS

def c11_cmake_build():
    """Build a CMake project whose target name and output are generated now."""
    if not have("cmake"):
        return report("C11", "CMake configure and build", False,
                      "cmake not installed. Install: sudo apt install -y cmake")

    target = f"app_{TAG}"
    n = SEED % 500 + 50
    expected = 0
    for i in range(1, n + 1):
        expected = (expected * 13 + i) % 999983

    work = tmpdir("cmake")
    (work / "main.c").write_text(
        "#include <stdio.h>\n"
        "int main(void) {\n"
        "    long acc = 0;\n"
        f"    for (int i = 1; i <= {n}; i++) acc = (acc * 13 + i) % 999983;\n"
        "    printf(\"BUILD_RESULT=%ld\\n\", acc);\n"
        "    return 0;\n"
        "}\n"
    )
    (work / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.16)\n"
        f"project({target} C)\n"
        f"add_executable({target} main.c)\n"
    )

    try:
        from medha.build import BuildSystem
        bs = BuildSystem(str(work))
        kind = bs.detect()
        cfg_code, cfg_out = bs.configure()
        code, out, artifact = bs.build()

        run_out = ""
        if artifact and Path(artifact).exists():
            run_out = subprocess.run([str(artifact)], capture_output=True,
                                     text=True, timeout=30).stdout

        m = re.search(r"BUILD_RESULT=(\d+)", run_out)
        got = int(m.group(1)) if m else None
        ok = kind == "cmake" and code == 0 and got == expected

        detail = (f"target generated this run : {target}\n"
                  f"detect()                  : {kind}\n"
                  f"configure() exit          : {cfg_code}\n"
                  f"build() exit              : {code}\n"
                  f"artifact                  : {artifact}\n"
                  f"expected                  : {expected}\n"
                  f"got                       : {got}\n"
                  f"build output tail         : {str(out)[-300:]}")
    except ImportError as e:
        ok, detail = False, f"medha/build.py missing or BuildSystem not defined: {e}"
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C11", "CMake configure and build", ok, detail)


# ========================================================== C12 — hygiene

FORBIDDEN = [
    (r"confidence\s*[:=]\s*\d+", "hardcoded confidence constant"),
    (r"QT_QPA_PLATFORM['\"]?\s*\]?\s*=\s*['\"]offscreen", "headless mode forced in source"),
    (r"MEDHA_VERIFY|VERIFY_MODE|IS_TEST_RUN", "branching on the referee"),
    (r"['\"]\d+\.\d+\.\d+\s*\(Ubuntu Host\)['\"]", "hardcoded toolchain version"),
]

def c12_no_fabrication():
    hits = []
    for path in (ROOT / "medha").rglob("*.py"):
        text = path.read_text(errors="ignore")
        for pattern, label in FORBIDDEN:
            for m in re.finditer(pattern, text):
                line = text[:m.start()].count("\n") + 1
                hits.append(f"{path.relative_to(ROOT)}:{line} — {label}")
    return report("C12", "No fabrication or referee-detection in source", not hits,
                  "\n".join(hits) or "Source scan clean.")


CHECKS = {
    "C6": c6_lsp_definition,
    "C7": c7_lsp_completion,
    "C8": c8_gdb_breakpoint,
    "C9": c9_debugpy_breakpoint,
    "C10": c10_git_commit,
    "C11": c11_cmake_build,
    "C12": c12_no_fabrication,
}

PHASE_OF = {"C6": "P3", "C7": "P3", "C8": "P4", "C9": "P4",
            "C10": "P5", "C11": "P6", "C12": "all"}


def main():
    print("=" * 64)
    print("MEDHĀ ADVERSARIAL VALIDATOR — P3 to P6")
    print(f"validator sha256 : {hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:32]}")
    print(f"run seed         : {SEED}")
    print(f"run tag          : {TAG}   (symbols and markers derive from this)")
    print("=" * 64 + "\n")

    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].upper()

    for cid, fn in CHECKS.items():
        if only and cid != only:
            continue
        try:
            fn()
        except Exception as e:
            report(cid, cid, False, f"validator crashed: {type(e).__name__}: {e}")

    passed = sum(1 for _, _, ok in RESULTS if ok)
    total = len(RESULTS)
    print("=" * 64)
    print(f"RESULT: {passed}/{total} checkpoints passed")
    if passed < total:
        failed = [c for c, _, ok in RESULTS if not ok]
        print("Failed: " + ", ".join(f"{c} ({PHASE_OF[c]})" for c in failed))
        print("Those phases are NOT complete. Fix and re-run. Do not advance.")
    print("=" * 64)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
