# How MEDHĀ 2.0 works (explain-it-yourself guide)

* **platform_info.py** — answers "Windows or Linux? where can I write?". Every path decision lives here.
* **toolchains.py** — finds gcc, g++, gdb, javac, java, python, clangd. Order: your choice in Tools → Toolchains → bundled folder (Store build) → PATH → common folders. A tool counts only if `--version` really runs.
* **settings.py** — `settings.json` in your user folder (C/C++ standard, Turbo mode, Hinglish, tool paths). Saved atomically.
* **runner.py** — the Run button. Plans build steps, runs them with QProcess (UI never freezes), then starts your program. Typed terminal lines go to your program's stdin. Errors → Problems with a fix; crashes → explained.
* **explain.py** — regex rules: compiler message → English/Hinglish tip; exit code → crash reason (segfault, ÷0, stack overflow).
* **turbo/** — Turbo C mode. `adapt.py` fixes `void main`/`far` in a temp copy (line numbers unchanged), `builder.py` compiles PRABHA's `prabha_core.c` once and links your program, `protocol.py` decodes `##PRABHA##` frames, `panel.py` draws the 640×480 screen and sends keys (arrows = 0 + scan code, like Turbo C).
* **turbo/modernize.py** — 13 rules (iostream.h, void main, gets, clrscr, random, delay, NULL, std::…). Each change shows why + a quiz. Tests prove old and new programs print the same output.
* **analyzers/security.py** — CWE rules (gets, strcpy, scanf %s, printf(var), system, eval, SQL +, hard-coded password, `<= N` off-by-one).
* **terminal.py** — real shell: bash on Linux, cmd.exe on Windows.
* **packaging/windows/** — PyInstaller → `MEDHA.exe --selftest` → MSIX (makeappx). Runs on GitHub's Windows machine.
