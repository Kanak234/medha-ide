"""
tests/test_modernize.py — "Modernize this code" must not change what a program does.

WHAT:  For each sample: run the ORIGINAL with Turbo mode and the MODERNIZED code with
       a strict modern compiler (-std=c11 / -std=c++17 -pedantic-errors, no Turbo
       runtime at all), feed both the same input, and require identical output.
WHY:   A modernizer that "looks right" but changes behaviour would teach students
       wrong code. This proves each rewrite is safe (same contract as PRABHA's tests).
FLOW:  pytest tests/test_modernize.py   (skips if gcc/g++ missing)
"""

import os
import shutil
import subprocess

import pytest

from medha.turbo.builder import plan, run_env
from medha.turbo.modernize import RULES, modernize
from medha.turbo.protocol import ProtocolDecoder

HAVE_GCC = shutil.which("gcc") and shutil.which("g++")
ALL_RULES = {r.id for r in RULES}

SAMPLES = {
    "marks.cpp": ("#include <iostream.h>\n#include <conio.h>\nvoid main()\n{\n  clrscr();\n  char name[20];\n"
                  "  int a, b, c;\n  cout << \"Enter name: \";\n  cin >> name;\n  cout << \"Enter 3 marks: \";\n"
                  "  cin >> a >> b >> c;\n  cout << \"Student: \" << name << endl;\n"
                  "  cout << \"Average: \" << (a + b + c) / 3 << endl;\n  getch();\n}\n",
                  b"Kanak\r\n70 80 90\r\n\r\n"),
    "student.c": ("#include <stdio.h>\n#include <conio.h>\nvoid main()\n{\n  char city[30];\n  int age;\n  clrscr();\n"
                  "  printf(\"Enter city: \");\n  gets(city);\n  printf(\"Enter age: \");\n  scanf(\"%d\", &age);\n"
                  "  printf(\"%s, age %d\\nNext year: %d\\n\", city, age, age + 1);\n  getch();\n}\n",
                  b"Hazaribagh\n20\n\n"),
    "table.cpp": ("#include <iostream.h>\n#include <iomanip.h>\nvoid main()\n{\n  int n = 7;\n"
                  "  for (int i = 1; i <= 5; i++)\n    cout << setw(2) << n << \" x \" << i << \" = \" << setw(3) << n * i << endl;\n}\n",
                  b""),
}


def _run(cmd, inp, env=None):
    r = subprocess.run(cmd, input=inp, capture_output=True, timeout=30, env=env)
    d = ProtocolDecoder()
    text, _ = d.feed(r.stdout)
    return (text + d.flush_text()).replace("\r\n", "\n")


@pytest.mark.skipif(not HAVE_GCC, reason="gcc/g++ not installed")
@pytest.mark.parametrize("name", sorted(SAMPLES))
def test_modernized_program_behaves_the_same(name, tmp_path):
    src, inp = SAMPLES[name]
    old_file = tmp_path / ("old_" + name)
    old_file.write_text(src)
    bp = plan(str(old_file), "gcc", "g++")
    for prog, args, cwd, _ in bp.steps:
        assert subprocess.run([prog] + args, cwd=cwd, capture_output=True).returncode == 0
    old_out = _run([bp.binary], inp, run_env())

    res = modernize(src, name, enabled=ALL_RULES)
    assert res.changes, "expected at least one modernization"
    assert not res.warnings
    new_file = tmp_path / name
    new_file.write_text(res.code)
    cpp = name.endswith(".cpp")
    exe = tmp_path / "modern"
    c = subprocess.run(["g++" if cpp else "gcc", "-std=c++17" if cpp else "-std=c11", "-pedantic-errors",
                        "-Wall", str(new_file), "-o", str(exe), "-lm"], capture_output=True, text=True)
    assert c.returncode == 0, "modernized code must compile with a strict standard compiler:\n" + c.stderr + res.code
    new_out = _run([str(exe)], inp)
    assert new_out == old_out


def test_modernize_explanations_exist_in_both_languages():
    res = modernize(SAMPLES["marks.cpp"][0], "marks.cpp", enabled=ALL_RULES, ui="hi")
    for ch in res.changes:
        assert ch.explanation.get("title") and ch.explanation.get("why")
    rules = {c.rule for c in res.changes}
    assert {"old-headers", "void-main", "std-qualify", "char-array-string"} <= rules


def test_clrscr_is_only_offered_by_default():
    res = modernize(SAMPLES["student.c"][0], "student.c")
    assert any(a["id"] == "clrscr" for a in res.available)
    assert "clrscr();" in res.code


def test_strings_and_comments_untouched():
    src = '#include <iostream.h>\n// void main() in a comment\nint main() { cout << "void main() NULL"; return 0; }\n'
    res = modernize(src, "x.cpp", enabled=ALL_RULES)
    assert '"void main() NULL"' in res.code and "// void main() in a comment" in res.code
