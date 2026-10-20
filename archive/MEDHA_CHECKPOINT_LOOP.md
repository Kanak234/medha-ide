# MEDHĀ IDE — SELF-VALIDATING CHECKPOINT LOOP

**Give this to Antigravity together with `verify_medha.py`.**
Place `verify_medha.py` in the project root, next to the `medha/` package.

---

## THE RULE

You do not decide whether a checkpoint passed. **`verify_medha.py` decides.**

Your own tests, your own reasoning, and your own confidence are not evidence.
The only evidence is the exit code of:

```bash
python3 verify_medha.py
```

Exit code `0` = passed. Anything else = not passed.

---

## THE LOOP

Run this loop. Do not exit it, do not ask me anything, do not report until it terminates.

```
loop:
    run:  python3 verify_medha.py
    if exit code == 0:
        the phase is complete -> stop and report
    else:
        read the FAIL block and its detail lines
        fix the actual cause in medha/
        goto loop
```

**Iteration limit: 15.** If you are still failing after 15 iterations, stop and report
which checkpoint is stuck, what you tried, and what you think the real blocker is.
Do not keep looping silently.

---

## WHAT YOU MAY NOT DO

These are the only hard prohibitions, and they exist because every one of them
has already happened in this project:

1. **Do not edit, move, rename, wrap, or regenerate `verify_medha.py`.**
   Its sha256 is printed at the top of every run. If it changes, every result
   after that point is void.

2. **Do not set `QT_QPA_PLATFORM=offscreen`** — not in the code, not in the
   environment, not in a test harness, not "temporarily." A window rendered to
   nowhere has not opened. Checkpoint C0 fails immediately if you do this.

3. **Do not special-case the validator.** No branching on `MEDHA_VERIFY`, no
   detecting the test seed, no checking whether the caller is a test. If code
   behaves differently under the validator than under a real user, it is a lie
   with extra steps.

4. **Do not weaken a checkpoint to make it pass.** If C3 fails, fix the runner.
   Do not make the runner print what C3 expects.

5. **Do not report a checkpoint as passing without pasting the validator's
   actual stdout**, including the `run seed` line.

---

## WHY YOU CANNOT SHORTCUT THIS

You should understand the mechanism, because it will save you from wasting
iterations trying:

- **C3** compiles a C program that computes a checksum **in a loop at runtime**.
  The value of `n` is generated fresh on every run. Extracting `printf()`
  arguments with a regex cannot perform arithmetic, so a simulated runner
  cannot produce the right number. Only a real `gcc` and a real executed binary
  can pass C3.

- **C4** places a syntax error at a line number chosen at run time. You cannot
  hardcode "line 5."

- **C5** echoes a SHA-256 token generated at run time. A hardcoded shell cannot
  echo a string it has never seen.

- **C1** greps `medha/` for the exact fabrication patterns found in the previous
  build: hardcoded confidence constants, canned `whoami`/`uname` responses,
  static toolchain version strings, regex-based "complexity analysis."

There is no path through these checks except building the real thing.

---

## TODAY'S SCOPE — READ THIS BEFORE PLANNING

The demo is **today**. Scope accordingly.

**In scope today:**
- Get `verify_medha.py` to exit 0 on all six checkpoints (C0–C5)
- Fix the duplicated `$ $` prompt in the terminal panel
- Window title, application icon, a clean dark theme
- Menu actions reachable from the GUI: Open Folder, Save (`Ctrl+S`), Run (`Ctrl+F5`), toggle panels
- Problems panel double-click jumps to the correct line **from the GUI**, not only from a script

**Out of scope today — do not start these:**
- LSP / autocompletion (P3)
- GDB debugging (P4)
- Git integration (P5)
- Build systems (P6)
- AI assistant (P7)
- `.deb` / AppImage packaging (P8)

A small IDE where every visible thing is real beats a large one where anything
is not. Do not add a panel today that you cannot make real today.

---

## REPORT FORMAT

When the loop terminates, report exactly this:

```
### Validator output (verbatim, including the seed line)
<paste>

### Iterations used
<n> of 15

### What was actually broken, per checkpoint
<cause, not symptom — "the runner never connected finished to the diagnostics
list" not "C4 was failing">

### What I changed
<files and functions>

### What is still not real
<mandatory — every panel or menu item that is visible but not functional.
An empty section means you did not look.>
```

Begin the loop now.
