"""
MEDHĀ IDE — turbo/adapt.py  (Python port of PRABHA lib/modern/turbo-adapt.js)
=============================================================================

WHAT:  Turbo mode fixes applied to a TEMP COPY of the student's file before
       compiling: `void main()` / bare `main()` → `int main()` (+ `return;` →
       `return 0;` inside it), and Turbo C `far`/`near`/`huge` pointer words removed.
WHY:   College lab code is written for Turbo C. GCC rejects `void main` (C++) and
       does not know `far`. C-Lite asks students to accept compiler errors; MEDHĀ
       runs the code as written. The student's own file is NEVER modified, and the
       number of lines never changes, so compiler error line numbers still point
       at the student's real lines.
USED BY: turbo/builder.py (and runner.py for console C++ with iostream.h).
FLOW:  adapt(src) → (new_src, ["void main() adapted to int main()", ...])
"""

import re

from medha.turbo.lexer import lex, match_bracket


def _returns_in_body(masked, body_open, edits):
    """Inside main's body turn every bare `return;` into `return 0;`."""
    body_close = match_bracket(masked, body_open)
    if body_close < 0:
        return
    for r in re.finditer(r"\breturn\s*;", masked[body_open:body_close]):
        s = body_open + r.start()
        edits.append((s, s + len(r.group(0)), "return 0;"))


def adapt(src: str):
    lx = lex(src)
    masked = lx.masked
    edits, changed = [], []

    # 1) void main( → int main(   — only in real code (masked), never inside strings
    for m in re.finditer(r"\bvoid(\s+)main(\s*)\(", masked):
        edits.append((m.start(), m.end(), "int" + m.group(1) + "main" + m.group(2) + "("))
        close = match_bracket(masked, m.end() - 1)
        k = close + 1
        while 0 < k < len(masked) and masked[k].isspace():
            k += 1
        if close > 0 and k < len(masked) and masked[k] == "{":
            _returns_in_body(masked, k, edits)

    # 2) old "implicit int" main() at line start → int main()   (clang rejects it)
    for m in re.finditer(r"(^|[;}])([ \t]*)main(\s*)\(", masked, re.M):
        at = m.start() + len(m.group(1)) + len(m.group(2))
        open_at = masked.find("(", at)
        close = match_bracket(masked, open_at)
        k = close + 1
        while 0 < k < len(masked) and masked[k].isspace():
            k += 1
        if close < 0 or k >= len(masked) or masked[k] != "{":
            continue   # a call or a prototype, not the definition
        edits.append((at, at, "int "))
        _returns_in_body(masked, k, edits)

    if edits:
        changed.append("void main() adapted to int main()")

    # 3) far / near / huge pointer qualifiers (only when followed by '*')
    fn = 0
    for m in re.finditer(r"\b(far|near|huge|_far|_near|_huge)\b\s*(?=\*)", masked):
        edits.append((m.start(), m.end(), ""))
        fn += 1
    if fn:
        changed.append("far/near/huge pointer qualifiers removed")

    out = src
    for s, e, t in sorted(set(edits), key=lambda x: x[0], reverse=True):
        out = out[:s] + t + out[e:]
    return out, changed


INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([\w./]+)[>"]', re.M)


def uses_panel(src: str) -> bool:
    """graphics.h / conio.h programs need the 640×480 PRABHA screen."""
    return bool(re.search(r'^\s*#\s*include\s*[<"](graphics|conio)\.h[>"]', src, re.M))


def needs_turbo(src: str) -> bool:
    """True when the program needs the Turbo runtime or the Turbo C++ shims.

    graphics.h / conio.h / dos.h → runtime; iostream.h / fstream.h / iomanip.h → shims;
    `void main` → adapt. Plain modern programs are compiled exactly as written.
    """
    heads = {h.lower() for h in INCLUDE_RE.findall(src)}
    turbo_heads = {"graphics.h", "conio.h", "dos.h", "iostream.h", "fstream.h",
                   "iomanip.h", "strstream.h", "constream.h", "process.h"}
    if heads & turbo_heads:
        return True
    return bool(re.search(r"\bvoid\s+main\s*\(", lex(src).masked))
