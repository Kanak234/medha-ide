"""
MEDHĀ IDE — problems.py — Problems panel (compiler errors + how to fix them)

WHAT:  Table of diagnostics from runner.py. v2 adds a "How to fix" column with the
       beginner explanation from explain.py (English / Hinglish) and a tooltip.
WHY:   Double-click jumps to the line (like Dev-C++/C-Lite); the explanation is what
       C-Lite does not have — the raw GCC message alone confuses beginners.
FLOW:  runner.finished → set_diagnostics() → double-click → problem_selected → app jumps
"""
import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

class ProblemsPanelWidget(QWidget):
    problem_selected = Signal(str, int, int) # file_path, line, col

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Severity", "Message", "How to fix", "File", "Line"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setWordWrap(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #090d16;
                color: #c9d1d9;
                border: none;
                gridline-color: #21262d;
            }
            QHeaderView::section {
                background-color: #161b22;
                color: #8b949e;
                padding: 4px;
                border: none;
            }
        """)

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        layout.addWidget(self.table)

    def set_diagnostics(self, diagnostics):
        self.table.setRowCount(0)
        for diag in diagnostics:
            row = self.table.rowCount()
            self.table.insertRow(row)

            item_sev = QTableWidgetItem(diag.severity.upper())
            if diag.severity == 'error':
                item_sev.setForeground(QColor('#f85149'))
            else:
                item_sev.setForeground(QColor('#d29922'))

            item_msg = QTableWidgetItem(diag.message)
            tip = getattr(diag, "tip", None) or ""
            item_tip = QTableWidgetItem(tip)
            item_tip.setForeground(QColor('#7ee787'))
            notes = getattr(diag, "notes", []) or []
            item_msg.setToolTip(diag.message + ("\n" + "\n".join(notes) if notes else "") + ("\n\nFix: " + tip if tip else ""))
            item_tip.setToolTip(tip)
            item_file = QTableWidgetItem(os.path.basename(diag.file_path or ""))
            item_file.setToolTip(diag.file_path or "")
            item_line = QTableWidgetItem(str(diag.line))

            item_msg.setData(Qt.ItemDataRole.UserRole, (diag.file_path, diag.line, diag.col))

            self.table.setItem(row, 0, item_sev)
            self.table.setItem(row, 1, item_msg)
            self.table.setItem(row, 2, item_tip)
            self.table.setItem(row, 3, item_file)
            self.table.setItem(row, 4, item_line)
        self.table.resizeRowsToContents()

    def on_cell_double_clicked(self, row, col):
        item = self.table.item(row, 1)
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                fpath, line, c = data
                self.problem_selected.emit(fpath, line, c)
