"""
MEDHĀ IDE — Automated Static Analysis & Safety Linter Module
Runs cppcheck and clang-tidy asynchronously via QProcess to detect:
 - Memory leaks
 - Buffer overflows
 - Undefined behavior
 - Null pointer dereferences
"""

import os
import re
import shutil
from PySide6.QtCore import QProcess, QObject, Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)


class SafetyDiagnostic:
    def __init__(self, file_path, line, severity, tool, message):
        self.file_path = file_path
        self.line = int(line) if line else 1
        self.severity = severity.lower() # "error" | "warning" | "style" | "performance"
        self.tool = tool # "cppcheck" | "clang-tidy"
        self.message = message.strip()


class StaticAnalyzerEngine(QObject):
    """Asynchronous background static code analyzer using cppcheck and clang-tidy."""

    analysis_finished = Signal(list) # list of SafetyDiagnostic
    output_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.finished.connect(self._on_finished)
        self.active_file = ""
        self.raw_output = ""
        self.diagnostics = []
        self.active_tool = "cppcheck"

    def analyze_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return

        self.active_file = file_path
        self.diagnostics = []
        self.raw_output = ""

        cppcheck_bin = shutil.which("cppcheck")
        clang_tidy_bin = shutil.which("clang-tidy")

        if cppcheck_bin:
            self.active_tool = "cppcheck"
            cmd_args = [
                "--enable=all", "--suppress=missingIncludeSystem", "--template={file}:{line}:{severity}:{message}",
                file_path
            ]
            self.output_received.emit(f"[MEDHĀ Safety Linter] Running cppcheck on {file_path}...\n")
            self.process.start(cppcheck_bin, cmd_args)
        elif clang_tidy_bin:
            self.active_tool = "clang-tidy"
            cmd_args = [file_path, "--", "-I."]
            self.output_received.emit(f"[MEDHĀ Safety Linter] Running clang-tidy on {file_path}...\n")
            self.process.start(clang_tidy_bin, cmd_args)
        else:
            self.output_received.emit("[MEDHĀ Safety Linter] cppcheck or clang-tidy not installed. Skipping static analysis.\n")
            self.analysis_finished.emit([])

    def _read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.raw_output += data
        self.output_received.emit(data)

    def _read_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.raw_output += data
        self._parse_output(data)
        self.output_received.emit(data)

    def _parse_output(self, text):
        if self.active_tool == "cppcheck":
            # format: file:line:severity:message
            pattern = re.compile(r'^([^:\n]+):(\d+):([a-zA-Z]+):(.+)$', re.MULTILINE)
            for m in pattern.finditer(text):
                fpath, line, sev, msg = m.groups()
                self.diagnostics.append(SafetyDiagnostic(
                    file_path=fpath, line=line, severity=sev, tool="cppcheck", message=msg
                ))
        elif self.active_tool == "clang-tidy":
            # format: file:line:col: warning: message [check-name]
            pattern = re.compile(r'^([^:\n]+):(\d+):\d+:\s*(warning|error):\s*(.+)$', re.MULTILINE)
            for m in pattern.finditer(text):
                fpath, line, sev, msg = m.groups()
                self.diagnostics.append(SafetyDiagnostic(
                    file_path=fpath, line=line, severity=sev, tool="clang-tidy", message=msg
                ))

    def _on_finished(self, exit_code, status):
        self.analysis_finished.emit(self.diagnostics)


class SafetyDiagnosticsPanelWidget(QWidget):
    """UI Panel displaying static analysis warnings & memory leak issues."""

    diagnostic_selected = Signal(str, int) # file_path, line

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(" SAFETY DIAGNOSTICS & STATIC ANALYSIS (cppcheck / clang-tidy)")
        header.setStyleSheet("background-color: #161b22; color: #e3b341; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Tool", "Severity", "Line", "Safety Warning / Leak Message"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
            }
            QTableWidget::item:hover { background-color: #161b22; }
            QTableWidget::item:selected { background-color: #1f6feb; color: white; }
        """)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.table)

    def set_diagnostics(self, diagnostics):
        self.table.setRowCount(0)
        for row, diag in enumerate(diagnostics):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(diag.tool))
            self.table.setItem(row, 1, QTableWidgetItem(diag.severity.upper()))
            self.table.setItem(row, 2, QTableWidgetItem(str(diag.line)))
            item_msg = QTableWidgetItem(diag.message)
            item_msg.setData(Qt.UserRole, (diag.file_path, diag.line))
            self.table.setItem(row, 3, item_msg)

    def _on_cell_double_clicked(self, row, col):
        item = self.table.item(row, 3)
        if item:
            data = item.data(Qt.UserRole)
            if data:
                fpath, line = data
                self.diagnostic_selected.emit(fpath, line)
