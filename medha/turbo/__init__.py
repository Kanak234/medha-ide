"""
MEDHĀ IDE — Turbo C mode (graphics.h / conio.h / dos.h / iostream.h).

WHAT:  Everything MEDHĀ needs so old college Turbo C / Turbo C++ programs run on a
       modern 64-bit GCC, on Windows AND Linux, without the student changing code.
WHY:   This is C-Lite IDE's home ground (it is Windows-only). MEDHĀ reuses the
       runtime from Kanak's own PRABHA project so the behaviour is identical.
PARTS: lexer.py     — "masked" view of C source (comments/strings blanked)
       adapt.py     — temp-copy fixes (void main → int main, far/near) — same lines
       builder.py   — compiles runtime once + the student program with the right flags
       protocol.py  — decodes the ##PRABHA## frame stream into a framebuffer
       panel.py     — the Qt window that shows the 640×480 screen and sends keys
       modernize.py — "Modernize this code": Turbo → standard C/C++ with explanations
FLOW:  runner.py sees graphics.h/conio.h → builder.build() → run → protocol → panel
"""
