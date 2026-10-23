# Turbo C runtime (graphics.h · conio.h · dos.h)

These files are **vendored from Kanak Prabhakar's own PRABHA project**
(github.com/Kanak234/prabha, MIT License, commit `7b77e26`, PRABHA 6.1.1).
MEDHĀ and PRABHA share one runtime so a program behaves the same in both.

* `prabha_core.c` — the whole Turbo C "machine": a 640×480, 16-colour,
  4-page framebuffer. It streams frames as `##PRABHA##{json}` lines on stdout.
  MEDHĀ's `medha/turbo/protocol.py` decodes them and `medha/turbo/panel.py` draws them.
* `graphics.h`, `conio.h`, `dos.h` — the Borland API headers students include.
* `compat/` — `iostream.h`, `fstream.h`, … shims so Turbo C++ code compiles
  on a modern g++ (Turbo mode only).
* `font8x8_basic.h` — public-domain 8×8 bitmap font (Daniel Hepper / Marcel Sondaar).
* `prabha_unbuffered.h` — makes stdout unbuffered so `printf("Enter a: ")` shows
  before `scanf` waits.

To update: copy `runtime/` from a newer PRABHA release and run
`python -m pytest tests/test_turbo.py`.
