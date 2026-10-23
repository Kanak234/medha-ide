"""
MEDHĀ IDE — analyzers/security.py — beginner security scan (PyraSec rules for code)
====================================================================================

WHAT:  Rule-based, offline scanner for the student's own C, C++, Java and Python
       code: gets/strcpy buffer overflows, format-string bugs, command injection,
       SQL built by string concatenation, eval/pickle, hard-coded passwords, and
       the classic `i <= N` off-by-one on an array of size N. Each finding has a
       CWE id, a severity, and a plain explanation + fix (English / Hinglish).
WHY:   Kanak's PyraSec scans projects (secrets, IaC, containers, dependencies);
       a first-year student needs the same idea on the program they just typed.
       C-Lite has nothing like this. Rules run on the *masked* source (comments and
       strings blanked by turbo/lexer.py), so `// never use gets()` is not flagged.
USED BY: app.py (Analyze → Security Scan, bottom tab "Security"), tests/test_security.py.
FLOW:  scan_file(path) → [Finding] → SecurityPanel.set_findings() → double-click → line
"""

import os
import re
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QHeaderView, QLabel, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from medha.turbo.lexer import lex


@dataclass
class Finding:
    file_path: str
    line: int
    severity: str      # "critical" | "high" | "medium" | "low"
    cwe: str
    title: str
    why: str
    fix: str


def _line(src, off):
    return src.count("\n", 0, off) + 1


# (id, languages, regex on MASKED code, severity, CWE, title, why_en, fix_en, why_hi, fix_hi)
CODE_RULES = [
    ("gets", ("c", "cpp"), r"\bgets\s*\(", "critical", "CWE-242",
     "gets() can overflow the buffer",
     "gets() does not know how big your array is — typing more characters writes past its end (removed from C11).",
     "Use fgets(buf, sizeof buf, stdin) in C or std::getline / cin.getline in C++.",
     "gets() ko array ka size pata nahi — zyada type karne par memory ke bahar likhta hai (C11 se hata diya gaya).",
     "C mein fgets(buf, sizeof buf, stdin), C++ mein std::getline ya cin.getline use karo."),
    ("strcpy", ("c", "cpp"), r"\b(strcpy|strcat|sprintf|vsprintf)\s*\(", "high", "CWE-120",
     "Unbounded copy into a fixed buffer",
     "strcpy/strcat/sprintf copy until the end of the source, even when the destination is smaller.",
     "Use snprintf(buf, sizeof buf, ...) or strncpy/strncat with the buffer size (and terminate with '\\0').",
     "strcpy/strcat/sprintf source khatam hone tak copy karte hain, chahe destination chhota ho.",
     "snprintf(buf, sizeof buf, ...) ya size ke saath strncpy/strncat use karo (aur '\\0' lagao)."),
    ("scanf-s", ("c", "cpp"), None, "high", "CWE-120",
     "scanf(\"%s\") without a width",
     "%s reads a whole word of any length into your array.",
     "Give a width one less than the array size: char name[20]; scanf(\"%19s\", name);",
     "%s kitna bhi lamba word array mein padh leta hai.",
     "Array size se ek kam width do: char name[20]; scanf(\"%19s\", name);"),
    ("format", ("c", "cpp"), r"\b(?:printf\s*\(|fprintf\s*\(\s*\w+\s*,)\s*[A-Za-z_]\w*\s*\)", "high", "CWE-134",
     "Format string is a variable",
     "printf(name) treats % signs inside the user's text as format commands — it can print or even overwrite memory.",
     "Always pass a literal format: printf(\"%s\", name);",
     "printf(name) user ke text ke % ko format command samajhta hai — memory padh ya badal sakta hai.",
     "Hamesha literal format do: printf(\"%s\", name);"),
    ("system", ("c", "cpp"), r"\b(system|popen)\s*\(", "medium", "CWE-78",
     "Runs a shell command",
     "If any part of the command comes from user input, the user can run any command on the PC.",
     "Avoid system(); if needed, never build the command from user input.",
     "Command ka koi hissa user input se aaya to user PC par koi bhi command chala sakta hai.",
     "system() se bacho; zaroori ho to command user input se mat banao."),
    ("py-eval", ("py",), r"\b(eval|exec)\s*\(", "high", "CWE-95",
     "eval()/exec() runs text as code",
     "If the text comes from input(), the user can run any Python code.",
     "Use int()/float() to convert input, or ast.literal_eval for literals.",
     "Text input() se aaya to user koi bhi Python code chala sakta hai.",
     "Input convert karne ke liye int()/float(), ya literals ke liye ast.literal_eval use karo."),
    ("py-shell", ("py",), r"\bos\.system\s*\(|shell\s*=\s*True", "medium", "CWE-78",
     "Command run through the shell",
     "Building a shell command with user data allows command injection.",
     "Use subprocess.run([...]) with a list of arguments and shell=False.",
     "User data se shell command banana command injection ka rasta hai.",
     "subprocess.run([...]) arguments ki list ke saath, shell=False rakho."),
    ("py-pickle", ("py",), r"\bpickle\.loads?\s*\(|\byaml\.load\s*\((?![^)]*Loader)", "high", "CWE-502",
     "Unsafe deserialization",
     "pickle.load / yaml.load on untrusted data can execute code.",
     "Use json, or yaml.safe_load.",
     "Untrusted data par pickle.load / yaml.load code chala sakta hai.",
     "json ya yaml.safe_load use karo."),
    ("java-exec", ("java",), r"Runtime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\s*\(", "medium", "CWE-78",
     "Runtime.exec runs an OS command",
     "If user input is part of the command, the user controls what runs.",
     "Use ProcessBuilder with separate arguments and never concatenate user input.",
     "User input command ka hissa ho to user decide karta hai kya chalega.",
     "Alag arguments ke saath ProcessBuilder use karo, user input mat jodo."),
]

SQL_RE = re.compile(r'"\s*(SELECT|INSERT|UPDATE|DELETE)\b[^"]*"\s*\+', re.I)
SECRET_RE = re.compile(r'\b(password|passwd|pwd|secret|api_?key|token)\w*\s*(?:\[\s*\d*\s*\])?\s*[:=]\s*(?:new\s+String\s*\()?\s*["\'][^"\'\s]{3,}["\']', re.I)
SCANF_RE = re.compile(r'\bscanf\s*\(\s*"([^"]*)"')
ARRAY_DECL_RE = re.compile(r"\b(?:int|char|float|double|long)\s+([A-Za-z_]\w*)\s*\[\s*(\d+|[A-Z_][A-Z0-9_]*)\s*\]")
LOOP_RE = re.compile(r"\bfor\s*\([^;]*;\s*([A-Za-z_]\w*)\s*<=\s*(\d+|[A-Z_][A-Z0-9_]*)\s*;")


def lang_of(path):
    ext = os.path.splitext(path)[1].lower()
    return {".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp",
            ".py": "py", ".java": "java"}.get(ext)


def _mask_python(src):
    """Blank comments and string *contents* in Python (keeps offsets, newlines, quotes).

    Quotes stay so a rule can tell "string in real code" (quote kept) from
    "text inside a comment" (blanked) — same convention as turbo/lexer.py for C.
    """
    out = list(src)
    for m in re.finditer(r'#[^\n]*|"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'', src):
        keep_edges = not m.group(0).startswith("#")
        for k in range(m.start(), m.end()):
            if out[k] != "\n" and not (keep_edges and k in (m.start(), m.end() - 1)):
                out[k] = " "
    return "".join(out)


def scan_source(src, file_path="<code>", ui="en"):
    lang = lang_of(file_path)
    if not lang:
        return []
    masked = _mask_python(src) if lang == "py" else lex(src).masked
    findings = []

    def add(off, sev, cwe, title, why, fix):
        findings.append(Finding(file_path, _line(src, off), sev, cwe, title, why, fix))

    for rid, langs, rx, sev, cwe, title, why, fix, why_hi, fix_hi in CODE_RULES:
        if lang not in langs:
            continue
        w, f = (why_hi, fix_hi) if ui == "hi" else (why, fix)
        if rid == "scanf-s":
            # look at the real string literal (masked hides it) at each scanf( in code
            for m in re.finditer(r"\bscanf\s*\(", masked):
                lit = SCANF_RE.match(src, m.start())
                if lit and re.search(r"%s", lit.group(1)):
                    add(m.start(), sev, cwe, title, w, f)
            continue
        for m in re.finditer(rx, masked):
            add(m.start(), sev, cwe, title, w, f)

    # SQL by concatenation and hard-coded secrets need the real strings → original source
    for m in SQL_RE.finditer(src):
        if masked[m.start()] == '"':   # the string is real code (a comment would be blanked)
            add(m.start(), "high", "CWE-89", "SQL query built with +",
                "Joining user input into SQL lets a user change the query (SQL injection)."
                if ui != "hi" else "User input ko SQL mein jodne se user query badal sakta hai (SQL injection).",
                "Use parameterized queries: cursor.execute(\"... WHERE id = ?\", (uid,)) / PreparedStatement."
                if ui != "hi" else "Parameterized query use karo: cursor.execute(\"... WHERE id = ?\", (uid,)) / PreparedStatement.")
    for m in SECRET_RE.finditer(src):
        if masked[m.start()] != " ":     # the variable name is real code, not inside a comment
            add(m.start(), "medium", "CWE-798", "Hard-coded password / secret",
                "Anyone who reads the code or the compiled program sees this secret."
                if ui != "hi" else "Code ya compiled program padhne wala har koi ye secret dekh sakta hai.",
                "Read it from an environment variable or a config file kept out of Git."
                if ui != "hi" else "Environment variable ya Git ke bahar rakhi config file se padho.")

    # off-by-one: int a[10]; for (i = 0; i <= 10; i++)
    if lang in ("c", "cpp"):
        sizes = {m.group(2) for m in ARRAY_DECL_RE.finditer(masked)}
        for m in LOOP_RE.finditer(masked):
            if m.group(2) in sizes:
                add(m.start(), "medium", "CWE-193", f"Loop goes to <= {m.group(2)} on an array of size {m.group(2)}",
                    "Valid indexes are 0..N-1; index N is outside the array."
                    if ui != "hi" else "Valid index 0..N-1 hote hain; index N array ke bahar hai.",
                    f"Use `< {m.group(2)}` instead of `<= {m.group(2)}`.")
    findings.sort(key=lambda x: (x.line, x.cwe))
    return findings


def scan_file(path, ui="en"):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError:
        return []
    return scan_source(src, path, ui)


SEV_COLOUR = {"critical": "#ff7b72", "high": "#f85149", "medium": "#d29922", "low": "#8b949e"}


class SecurityPanel(QWidget):
    """Bottom tab: table of findings + explanation of the selected one."""

    finding_selected = Signal(str, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.summary = QLabel("Analyze → Security Scan checks the current file (offline, rule-based).")
        self.summary.setStyleSheet("color:#8b949e; padding:4px;")
        lay.addWidget(self.summary)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Severity", "CWE", "Problem", "Line"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellDoubleClicked.connect(self._open)
        self.table.currentCellChanged.connect(lambda r, *_: self._detail(r))
        lay.addWidget(self.table, 1)
        self.detail = QLabel("")
        self.detail.setWordWrap(True)
        self.detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.detail.setStyleSheet("color:#c9d1d9; padding:6px; background:#161b22;")
        lay.addWidget(self.detail)
        self.findings = []

    def set_findings(self, findings, file_name=""):
        self.findings = findings
        self.table.setRowCount(0)
        for f in findings:
            r = self.table.rowCount()
            self.table.insertRow(r)
            sev = QTableWidgetItem(f.severity.upper())
            sev.setForeground(QColor(SEV_COLOUR.get(f.severity, "#c9d1d9")))
            self.table.setItem(r, 0, sev)
            self.table.setItem(r, 1, QTableWidgetItem(f.cwe))
            item = QTableWidgetItem(f.title)
            item.setToolTip(f"{f.why}\nFix: {f.fix}")
            self.table.setItem(r, 2, item)
            self.table.setItem(r, 3, QTableWidgetItem(str(f.line)))
        name = os.path.basename(file_name) if file_name else "file"
        self.summary.setText(f"{len(findings)} security finding(s) in {name}" if findings
                             else f"No security findings in {name} — nice.")
        self.detail.setText("")

    def _detail(self, row):
        if 0 <= row < len(self.findings):
            f = self.findings[row]
            self.detail.setText(f"<b>{f.cwe} · {f.title}</b> (line {f.line})<br>{f.why}<br><b>Fix:</b> {f.fix}")

    def _open(self, row, _col):
        if 0 <= row < len(self.findings):
            f = self.findings[row]
            self.finding_selected.emit(f.file_path, f.line, 1)
