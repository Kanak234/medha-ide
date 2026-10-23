"""
MEDHĀ IDE — turbo/lexer.py  (Python port of PRABHA lib/modern/lexer.js)
=======================================================================

WHAT:  Builds a "masked" copy of C/C++ source: comments, string literals and
       char literals are replaced by spaces of the SAME length (newlines kept).
       Preprocessor lines (#include ...) are listed separately.
WHY:   Every Turbo rule is a regex. Without masking, `printf("void main()")` or
       `// use gets()` would be "fixed" too — a real bug PRABHA 5.x had. Same
       length means an offset in the masked text is the same offset in the real
       source, so edits can be applied to the original.
USED BY: adapt.py (Turbo mode temp copy) and modernize.py (Modernize panel).
FLOW:  lex(src) → Lexed(masked, strings, preproc) → rules search `masked`,
       then edit `src` at the same offsets.
"""

import re
from dataclasses import dataclass, field


@dataclass
class Span:
    start: int
    end: int
    kind: str = ""
    text: str = ""


@dataclass
class Lexed:
    masked: str
    strings: list = field(default_factory=list)   # Span(kind="string"|"char"|"raw")
    preproc: list = field(default_factory=list)   # Span(text="#include <x>")


def lex(src: str) -> Lexed:
    out = list(src)
    strings, preproc = [], []
    n = len(src)

    def blank(a, b):
        # replace characters with spaces but keep line breaks → line numbers unchanged
        for k in range(a, min(b, n)):
            if out[k] not in "\r\n":
                out[k] = " "

    i = 0
    line_start = True
    while i < n:
        c = src[i]
        d = src[i + 1] if i + 1 < n else ""
        if c == "\n":
            line_start = True
            i += 1
            continue
        if line_start and c in " \t":
            i += 1
            continue
        # preprocessor line — may continue with backslash-newline
        if line_start and c == "#":
            j = i
            while j < n and src[j] != "\n":
                if src[j] == "\\" and j + 1 < n and src[j + 1] == "\n":
                    j += 1
                j += 1
            preproc.append(Span(i, j, "pre", src[i:j]))
            seg = src[i:j]
            m = re.search(r"//|/\*", seg)
            if m:
                blank(i + m.start(), j)   # comment at the end of an #include line
            i = j
            line_start = False
            continue
        line_start = False
        if c == "/" and d == "/":
            j = i + 2
            while j < n and src[j] != "\n":
                j += 1
            blank(i, j)
            i = j
            continue
        if c == "/" and d == "*":
            j = src.find("*/", i + 2)
            j = n if j == -1 else j + 2
            blank(i, j)
            i = j
            continue
        # C++11 raw string R"delim( ... )delim"
        if c == "R" and d == '"' and not (i > 0 and re.match(r"[\w$]", src[i - 1])):
            m = re.match(r'R"([^(\s]{0,16})\(', src[i:i + 20])
            if m:
                close = ")" + m.group(1) + '"'
                j = src.find(close, i + len(m.group(0)))
                j = n if j == -1 else j + len(close)
                strings.append(Span(i + 1, j, "raw"))
                blank(i + 2, j - 1)
                i = j
                continue
        if c == '"':
            j = i + 1
            while j < n and src[j] != '"' and src[j] != "\n":
                if src[j] == "\\":
                    j += 1
                j += 1
            j = min(n, j + 1)
            strings.append(Span(i, j, "string"))
            blank(i + 1, j - 1)
            i = j
            continue
        if c == "'":
            # C++14 digit separator 1'000'000 is not a char literal
            prev = src[i - 1] if i > 0 else ""
            if re.match(r"[0-9A-Fa-f]", prev) and re.match(r"[0-9A-Fa-f]", d or ""):
                i += 1
                continue
            j = i + 1
            while j < n and src[j] != "'" and src[j] != "\n":
                if src[j] == "\\":
                    j += 1
                j += 1
            j = min(n, j + 1)
            strings.append(Span(i, j, "char"))
            blank(i + 1, j - 1)
            i = j
            continue
        i += 1
    return Lexed("".join(out), strings, preproc)


PAIRS = {"(": ")", "{": "}", "[": "]"}


def match_bracket(masked: str, open_at: int) -> int:
    """Index of the bracket that closes masked[open_at], or -1."""
    if open_at < 0 or open_at >= len(masked):
        return -1
    o = masked[open_at]
    cl = PAIRS.get(o)
    if not cl:
        return -1
    depth = 0
    for k in range(open_at, len(masked)):
        ch = masked[k]
        if ch == o:
            depth += 1
        elif ch == cl:
            depth -= 1
            if depth == 0:
                return k
    return -1


def line_start(s, off):
    while off > 0 and s[off - 1] != "\n":
        off -= 1
    return off


def line_end(s, off):
    while off < len(s) and s[off] != "\n":
        off += 1
    return off


def line_of(s, off):
    return s.count("\n", 0, max(0, off)) + 1


def delete_statement(src, start, end):
    """Remove a whole line if it holds only this statement, else just the statement."""
    ls, le = line_start(src, start), line_end(src, max(start, end - 1))
    if src[ls:start].strip() == "" and src[end:le].strip() == "":
        return (ls, min(len(src), le + 1), "")
    return (start, end, "")
