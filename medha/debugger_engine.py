"""
MEDHĀ IDE — Interactive GDB Debugger Engine & Panels
Extends DebugSession with GUI panels:
 1. Breakpoints Panel
 2. Call Stack / Backtrace Panel
 3. Variables & Watch Expressions Panel
Signals UI updates for editor execution line highlighting and margin breakpoints.
"""

import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QLabel, QSplitter
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, Signal, QObject
from medha.debugger import DebugSession


class GdbDebuggerEngine(QObject):
    """Asynchronous Debugger Controller wrapper for GDB MI and DAP."""

    state_changed = Signal(str) # "running" | "stopped" | "terminated"
    stopped_at = Signal(str, int) # file_path, line
    variables_updated = Signal(list) # list of (name, value)
    frames_updated = Signal(list) # list of (level, func, file, line)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = None
        self.active_target = ""
        self.breakpoints = {} # file_path -> set of line numbers

    def start_debug(self, target_path, kind="gdb"):
        self.stop_debug()
        self.active_target = target_path
        self.session = DebugSession(target_path, kind=kind)
        self.session.start()

        # Apply set breakpoints
        for fpath, lines in self.breakpoints.items():
            for l in lines:
                self.session.set_breakpoint(fpath, l)

        self.session.run()
        self.state_changed.emit("running")

    def toggle_breakpoint(self, file_path, line):
        abs_path = os.path.abspath(file_path)
        if abs_path not in self.breakpoints:
            self.breakpoints[abs_path] = set()

        if line in self.breakpoints[abs_path]:
            self.breakpoints[abs_path].remove(line)
            is_added = False
        else:
            self.breakpoints[abs_path].add(line)
            is_added = True
            if self.session:
                self.session.set_breakpoint(abs_path, line)
        return is_added

    def step_over(self):
        if self.session and self.session.kind == "gdb":
            self.session._send_gdb_cmd("-exec-next")
            self.poll_stop_status()

    def step_into(self):
        if self.session and self.session.kind == "gdb":
            self.session._send_gdb_cmd("-exec-step")
            self.poll_stop_status()

    def step_out(self):
        if self.session and self.session.kind == "gdb":
            self.session._send_gdb_cmd("-exec-finish")
            self.poll_stop_status()

    def continue_exec(self):
        if self.session:
            self.session.continue_()
            self.state_changed.emit("running")

    def poll_stop_status(self):
        if self.session and self.session.wait_for_stop(timeout=2.0):
            self.state_changed.emit("stopped")
            self.fetch_stack_frames()
            self.fetch_variables()

    def fetch_stack_frames(self):
        if not self.session or self.session.kind != "gdb":
            return
        res = self.session._send_gdb_cmd("-stack-list-frames")
        frames = []
        # Parse frame={level="0",addr="...",func="main",file="main.c",line="5"}
        pattern = re.compile(r'frame=\{level="(\d+)",(?:[^}]*?)func="([^"]+)"(?:[^}]*?)file="([^"]+)"(?:[^}]*?)line="(\d+)"')
        for match in pattern.finditer(res):
            lvl, func, fpath, line = match.groups()
            frames.append((lvl, func, fpath, int(line)))
            if lvl == "0":
                self.stopped_at.emit(fpath, int(line))
        self.frames_updated.emit(frames)

    def fetch_variables(self):
        if not self.session or self.session.kind != "gdb":
            return
        res = self.session._send_gdb_cmd("-stack-list-variables --all-values")
        variables = []
        # Parse {name="acc",value="0"}
        pattern = re.compile(r'\{name="([^"]+)",value="([^"]+)"\}')
        for match in pattern.finditer(res):
            name, val = match.groups()
            variables.append((name, val))
        self.variables_updated.emit(variables)

    def evaluate_expression(self, expr):
        if self.session:
            return self.session.evaluate(expr)
        return ""

    def stop_debug(self):
        if self.session:
            self.session.terminate()
            self.session = None
            self.state_changed.emit("terminated")


class GdbDebuggerPanelWidget(QWidget):
    """UI Dock Panel for Breakpoints, Call Stack, and Variable Watch."""

    def __init__(self, engine: GdbDebuggerEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #21262d; background-color: #090d16; }
            QTabBar::tab { background-color: #161b22; color: #8b949e; padding: 4px 10px; }
            QTabBar::tab:selected { background-color: #0d1117; color: #58a6ff; }
        """)

        # 1. Breakpoints Table
        self.table_bp = QTableWidget(0, 3)
        self.table_bp.setHorizontalHeaderLabels(["File", "Line", "Status"])
        self.table_bp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.table_bp, "Breakpoints")

        # 2. Call Stack Table
        self.table_stack = QTableWidget(0, 4)
        self.table_stack.setHorizontalHeaderLabels(["Level", "Function", "File", "Line"])
        self.table_stack.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.table_stack, "Call Stack")

        # 3. Variables Table
        var_widget = QWidget()
        var_layout = QVBoxLayout(var_widget)
        var_layout.setContentsMargins(0, 0, 0, 0)

        self.table_vars = QTableWidget(0, 2)
        self.table_vars.setHorizontalHeaderLabels(["Variable Name", "Value"])
        self.table_vars.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        var_layout.addWidget(self.table_vars)

        # Watch Expression Bar
        watch_box = QHBoxLayout()
        self.input_watch = QLineEdit()
        self.input_watch.setPlaceholderText("Watch expression (e.g. acc)...")
        self.input_watch.setStyleSheet("background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d;")
        btn_eval = QPushButton("Eval")
        btn_eval.setStyleSheet("background-color: #1f6feb; color: white;")
        btn_eval.clicked.connect(self.eval_watch_expr)
        watch_box.addWidget(self.input_watch)
        watch_box.addWidget(btn_eval)
        var_layout.addLayout(watch_box)

        self.tabs.addTab(var_widget, "Variables & Watch")

        layout.addWidget(self.tabs)

        # Connect Engine Signals
        self.engine.frames_updated.connect(self.update_call_stack)
        self.engine.variables_updated.connect(self.update_variables)

    def refresh_breakpoints(self):
        self.table_bp.setRowCount(0)
        row = 0
        for fpath, lines in self.engine.breakpoints.items():
            for line in lines:
                self.table_bp.insertRow(row)
                self.table_bp.setItem(row, 0, QTableWidgetItem(os.path.basename(fpath)))
                self.table_bp.setItem(row, 1, QTableWidgetItem(str(line)))
                self.table_bp.setItem(row, 2, QTableWidgetItem("Active"))
                row += 1

    def update_call_stack(self, frames):
        self.table_stack.setRowCount(0)
        for row, (lvl, func, fpath, line) in enumerate(frames):
            self.table_stack.insertRow(row)
            self.table_stack.setItem(row, 0, QTableWidgetItem(str(lvl)))
            self.table_stack.setItem(row, 1, QTableWidgetItem(func))
            self.table_stack.setItem(row, 2, QTableWidgetItem(os.path.basename(fpath)))
            self.table_stack.setItem(row, 3, QTableWidgetItem(str(line)))

    def update_variables(self, variables):
        self.table_vars.setRowCount(0)
        for row, (name, val) in enumerate(variables):
            self.table_vars.insertRow(row)
            self.table_vars.setItem(row, 0, QTableWidgetItem(name))
            self.table_vars.setItem(row, 1, QTableWidgetItem(val))

    def eval_watch_expr(self):
        expr = self.input_watch.text().strip()
        if expr:
            val = self.engine.evaluate_expression(expr)
            row = self.table_vars.rowCount()
            self.table_vars.insertRow(row)
            self.table_vars.setItem(row, 0, QTableWidgetItem(f"[Watch] {expr}"))
            self.table_vars.setItem(row, 1, QTableWidgetItem(str(val)))
