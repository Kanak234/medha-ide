"""
MEDHĀ IDE — toolchains_dialog.py — Tools → Toolchains & Run settings
=====================================================================

WHAT:  A settings page that shows every compiler/tool MEDHĀ found, WHERE it came
       from (bundled / settings / PATH / common folder) and its REAL version line
       (from running `--version`), lets the student pick a different exe, and
       choose the C / C++ standard, Turbo mode and the explanation language.
WHY:   On a lab PC the first question is always "which compiler is it using?".
       C-Lite has one fixed 2016 GCC 6.3; MEDHĀ shows the truth and lets you switch.
       Only standards the detected GCC really supports are offered.
USED BY: app.py (Tools menu).
FLOW:  open → toolchains.report() → table; Browse → settings.tool_paths →
       toolchains.clear_cache() → table refresh; OK → settings saved.
"""

from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QFileDialog, QFormLayout, QGroupBox, QHeaderView,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout)

from medha import settings, toolchains
from medha.platform_info import IS_WINDOWS


class ToolchainsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Toolchains & Run settings")
        self.resize(900, 560)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Detected tools (each version line below comes from actually running the tool):"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Tool", "Found in", "Path", "Version", ""])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lay.addWidget(self.table, 1)

        box = QGroupBox("Run settings")
        form = QFormLayout(box)
        self.c_std = QComboBox()
        self.cpp_std = QComboBox()
        self.turbo = QCheckBox("Turbo mode — run graphics.h / conio.h / iostream.h / void main() code unchanged")
        self.lang = QComboBox()
        self.lang.addItem("English", "en")
        self.lang.addItem("Hinglish (Roman script)", "hi")
        form.addRow("C standard (-std=)", self.c_std)
        form.addRow("C++ standard (-std=)", self.cpp_std)
        form.addRow("", self.turbo)
        form.addRow("Error explanations", self.lang)
        lay.addWidget(box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)
        self.refresh()

    def refresh(self):
        toolchains.clear_cache()
        rows = toolchains.report()
        self.table.setRowCount(0)
        for name, tool in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(name))
            self.table.setItem(r, 1, QTableWidgetItem(tool.source or "—"))
            self.table.setItem(r, 2, QTableWidgetItem(tool.path or "NOT FOUND"))
            self.table.setItem(r, 3, QTableWidgetItem(tool.version or ""))
            btn = QPushButton("Browse…")
            btn.clicked.connect(lambda _=False, n=name: self.browse(n))
            self.table.setCellWidget(r, 4, btn)
        self.table.resizeColumnsToContents()
        self._fill(self.c_std, toolchains.supported_c_standards(), settings.get("c_std"))
        self._fill(self.cpp_std, toolchains.supported_cpp_standards(), settings.get("cpp_std"))
        self.turbo.setChecked(bool(settings.get("turbo_mode", True)))
        idx = self.lang.findData(settings.get("explain_lang", "en"))
        self.lang.setCurrentIndex(max(0, idx))

    @staticmethod
    def _fill(combo, values, current):
        combo.clear()
        combo.addItems(values)
        if current in values:
            combo.setCurrentText(current)

    def browse(self, name):
        flt = "Programs (*.exe)" if IS_WINDOWS else "All files (*)"
        path, _ = QFileDialog.getOpenFileName(self, f"Choose {name}", "", flt)
        if path:
            paths = settings.get("tool_paths") or {}
            paths[name] = path
            settings.set("tool_paths", paths)
            self.refresh()

    def save(self):
        settings.set("c_std", self.c_std.currentText())
        settings.set("cpp_std", self.cpp_std.currentText())
        settings.set("turbo_mode", self.turbo.isChecked())
        settings.set("explain_lang", self.lang.currentData())
        self.accept()
