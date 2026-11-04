"""Status values come from the active document, compiler discovery and local Git."""
import os
import psutil
from PySide6.QtCore import QObject, QProcess, QTimer
from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtGui import QAction
from medha import toolchains


class StatusController(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        bar = QStatusBar()
        window.setStatusBar(bar)
        self.branch = QLabel('Git: checking…')
        self.diagnostics = QLabel('No build diagnostics')
        window.lbl_status = QLabel('Ready')
        window.lbl_cursor_pos = QLabel('No active file')
        self.compiler = QLabel('Compiler: —')
        window.lbl_theme = QLabel('Medhā Dark')
        window.lbl_sys_info = QLabel()
        for label in [self.branch, self.diagnostics]:
            bar.addWidget(label)
        bar.addWidget(window.lbl_status, 1)
        for label in [window.lbl_cursor_pos, self.compiler, window.lbl_theme, window.lbl_sys_info]:
            bar.addPermanentWidget(label)
        self.monitor = QAction('Show CPU and RAM', window)
        self.monitor.setCheckable(True)
        self.monitor.setChecked(window.workbench.prefs.value('system_monitor', False, type=bool))
        self.monitor.toggled.connect(self.toggle_monitor)
        window.menuBar().actions()[3].menu().addAction(self.monitor)
        self.toggle_monitor(self.monitor.isChecked())
        self.git = QProcess(self)
        self.git.finished.connect(self.branch_finished)
        self.git.errorOccurred.connect(lambda _: self.branch.setText('Git unavailable'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)
        self.refresh()
        # Git is a short, local asynchronous command; no fetch or network is involved.

    def toggle_monitor(self, enabled):
        self.window.lbl_sys_info.setVisible(enabled)
        self.window.workbench.prefs.setValue('system_monitor', enabled)

    def refresh(self):
        if self.git.state() == QProcess.ProcessState.NotRunning:
            self.git.setWorkingDirectory(self.window.workspace_path)
            self.git.start('git', ['rev-parse', '--abbrev-ref', 'HEAD'])
        if self.monitor.isChecked():
            self.window.lbl_sys_info.setText(f'CPU {psutil.cpu_percent():.0f}% · RAM {psutil.virtual_memory().percent:.0f}%')
        self.document_changed()

    def branch_finished(self, code, status):
        text = bytes(self.git.readAllStandardOutput()).decode('utf-8', 'replace').strip()
        self.branch.setText(('Branch: ' + text) if code == 0 and text else 'No Git repository')

    def document_changed(self):
        window = self.window
        editor = window.get_current_editor()
        name = os.path.basename(editor.file_path) if editor and editor.file_path else ('Untitled' if editor else 'Welcome')
        window.setWindowTitle(f'Medhā · {name} · {os.path.basename(window.workspace_path)}')
        if not editor:
            window.lbl_cursor_pos.setText('No active file')
            self.compiler.setText('Compiler: —')
            return
        cursor = editor.textCursor()
        encoding = getattr(editor, 'encoding_label', 'UTF-8')
        window.lbl_cursor_pos.setText(f'Ln {cursor.blockNumber()+1}, Col {cursor.columnNumber()+1} · {editor.lang.upper()} · {encoding}')
        tool_name = {'c': 'gcc', 'cpp': 'g++', 'java': 'javac', 'python': 'python'}.get(editor.lang)
        tool = toolchains.find(tool_name) if tool_name else None
        self.compiler.setText(f'{tool_name}: ' + ('ready' if tool.found else 'not found') if tool else 'Compiler: —')
        self.compiler.setToolTip(tool.path or '' if tool else '')
        # Discovery respects bundled/user-configured compilers, not just PATH.

    def set_diagnostics(self, diagnostics):
        errors = sum(d.severity == 'error' for d in diagnostics)
        warnings = sum(d.severity == 'warning' for d in diagnostics)
        self.diagnostics.setText(f'{errors} errors · {warnings} warnings')
