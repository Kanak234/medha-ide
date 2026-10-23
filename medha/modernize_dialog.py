"""
MEDHĀ IDE — modernize_dialog.py — Tools → Modernize this code (Turbo → standard)
=================================================================================

WHAT:  Side-by-side window: left = the student's Turbo C/C++ code, right = the
       modern C11 / C++17 version, below = one card per change (before → after,
       why, common mistake, a quiz question) in English or Hinglish. Buttons:
       open the modern code in a new tab, or replace the editor text (undoable).
WHY:   Teaches *why* `void main`, `iostream.h`, `gets()` and `clrscr()` are gone,
       instead of silently fixing them. Engine: turbo/modernize.py.
USED BY: app.py (Tools menu, Ctrl+Alt+M).
FLOW:  open(src) → modernize() → views; "Open as new tab" → app.create_untitled_tab()
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel, QPlainTextEdit,
                               QPushButton, QSplitter, QTextBrowser, QVBoxLayout)

from medha.turbo.modernize import RULES, default_enabled, modernize


class ModernizeDialog(QDialog):
    def __init__(self, source, file_name, ui="en", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Modernize — {file_name or 'code'}")
        self.resize(1200, 760)
        self.source, self.file_name, self.ui = source, file_name, ui
        self.result_code = None   # set when the user accepts

        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.chk_review = QCheckBox("Also apply 'review' changes (e.g. remove clrscr())")
        self.chk_review.toggled.connect(self.recompute)
        top.addWidget(self.chk_review)
        top.addStretch(1)
        self.lbl = QLabel("")
        top.addWidget(self.lbl)
        lay.addLayout(top)

        mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        split = QSplitter(Qt.Orientation.Horizontal)
        self.old = QPlainTextEdit(source)
        self.old.setReadOnly(True)
        self.old.setFont(mono)
        self.new = QPlainTextEdit()
        self.new.setReadOnly(True)
        self.new.setFont(mono)
        split.addWidget(self.old)
        split.addWidget(self.new)
        vsplit = QSplitter(Qt.Orientation.Vertical)
        vsplit.addWidget(split)
        self.cards = QTextBrowser()
        vsplit.addWidget(self.cards)
        vsplit.setSizes([440, 260])
        lay.addWidget(vsplit, 1)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_tab = QPushButton("Open modern code in a new tab")
        self.btn_tab.clicked.connect(lambda: self._done("tab"))
        self.btn_replace = QPushButton("Replace editor text (Ctrl+Z undoes)")
        self.btn_replace.clicked.connect(lambda: self._done("replace"))
        close = QPushButton("Close")
        close.clicked.connect(self.reject)
        for b in (self.btn_tab, self.btn_replace, close):
            btns.addWidget(b)
        lay.addLayout(btns)
        self.mode = None
        self.recompute()

    def recompute(self):
        enabled = default_enabled()
        if self.chk_review.isChecked():
            enabled = {r.id for r in RULES}
        res = modernize(self.source, self.file_name, enabled=enabled, ui=self.ui)
        self.res = res
        self.new.setPlainText(res.code)
        self.lbl.setText(f"{len(res.changes)} change(s) · target {res.target}")
        html = []
        if not res.changes and not res.available:
            html.append("<p>This code already looks modern — nothing to change.</p>")
        for ch in res.changes:
            ex = ch.explanation or {}
            html.append(f"<h3>Line {ch.line}: {ex.get('title', ch.rule)}</h3>"
                        f"<pre style='background:#2d1414'>{_esc(ch.before)}</pre>"
                        f"<pre style='background:#12261a'>{_esc(ch.after)}</pre>"
                        f"<p>{_esc(ex.get('why', ''))}</p><p><i>{_esc(ex.get('mistake', ''))}</i></p>")
            q = ex.get("practice") or {}
            if q.get("q"):
                opts = "".join(f"<li>{_esc(o)}</li>" for o in q.get("options", []))
                html.append(f"<p><b>Quiz:</b> {_esc(q['q'])}</p><ol>{opts}</ol>"
                            f"<p><small>Answer: option {int(q.get('answer', 0)) + 1} — {_esc(q.get('explain', ''))}</small></p>")
        for a in res.available:
            html.append(f"<p>⚠ <b>{_esc(a.get('title') or a['id'])}</b> — {a['count']} place(s); "
                        f"tick the box above to apply (needs a quick review).</p>")
        for w in res.warnings:
            html.append(f"<p>Skipped for safety: {_esc(w)}</p>")
        self.cards.setHtml("".join(html))
        changed = res.code != self.source
        self.btn_tab.setEnabled(changed)
        self.btn_replace.setEnabled(changed)

    def _done(self, mode):
        self.mode = mode
        self.result_code = self.res.code
        self.accept()


def _esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("`", ""))
