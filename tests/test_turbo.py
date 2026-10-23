"""
tests/test_turbo.py — Turbo C mode, end to end, with REAL gcc/g++.

WHAT:  1) protocol decoder unit tests (markers mid-line, partial chunks)
       2) adapt() keeps line numbers and never touches strings/comments
       3) every program in examples/turboc/ is compiled with the vendored PRABHA
          runtime, RUN, and its decoded framebuffer is checked pixel by pixel.
WHY:   The old fake MEDHĀ "ran" code with regexes. These tests can only pass if a
       real compiler builds a real binary whose real output draws real pixels.
FLOW:  pytest tests/test_turbo.py   (skips automatically if gcc is not installed)
"""

import os
import shutil
import subprocess
import time

import pytest

from medha.turbo.adapt import adapt, needs_turbo, uses_panel
from medha.turbo.builder import plan, run_env
from medha.turbo.protocol import ProtocolDecoder

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "examples", "turboc")
HAVE_GCC = shutil.which("gcc") and shutil.which("g++")

# colour indices (Borland): 0 BLACK 1 BLUE 2 GREEN 9 LIGHTBLUE 10 LIGHTGREEN 12 LIGHTRED 14 YELLOW 15 WHITE
PIXEL_CHECKS = {
    "03_smiley.c": [((320, 170), 14), ((275, 200), 0)],
    "05_national_flag.c": [((160, 90), 12), ((160, 170), 15), ((160, 250), 2)],
    "16_boundary_fill.c": [((320, 240), 9), ((250, 240), 15)],
    "17_flood_fill.c": [((200, 240), 12), ((320, 240), 10), ((440, 240), 9)],
    "28_star_polygon.c": [((320, 240), 14), ((5, 5), 0)],
    "32_keyboard_move_box.c": [((345, 215), 10), ((305, 255), 0)],   # moved up + right
}
STDIN = {
    "31_turbo_cpp_marks.cpp": b"80\r\n70\r\n90\r\n",
    "32_keyboard_move_box.c": b"\x00H\x00M\x1b",   # Up, Right, Esc (Turbo 0+scan codes)
}
KEEP_OPEN = {"08_bouncing_ball.c": 1.0}   # animation polls kbhit(): send ESC after 1 s


# ------------------------------------------------------------------ decoder
def test_decoder_separates_text_and_messages_mid_line():
    d = ProtocolDecoder()
    text, msgs = d.feed(b'Choice: ##PRABHA##{"t":"input","mode":"getch"}\nafter\n')
    assert text == "Choice: after\n"
    assert msgs == [{"t": "input", "mode": "getch"}]


def test_decoder_handles_split_chunks_and_prompt_without_newline():
    d = ProtocolDecoder()
    t1, m1 = d.feed(b"Enter a: ##PRA")
    assert t1 == "Enter a: " and m1 == []          # prompt shown at once, marker held
    t2, m2 = d.feed(b'BHA##{"t":"sound","hz":440}\n')
    assert t2 == "" and m2[0]["hz"] == 440


def test_decoder_applies_rle_frame():
    import base64
    d = ProtocolDecoder()
    d.feed(b'##PRABHA##{"t":"init","w":4,"h":2}\n')
    rle = base64.b64encode(bytes([4, 14, 4, 2])).decode()       # 4×YELLOW then 4×GREEN
    d.feed(('##PRABHA##{"t":"frame","n":0,"x":0,"y":0,"w":4,"h":2,"full":1,"rle":"%s"}\n' % rle).encode())
    assert d.frames == 1 and d.pixel(0, 0) == 14 and d.pixel(3, 1) == 2


# -------------------------------------------------------------------- adapt
def test_adapt_void_main_keeps_lines_and_strings():
    src = '#include <stdio.h>\nvoid main()\n{\n  printf("void main()");\n  return;\n}\n'
    out, changed = adapt(src)
    assert "int main()" in out and 'printf("void main()")' in out
    assert "return 0;" in out
    assert out.count("\n") == src.count("\n")      # error line numbers stay correct
    assert changed


def test_adapt_far_pointer_removed():
    out, _ = adapt("int main(){ char far *p = 0; return 0; }")
    assert "far" not in out and "char *p" in out


def test_needs_turbo_detection():
    assert needs_turbo("#include <graphics.h>\nint main(){}")
    assert needs_turbo("#include<iostream.h>\nint main(){}")
    assert needs_turbo("void main(){}")
    assert not needs_turbo('#include <stdio.h>\nint main(){ puts("void main()"); }')
    assert uses_panel("#include <conio.h>") and not uses_panel("#include <iostream.h>")


# ----------------------------------------------------------- real programs
ALL = sorted(f for f in os.listdir(EXAMPLES) if f.endswith((".c", ".cpp")))


def test_at_least_thirty_examples():
    assert len(ALL) >= 30


@pytest.mark.skipif(not HAVE_GCC, reason="gcc/g++ not installed")
@pytest.mark.parametrize("name", ALL)
def test_example_compiles_runs_and_draws(name):
    path = os.path.join(EXAMPLES, name)
    bp = plan(path, shutil.which("gcc"), shutil.which("g++"))
    for prog, args, cwd, label in bp.steps:
        r = subprocess.run([prog] + args, cwd=cwd, capture_output=True, text=True)
        assert r.returncode == 0, f"{label} failed:\n{r.stderr}"
    if name in KEEP_OPEN:
        p = subprocess.Popen([bp.binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=run_env())
        time.sleep(KEEP_OPEN[name])
        out, _ = p.communicate(b"\x1b\x1b", timeout=30)
        code = p.returncode
    else:
        r = subprocess.run([bp.binary], input=STDIN.get(name, b""), capture_output=True,
                           env=run_env(), timeout=30)
        out, code = r.stdout, r.returncode
    d = ProtocolDecoder()
    text, _ = d.feed(out)
    text += d.flush_text()
    assert code == 0, f"exit code {code}"
    assert d.frames >= 1, "no frame was drawn"
    used = [i for i, c in enumerate(d.colour_histogram()) if c]
    if name.endswith(".cpp"):
        assert "Total = 240" in text and "Average = 80" in text
    else:
        assert len(used) >= 2, f"only colours {used} — nothing was drawn"
    for (x, y), colour in PIXEL_CHECKS.get(name, []):
        assert d.pixel(x, y) == colour, f"pixel ({x},{y}) = {d.pixel(x, y)}, expected {colour}"
    if name in KEEP_OPEN:
        assert d.frames > 5, "animation should produce many frames before ESC"
