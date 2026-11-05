# Windows release acceptance — 2026-11-05

## Verified 2.0.2 candidate

[Artifact-only run 42031151597](https://github.com/Kanak234/medha-ide/actions/runs/42031151597)
passed on Windows for commit `398809d6203e0e51e2a531b00b7e17372fffcf5c`.
It builds through `packaging/windows/build_msix.ps1` and publishes no GitHub release.
The publishing `windows-msix.yml` workflow was not dispatched.

| Check | Result |
|---|---|
| Windows offline tests and real ConPTY, Python 3.13 | 214 passed, 6 skipped; pyflakes clean |
| Separate Windows Python 3.12 suite | 214 passed, 6 skipped; run 42031151656 |
| Frozen GUI launch from Windows system directory | PASS; Welcome visible and shell command produced MEDHA_SMOKE_OK |
| Frozen bundled GCC compiler selftest | PASS, SUM=5050 |
| Frozen ConPTY dir, continuous ping, Ctrl+C, another dir | PASS; shell survives |
| Frozen C build/run with scanf through terminal | PASS; input 21 produces ANSWER=42 |
| Frozen Turbo C graphics | PASS; real decoded framebuffer and screenshot |
| Same terminal/C/Turbo checks in source GUI | PASS |
| Linux regression | 218 passed, 2 skipped; pyflakes clean; 20 UI smoke tests passed |
| MSIX installation, installed launch, uninstall | Not performed |
| Installed-package terminal/C/Turbo interaction | Not performed; frozen executable was tested before packaging |
| Manual Windows breakpoint, DSA stepping, save/close/reopen | Not performed in this acceptance run |
| Extension install/uninstall | Not performed |

No connected Windows desktop or signing certificate was available. No signing
files or Windows trust/security settings were changed. GitHub Windows GUI tests
are not a claim that the unperformed installed/manual checks passed.

## Packaging fixes proven by the run

B13: pywinpty imports alone omitted its runtime console hosts. Explicit collection
of the companion DLLs and executables, including `winpty/OpenConsole.exe`, fixes
the frozen shell exit. Hidden-console mode did not help and was reverted. The app
remains a windowed executable. Streaming ANSI/OSC filtering removes raw terminal
control sequences from the QTextEdit display; this is not a full VT emulator.

B14: the build now waits for the compiler selftest process and verifies its exit
code and PASS marker. UTF-8 stdout/stderr prevent the MEDHĀ text from raising a
cp1252 encoding error. The GUI smoke now requires live command output, not only
a visible window. Lifecycle evidence shows shell shutdown after checks at close.

## Evidence

- [Frozen results](screenshots/windows-acceptance/frozen-results.json)
- [Source results](screenshots/windows-acceptance/source-results.json)
- [Frozen startup JSON](screenshots/windows-acceptance/frozen-gui.json)
- [Startup terminal text](screenshots/windows-acceptance/frozen-terminal.txt)
- [Artifact archive](https://github.com/Kanak234/medha-ide/actions/runs/42031151597/artifacts/13415918858)
  (`medha-windows-validation`, MSIX plus portable ZIP).

![Frozen Welcome and healthy terminal](screenshots/windows-acceptance/frozen-welcome.png)
![Frozen Turbo graphics](screenshots/windows-acceptance/frozen-turbo.png)

## Store preparation

The live Store package is 2.0.1.0, so this update uses **2.0.2 / 2.0.2.0**.
Partner Center Submission 2 has the WHATS_NEW block from `store/listing.md` and
seven screenshots saved. At report time the new binary has not been uploaded
and certification has not been submitted. The existing draft inherits 2.0.1;
it must be replaced with the validated 2.0.2 MSIX before submission.
