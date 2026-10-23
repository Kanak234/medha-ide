#!/usr/bin/env python3
"""
MEDHĀ IDE — ADVERSARIAL CHECKPOINT VALIDATOR
============================================

This file is the referee. The agent must RUN it, never EDIT it.

Design principle: every check uses a value generated fresh at runtime that the
agent could not have known when it wrote the code. Hardcoded output, regex
"simulation", and mocked tests all fail automatically — they cannot produce a
number they have never seen.

Usage:
    python3 verify_medha.py            # run all checkpoints
    python3 verify_medha.py --only C4  # run one checkpoint

Exit code 0 = all passed. Anything else = the phase is NOT complete.
"""

import os
import sys
import re
import time
import random
import hashlib
import shutil
import signal
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "medha"
RESULTS = []
SEED = random.randint(10**6, 10**7 - 1)


# ----------------------------------------------------------------- helpers

def report(cid, name, ok, detail=""):
    # ok=True → PASS, ok=False → FAIL, ok=None → SKIP.
    # WHY: a check that could not run (missing wmctrl, no display) must never be
    # counted as a pass — earlier versions printed PASS for a skipped window check,
    # which hid the real launch bug. SKIP is reported separately in the summary.
    RESULTS.append((cid, name, ok))
    mark = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
    print(f"[{mark}] {cid} — {name}")
    for line in str(detail).rstrip().split("\n"):
        if line.strip():
            print(f"       {line}")
    print()
    return ok


def sh(cmd, **kw):
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    kw.setdefault("timeout", 60)
    try:
        return subprocess.run(cmd, **kw)
    except Exception as e:
        class R: returncode, stdout, stderr = -1, "", str(e)
        return R()


# ----------------------------------------------------- C0: honest environment

def c0_environment():
    problems = []

    if os.environ.get("QT_QPA_PLATFORM", "").lower() in ("offscreen", "minimal", "vnc"):
        problems.append(
            f"QT_QPA_PLATFORM={os.environ['QT_QPA_PLATFORM']} — headless mode is not "
            "acceptable evidence. A window that renders nowhere has not opened."
        )

    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        problems.append("No DISPLAY or WAYLAND_DISPLAY — not running on a real session.")

    if not PKG.is_dir():
        problems.append(f"{PKG} does not exist.")

    return report("C0", "Real graphical session, not headless",
                  not problems, "\n".join(problems) or "Real session detected.")


# --------------------------------------------- C1: source is free of fakery

FORBIDDEN = [
    (r"confidence\s*[:=]\s*\d+", "hardcoded confidence constant"),
    (r"['\"]\s*(?:kanak|Kanak)[^'\"]*Lead Architect", "hardcoded whoami response"),
    (r"Linux\s+medha-\w+\s+\d+\.\d+", "hardcoded uname response"),
    (r"['\"]\d+\.\d+\.\d+\s*\(Ubuntu Host\)['\"]", "hardcoded toolchain version"),
    (r"Zero\s+Hallucination", "self-awarded verification badge"),
    (r"matchAll|\.includes\(['\"]for['\"]\)", "regex-based code 'analysis'"),
]

def c1_no_fabrication():
    hits = []
    for path in PKG.rglob("*.py"):
        text = path.read_text(errors="ignore")
        for pattern, label in FORBIDDEN:
            for m in re.finditer(pattern, text):
                line = text[:m.start()].count("\n") + 1
                hits.append(f"{path.relative_to(ROOT)}:{line} — {label}: {m.group(0)[:60]}")
    return report("C1", "No fabricated values in source", not hits,
                  "\n".join(hits) or "Source scan clean.")


# ------------------------------------------------ C2: window really appears

def c2_window_visible():
    env = dict(os.environ)
    env.pop("QT_QPA_PLATFORM", None)

    proc = subprocess.Popen([sys.executable, "-m", "medha"], cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(6)

    if proc.poll() is not None:
        out, err = proc.communicate()
        return report("C2", "Native window appears on screen", False,
                      f"Process exited immediately with code {proc.returncode}\n"
                      f"stdout: {out[-800:]}\nstderr: {err[-800:]}")

    lister = shutil.which("wmctrl") or shutil.which("xdotool")
    detail, ok = "", False

    if lister and "wmctrl" in lister:
        r = sh([lister, "-lp"])
        ok = any(str(proc.pid) in ln for ln in r.stdout.splitlines())
        detail = r.stdout.strip() or "wmctrl returned no windows"
    elif lister:
        r = sh([lister, "search", "--pid", str(proc.pid)])
        ok = bool(r.stdout.strip())
        detail = f"xdotool window ids: {r.stdout.strip() or '(none)'}"
    else:
        ok = None   # cannot be verified automatically → SKIP, not PASS
        detail = ("wmctrl/xdotool not installed — automatic window detection skipped.\n"
                  "MANUAL CHECK REQUIRED: is a MEDHĀ window visible on your screen "
                  "right now? If not, this checkpoint FAILED regardless of this output.\n"
                  "Install with: sudo apt install wmctrl")

    detail += f"\nProcess {proc.pid} alive after 6s: {proc.poll() is None}"
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()

    return report("C2", "Native window appears on screen", ok, detail)


# ------------------------------- C3: runner really compiles (defeats regex)

def c3_real_compilation():
    """
    The C program COMPUTES its answer in a loop at runtime.
    Regex extraction of printf() cannot perform arithmetic, so a simulated
    runner physically cannot produce the right number.
    """
    n = SEED % 900 + 100
    expected = 0
    for i in range(1, n + 1):
        expected = (expected * 31 + i * i) % 1000003

    src = f"""#include <stdio.h>
int main(void) {{
    long acc = 0;
    for (int i = 1; i <= {n}; i++) acc = (acc * 31 + (long)i * i) % 1000003;
    printf("MEDHA_RESULT=%ld\\n", acc);
    return 0;
}}
"""
    work = Path(tempfile.mkdtemp(prefix="medha_verify_"))
    cfile = work / "checksum.c"
    cfile.write_text(src)

    try:
        sys.path.insert(0, str(ROOT))
        os.environ.pop("QT_QPA_PLATFORM", None)
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QEventLoop, QTimer
        from medha.runner import ProcessRunner

        app = QApplication.instance() or QApplication([])
        runner = ProcessRunner()
        captured = {"text": ""}

        for sig in ("output", "stdout_ready", "output_ready"):
            if hasattr(runner, sig):
                getattr(runner, sig).connect(lambda s: captured.__setitem__("text", captured["text"] + str(s)))
                break

        loop = QEventLoop()
        runner.finished.connect(lambda *a: loop.quit())
        QTimer.singleShot(45000, loop.quit)
        runner.run_file(str(cfile))
        loop.exec()

        text = captured["text"] or getattr(runner, "last_output", "") or ""
        m = re.search(r"MEDHA_RESULT=(\d+)", text)
        got = int(m.group(1)) if m else None
        ok = got == expected

        detail = (f"n={n} (generated this run)\n"
                  f"expected={expected}\n"
                  f"got={got}\n"
                  f"runner output: {text[-400:] or '(empty)'}")
        if got is None:
            detail += ("\nNo MEDHA_RESULT found — the runner did not execute the binary, "
                       "or its output is not being captured.")
        elif not ok:
            detail += "\nWrong value — output is not coming from a real compiled binary."
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C3", "Run button invokes a real compiler and real binary", ok, detail)


# ------------------------------ C4: diagnostics parsed from real gcc output

def c4_real_diagnostics():
    """Syntax error is placed at a line number chosen this run."""
    pad = SEED % 12 + 3
    lines = ["#include <stdio.h>", "", "int main(void) {"]
    lines += [f"    int v{i} = {i};" for i in range(pad)]
    err_line = len(lines) + 1
    lines += ['    printf("x")', "    return 0;", "}"]
    src = "\n".join(lines) + "\n"

    work = Path(tempfile.mkdtemp(prefix="medha_diag_"))
    cfile = work / "diag.c"
    cfile.write_text(src)

    try:
        sys.path.insert(0, str(ROOT))
        os.environ.pop("QT_QPA_PLATFORM", None)
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QEventLoop, QTimer
        from medha.runner import ProcessRunner

        app = QApplication.instance() or QApplication([])
        runner = ProcessRunner()
        box = {"diags": []}
        loop = QEventLoop()

        def done(*args):
            for a in args:
                if isinstance(a, (list, tuple)):
                    box["diags"] = list(a)
            loop.quit()

        runner.finished.connect(done)
        QTimer.singleShot(45000, loop.quit)
        runner.run_file(str(cfile))
        loop.exec()

        diags = box["diags"]
        reported = [getattr(d, "line", None) or (d.get("line") if isinstance(d, dict) else None)
                    for d in diags]
        ok = err_line in reported or (err_line + 1) in reported

        detail = (f"error deliberately placed at line {err_line} (chosen this run)\n"
                  f"lines reported by MEDHĀ: {reported or '(none)'}\n"
                  f"diagnostic count: {len(diags)}")
        if not diags:
            detail += "\nNo diagnostics returned — compiler stderr is not being parsed."
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return report("C4", "Compiler errors parsed with correct line numbers", ok, detail)


# ---------------------------------------- C5: terminal runs a real shell

def c5_real_terminal():
    """Echo a token generated this run — no hardcoded response can match it."""
    token = hashlib.sha256(f"{SEED}{time.time()}".encode()).hexdigest()[:16]
    try:
        sys.path.insert(0, str(ROOT))
        os.environ.pop("QT_QPA_PLATFORM", None)
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer, QEventLoop
        from medha.terminal import IntegratedTerminalWidget

        app = QApplication.instance() or QApplication([])
        term = IntegratedTerminalWidget()
        time.sleep(1)

        for meth in ("execute_command", "run_command", "send_command"):
            if hasattr(term, meth):
                getattr(term, meth)(f"echo MEDHA_TERM_{token} && pwd && id -un")
                break
        else:
            return report("C5", "Terminal executes a real shell", False,
                          "No command-execution method found on IntegratedTerminalWidget")

        loop = QEventLoop()
        QTimer.singleShot(6000, loop.quit)
        loop.exec()

        buf = ""
        for attr in ("output_edit", "output", "console"):
            w = getattr(term, attr, None)
            if w is not None and hasattr(w, "toPlainText"):
                buf = w.toPlainText()
                break

        ok = f"MEDHA_TERM_{token}" in buf
        detail = (f"token generated this run: {token}\n"
                  f"found in terminal buffer: {ok}\n"
                  f"buffer tail: {buf[-400:] or '(empty)'}")
        if not ok:
            detail += "\nA hardcoded shell cannot echo a token it has never seen."
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"

    return report("C5", "Terminal executes a real shell", ok, detail)


# ---------------------------------------------------------------- driver

CHECKS = {
    "C0": c0_environment,
    "C1": c1_no_fabrication,
    "C2": c2_window_visible,
    "C3": c3_real_compilation,
    "C4": c4_real_diagnostics,
    "C5": c5_real_terminal,
}

def main():
    print("=" * 62)
    print("MEDHĀ ADVERSARIAL VALIDATOR")
    print(f"validator sha256 : {hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:32]}")
    print(f"run seed         : {SEED}   (different every run — cannot be pre-baked)")
    print("=" * 62 + "\n")

    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].upper()

    for cid, fn in CHECKS.items():
        if only and cid != only:
            continue
        try:
            fn()
        except Exception as e:
            report(cid, fn.__doc__ or cid, False, f"validator crashed: {type(e).__name__}: {e}")

    passed = sum(1 for _, _, ok in RESULTS if ok is True)
    skipped = [c for c, _, ok in RESULTS if ok is None]
    failed = [c for c, _, ok in RESULTS if ok is False]
    total = len(RESULTS)
    print("=" * 62)
    print(f"RESULT: {passed}/{total} checkpoints passed, {len(skipped)} skipped, {len(failed)} failed")
    if skipped:
        print("Skipped (NOT verified): " + ", ".join(skipped))
    if failed:
        print("Failed: " + ", ".join(failed))
        print("The phase is NOT complete. Fix and re-run. Do not advance.")
    print("=" * 62)
    # Exit 0 only when every check really passed; a skip is exit 2 so CI never
    # mistakes "could not check" for "checked and fine".
    sys.exit(1 if failed else (2 if skipped else 0))


if __name__ == "__main__":
    main()
