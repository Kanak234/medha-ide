"""
MEDHĀ IDE — turbo/modernize.py — "Modernize this code" (Turbo C/C++ → standard)
================================================================================

WHAT:  Rewrites old Turbo C / Turbo C++ code into standard C11 / C++17 and returns
       every change with a student-level explanation (why, common mistake, a quiz
       question) in English or Hinglish. Python port of Kanak's PRABHA
       lib/modern/{engine,rules}.js (the Punarnava-style engine); explanations are
       loaded from modernize_explanations.json (exported from PRABHA's explain.js).
WHY:   Turbo mode RUNS old code; Modernize TEACHES the modern way. C-Lite only
       compiles Turbo code — it never shows the student what today's C++ looks like.
SAFETY: "If in doubt, do not change". Each rule works on the masked source
       (comments/strings untouched), overlapping edits skip the rule, and any
       result with unbalanced brackets is rejected. `review` rules (clrscr) are
       only offered, never applied by default.
USED BY: modernize_dialog.py (side-by-side view), tests/test_modernize.py.
FLOW:  modernize(src, file_name) → Result(code, changes[], available[], warnings[], lang)
"""

import difflib
import json
import os
import re
from dataclasses import dataclass, field

from medha.turbo.lexer import (delete_statement, lex, line_end, line_of,
                               line_start, match_bracket)

CONIO_FNS = ["clrscr", "getch", "getche", "kbhit", "gotoxy", "textcolor", "textbackground", "cprintf",
             "cputs", "cgets", "cscanf", "putch", "clreol", "delline", "insline", "wherex", "wherey",
             "window", "textattr", "textmode", "highvideo", "lowvideo", "normvideo", "_setcursortype",
             "gettext", "puttext"]
DOS_FNS = ["delay", "sound", "nosound", "getdate", "gettime", "setdate", "settime", "int86", "sleep"]
STD_NAMES = ["cout", "cin", "cerr", "clog", "endl", "ends", "flush", "setw", "setprecision", "setfill",
             "fixed", "scientific", "showpoint", "left", "right", "ifstream", "ofstream", "fstream",
             "ios", "istream", "ostream"]

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "modernize_explanations.json"),
          encoding="utf-8") as _f:
    EXPLAIN = json.load(_f)


def explain(rule_id, ui="en"):
    entry = EXPLAIN.get(rule_id)
    return entry.get("hi" if ui == "hi" else "en") if entry else None


# ------------------------------------------------------------------ helpers
def find_main(masked):
    """Header + body offsets of the top-level main() definition (not a call/prototype)."""
    for m in re.finditer(r"(^|[\s;}])((?:void|int)\s+)?main\s*\(", masked):
        name_at = m.start() + len(m.group(1)) + len(m.group(2) or "")
        open_at = masked.find("(", name_at)
        close = match_bracket(masked, open_at)
        if close < 0:
            continue
        k = close + 1
        while k < len(masked) and masked[k].isspace():
            k += 1
        if k >= len(masked) or masked[k] != "{":
            continue
        body_close = match_bracket(masked, k)
        if body_close < 0:
            continue
        return {"type_start": m.start() + len(m.group(1)), "type": (m.group(2) or "").strip(),
                "name_at": name_at, "body_open": k, "body_close": body_close}
    return None


def uses(masked, name):
    """Offsets of `name` as a free identifier (not .name, ->name or ::name)."""
    out = []
    for m in re.finditer(r"\b" + re.escape(name) + r"\b", masked):
        before = masked[max(0, m.start() - 2):m.start()]
        if re.search(r"(\.|->|::)$", before):
            continue
        out.append(m.start())
    return out


def has_include(src, header):
    return re.search(r'^\s*#\s*include\s*[<"]' + re.escape(header) + r'[>"]', src, re.M) is not None


def include_edit(src, header):
    """Insert `#include <header>` after the last #include (or at the top)."""
    if has_include(src, header):
        return None
    allm = list(re.finditer(r"^[ \t]*#[ \t]*include[^\n]*\n?", src, re.M))
    if allm:
        last = allm[-1]
        nl = "" if last.group(0).endswith("\n") else "\n"
        return (last.end(), last.end(), nl + "#include <" + header + ">\n")
    return (0, 0, "#include <" + header + ">\n")


def statement_at(masked, at):
    s = at
    while s > 0 and masked[s - 1] not in ";{}":
        s -= 1
    e, depth = at, 0
    while e < len(masked):
        c = masked[e]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == ";" and depth <= 0:
            e += 1
            break
        e += 1
    return s, e


def _after_control(masked, start):
    """True if the statement is the single body of `if (...)`, `for`, `while` or `else`."""
    prev = masked[:start].rstrip()
    if re.search(r"\)\s*$", prev) and re.search(r"\b(if|for|while)\s*\([^;{}]*\)$", prev[-200:]):
        return True
    return bool(re.search(r"\belse$", prev))


# -------------------------------------------------------------------- rules
def r_old_headers(ctx):
    return [(m.start(), m.end(), m.group(1) + "<" + m.group(3) + ">")
            for m in re.finditer(r'^([ \t]*#[ \t]*include[ \t]*)([<"])(iostream|fstream|iomanip)\.h([>"])',
                                 ctx["src"], re.M)]


def r_std_qualify(ctx):
    masked, pre = ctx["masked"], ctx["preproc"]
    if re.search(r"\busing\s+namespace\s+std\s*;", masked):
        return []
    in_pre = lambda off: any(p.start <= off < p.end for p in pre)
    edits = []
    for name in STD_NAMES:
        # the student declared a variable with this name (e.g. `int left;`) → leave it
        if re.search(r"\b(?:int|char|float|double|long|short|bool|auto|void|unsigned|signed|const)\s+(?:\*\s*)?"
                     + name + r"\b", masked):
            continue
        for at in uses(masked, name):
            if in_pre(at) or masked[max(0, at - 5):at].endswith("std::"):
                continue
            edits.append((at, at, "std::"))
    return edits


def r_void_main(ctx):
    masked, lang = ctx["masked"], ctx["lang"]
    m = find_main(masked)
    if not m or m["type"] == "int":
        return []
    edits = [(m["type_start"], m["name_at"], "int ")]
    if lang == "c":
        open_at = masked.find("(", m["name_at"])
        close = match_bracket(masked, open_at)
        if close > open_at and masked[open_at + 1:close].strip() == "":
            edits.append((open_at, close + 1, "(void)"))
    body = masked[m["body_open"]:m["body_close"]]
    for r in re.finditer(r"\breturn\s*;", body):
        at = m["body_open"] + r.start()
        pre = masked[m["body_open"]:at]
        if re.search(r"\[[^\]]*\]\s*\([^)]*\)\s*\{[^}]*$", pre):
            continue   # bare return inside a lambda belongs to the lambda
        edits.append((at, at + len(r.group(0)), "return 0;"))
    return edits


def r_getch_hold(ctx):
    src, masked, lang = ctx["src"], ctx["masked"], ctx["lang"]
    m = find_main(masked)
    if not m:
        return []
    body = masked[m["body_open"] + 1:m["body_close"]]
    stmts, depth, s = [], 0, 0
    for i, c in enumerate(body):
        if c in "{(":
            depth += 1
        elif c in "})":
            depth -= 1
            if depth == 0 and c == "}":
                stmts.append((s, i + 1))
                s = i + 1
        elif c == ";" and depth == 0:
            stmts.append((s, i + 1))
            s = i + 1
    txt = lambda st: body[st[0]:st[1]].strip()
    k = len(stmts) - 1
    if k >= 0 and re.match(r"^return\b", txt(stmts[k])):
        k -= 1
    if k < 0 or not re.match(r"^getche?\s*\(\s*\)\s*;$", txt(stmts[k])):
        return []
    st = stmts[k]
    lead = len(body[st[0]:st[1]]) - len(body[st[0]:st[1]].lstrip())
    start, end = m["body_open"] + 1 + st[0] + lead, m["body_open"] + 1 + st[1]
    edits = [(start, end, "std::cin.get();" if lang == "cpp" else "getchar();")]
    inc = include_edit(src, "iostream" if lang == "cpp" else "stdio.h")
    if inc:
        edits.append(inc)
    return edits


def r_clrscr(ctx):
    src, masked = ctx["src"], ctx["masked"]
    edits = []
    for m in re.finditer(r"\bclrscr\s*\(\s*\)\s*;", masked):
        s, e = statement_at(masked, m.start())
        if re.sub(r"\s+", "", masked[s:e]) != "clrscr();" or _after_control(masked, s):
            continue
        edits.append(delete_statement(src, m.start(), e))
    return edits


def r_gets(ctx):
    src, masked, lang = ctx["src"], ctx["masked"], ctx["lang"]
    edits = []
    for m in re.finditer(r"\bgets\s*\(\s*([A-Za-z_]\w*)\s*\)\s*;", masked):
        v = m.group(1)
        if not re.search(r"\bchar\s+" + v + r"\s*\[\s*[\w\s+*]+\]", masked):
            continue   # only real arrays — sizeof of a pointer would be wrong
        s, e = statement_at(masked, m.start())
        if re.sub(r"\s+", "", masked[s:e]) != f"gets({v});" or _after_control(masked, s):
            continue
        if lang == "cpp":
            new = f"std::cin.getline({v}, sizeof {v});"
        else:
            new = f"fgets({v}, sizeof {v}, stdin); {v}[strcspn({v}, \"\\n\")] = '\\0';"
        edits.append((m.start(), m.end(), new))
    if edits:
        for h in (["iostream"] if lang == "cpp" else ["stdio.h", "string.h"]):
            inc = include_edit(src, h)
            if inc:
                edits.append(inc)
    return edits


def r_char_array_string(ctx):
    src, masked = ctx["src"], ctx["masked"]
    edits = []
    for m in re.finditer(r"\bchar\s+([A-Za-z_]\w*)\s*\[\s*\d+\s*\]\s*;", masked):
        v = m.group(1)
        decl_at = m.start() + m.group(0).index(v)
        alls = [a for a in uses(masked, v) if a != decl_at]
        if not alls:
            continue
        ok_all, saw_in = True, False
        for at in alls:
            before = masked[:at].rstrip()
            after = masked[at + len(v):].lstrip()
            s, e = statement_at(masked, at)
            if before.endswith(">>"):
                saw_in = True
                if not re.match(r"^\s*(std::)?cin\b", masked[s:e]):
                    ok_all = False
            elif before.endswith("<<"):
                if not re.match(r"^\s*(std::)?(cout|cerr)\b", masked[s:e]):
                    ok_all = False
            else:
                ok_all = False
            if after.startswith("["):
                ok_all = False   # name[0] — character access, keep the array
            if not ok_all:
                break
        if ok_all and saw_in:
            edits.append((m.start(), m.end(), f"std::string {v};"))
    if edits:
        inc = include_edit(src, "string")
        if inc:
            edits.append(inc)
    return edits


def r_random(ctx):
    src, masked, cpp = ctx["src"], ctx["masked"], ctx["lang"] == "cpp"
    edits = []
    for m in re.finditer(r"\brandomize\s*\(\s*\)", masked):
        edits.append((m.start(), m.end(), "std::srand(static_cast<unsigned>(std::time(nullptr)))" if cpp
                      else "srand((unsigned)time(NULL))"))
    for m in re.finditer(r"\brandom\s*\(", masked):
        if re.search(r"(\.|->|::)$", masked[max(0, m.start() - 2):m.start()]):
            continue
        open_at = m.end() - 1
        close = match_bracket(masked, open_at)
        if close < 0:
            continue
        arg = src[open_at + 1:close].strip()
        if not arg:
            continue   # POSIX random() with no argument — not Turbo's random(n)
        edits.append((m.start(), close + 1, ("(std::rand() % (" if cpp else "(rand() % (") + arg + "))"))
    if edits:
        for h in (["cstdlib", "ctime"] if cpp else ["stdlib.h", "time.h"]):
            inc = include_edit(src, h)
            if inc:
                edits.append(inc)
    return edits


def r_delay(ctx):
    src, masked = ctx["src"], ctx["masked"]
    if ctx["graphics"]:
        return []   # graphics.h: the runtime's delay() also flushes frames — keep it
    edits = []
    for m in re.finditer(r"\bdelay\s*\(", masked):
        if re.search(r"(\.|->|::)$", masked[max(0, m.start() - 2):m.start()]):
            continue
        open_at = m.end() - 1
        close = match_bracket(masked, open_at)
        if close < 0:
            continue
        arg = src[open_at + 1:close].strip()
        edits.append((m.start(), close + 1, f"std::this_thread::sleep_for(std::chrono::milliseconds({arg}))"))
    if edits:
        for h in ["thread", "chrono"]:
            inc = include_edit(src, h)
            if inc:
                edits.append(inc)
    return edits


def r_null(ctx):
    pre = ctx["preproc"]
    return [(m.start(), m.start() + 4, "nullptr") for m in re.finditer(r"\bNULL\b", ctx["masked"])
            if not any(p.start <= m.start() < p.end for p in pre)]


def r_far_near(ctx):
    return [(m.start(), m.end(), "") for m in
            re.finditer(r"\b(far|near|huge|_far|_near|_huge)\b(\s*)(?=\*)", ctx["masked"])]


def r_conio_include(ctx):
    if any(re.search(r"\b" + f + r"\s*\(", ctx["masked"]) for f in CONIO_FNS):
        return []
    m = re.search(r'^[ \t]*#[ \t]*include[ \t]*[<"]conio\.h[>"][^\n]*\n?', ctx["src"], re.M)
    return [(m.start(), m.end(), "")] if m else []


def r_dos_include(ctx):
    masked = ctx["masked"]
    if any(re.search(r"\b" + f + r"\s*\(", masked) for f in DOS_FNS) or re.search(r"\bstruct\s+(date|time)\b", masked):
        return []
    m = re.search(r'^[ \t]*#[ \t]*include[ \t]*[<"]dos\.h[>"][^\n]*\n?', ctx["src"], re.M)
    return [(m.start(), m.end(), "")] if m else []


@dataclass
class Rule:
    id: str
    lang: tuple
    safety: str   # "safe" = applied by default, "review" = only offered
    run: object


# ORDER matters (same as PRABHA): gets before char-array, std-qualify last of the
# naming rules, include removal at the very end.
RULES = [
    Rule("old-headers", ("cpp",), "safe", r_old_headers),
    Rule("void-main", ("c", "cpp"), "safe", r_void_main),
    Rule("far-near", ("c", "cpp"), "safe", r_far_near),
    Rule("gets", ("c", "cpp"), "safe", r_gets),
    Rule("getch-hold", ("c", "cpp"), "safe", r_getch_hold),
    Rule("clrscr", ("c", "cpp"), "review", r_clrscr),
    Rule("random", ("c", "cpp"), "safe", r_random),
    Rule("delay", ("cpp",), "safe", r_delay),
    Rule("char-array-string", ("cpp",), "safe", r_char_array_string),
    Rule("null", ("cpp",), "safe", r_null),
    Rule("std-qualify", ("cpp",), "safe", r_std_qualify),
    Rule("conio-include", ("c", "cpp"), "safe", r_conio_include),
    Rule("dos-include", ("c", "cpp"), "safe", r_dos_include),
]


def default_enabled():
    return {r.id for r in RULES if r.safety == "safe"}


def detect_lang(src, file_name=None):
    if file_name:
        if re.search(r"\.c$", file_name, re.I):
            return "c"
        if re.search(r"\.(cpp|cc|cxx|c\+\+|hpp)$", file_name, re.I):
            return "cpp"
    return "cpp" if re.search(r"\b(cout|cin|iostream|namespace|class|template)\b", src) else "c"


@dataclass
class Change:
    rule: str
    line: int
    before: str
    after: str
    safety: str
    explanation: dict


@dataclass
class Result:
    code: str
    changes: list = field(default_factory=list)
    available: list = field(default_factory=list)   # review rules that would apply
    warnings: list = field(default_factory=list)
    lang: str = "c"
    target: str = "C11"


def _apply(src, edits):
    out = src
    for s, e, t in sorted(edits, key=lambda x: x[0], reverse=True):
        out = out[:s] + t + out[e:]
    return out


def balanced(src):
    lx = lex(src)
    m = list(lx.masked)
    for p in lx.preproc:
        for k in range(p.start, p.end):
            m[k] = " "
    a = b = c = 0
    for ch in m:
        a += (ch == "{") - (ch == "}")
        b += (ch == "(") - (ch == ")")
        c += (ch == "[") - (ch == "]")
        if a < 0 or b < 0 or c < 0:
            return False
    return a == b == c == 0


def _group(src, edits):
    """Edits on neighbouring lines become one before/after card."""
    groups = []
    for e in edits:
        ls, le = line_start(src, e[0]), line_end(src, max(e[0], e[1] - 1))
        if groups and line_of(src, ls) - line_of(src, groups[-1]["le"]) <= 1:
            groups[-1]["le"] = max(groups[-1]["le"], le)
            groups[-1]["edits"].append(e)
        else:
            groups.append({"start": e[0], "ls": ls, "le": le, "edits": [e]})
    out = []
    for g in groups:
        before = src[g["ls"]:g["le"]]
        rel = [(s - g["ls"], min(e - g["ls"], len(before)), t) for s, e, t in g["edits"]]
        after = _apply(before, rel)
        out.append((g["start"], before.rstrip(), after.rstrip()))
    return out


def modernize(source, file_name=None, enabled=None, ui="en"):
    crlf = "\r\n" in source
    src = source.replace("\r\n", "\n")
    lang = detect_lang(src, file_name)
    enabled = set(enabled) if enabled is not None else default_enabled()
    res = Result(code=src, lang=lang, target="C++17" if lang == "cpp" else "C11")
    for rule in RULES:
        if lang not in rule.lang:
            continue
        lx = lex(src)
        ctx = {"src": src, "masked": lx.masked, "preproc": lx.preproc, "lang": lang,
               "graphics": has_include(src, "graphics.h")}
        try:
            edits = rule.run(ctx) or []
        except Exception as e:   # a rule bug must never lose the student's code
            res.warnings.append(f"{rule.id}: {e}")
            continue
        if not edits:
            continue
        if rule.id not in enabled:
            ex = explain(rule.id, ui) or {}
            res.available.append({"id": rule.id, "count": len(edits), "safety": rule.safety, "title": ex.get("title")})
            continue
        edits = sorted(set(edits), key=lambda x: (x[0], x[1]))
        if any(edits[i][0] < edits[i - 1][1] for i in range(1, len(edits))):
            res.warnings.append(f"{rule.id}: overlapping edits — skipped")
            continue
        nxt = _apply(src, edits)
        if not balanced(nxt):
            res.warnings.append(f"{rule.id}: unbalanced result — skipped")
            continue
        for start, before, after in _group(src, edits):
            res.changes.append(Change(rule.id, line_of(src, start), before, after, rule.safety,
                                      explain(rule.id, ui) or {}))
        src = nxt
    if res.changes:
        src = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", src)
    res.code = src.replace("\n", "\r\n") if crlf else src
    return res


def unified_diff(old, new, name="code"):
    return "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                        fromfile=f"{name} (Turbo)", tofile=f"{name} (Modern)"))
