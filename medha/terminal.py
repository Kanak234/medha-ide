"""
MEDHĀ IDE — terminal.py — integrated terminal (real shell, real program input)
===============================================================================

WHAT:  A text area + input line backed by a REAL shell process:
         Linux/macOS → $SHELL -i (bash/zsh)      Windows → cmd.exe /Q (UTF-8 code page)
       While a program started by the Run button is running, whatever the student
       types goes to THAT program's stdin (scanf / cin / input() / Scanner) instead
       of the shell.
WHY:   v1 hardcoded `/bin/bash -i` (no terminal on Windows) and always sent typed
       text to bash, so a program waiting in scanf() could never receive input —
       the most basic thing a C-Lite/Dev-C++ user expects.
USED BY: app.py (bottom dock), verify_medha.py C5 (real shell check).
FLOW:  typed line → send_input() → input_override(text) if a program runs
       (runner.write_stdin) else shell stdin → shell/program output → append_output()
"""

import os

from PySide6.QtCore import QProcess, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QTextCursor
from PySide6.QtWidgets import QLineEdit, QTextEdit, QVBoxLayout, QWidget

from medha import platform_info as P


class IntegratedTerminalWidget(QWidget):
    command_executed = Signal(str)

    MAX_CHARS = 400_000   # keep memory bounded for programs that print forever

    def __init__(self, workspace_path=None, parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path or os.getcwd()
        self._shell_started = False
        self._pending_input = []
        # set by app.py while a Run is active: callable(str) -> bool (True = consumed)
        self.input_override = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setFont(font)
        self.output_edit.setAccessibleName("Terminal output")
        self.output_edit.setStyleSheet("QTextEdit { background-color: #090d16; color: #c9d1d9; border: none; padding: 4px; }")
        layout.addWidget(self.output_edit)

        self.input_line = QLineEdit()
        self.input_line.setFont(font)
        self.input_line.setAccessibleName("Terminal input")
        self.input_line.setPlaceholderText("Type a command — or the input your running program is waiting for, then Enter")
        self.input_line.setStyleSheet("QLineEdit { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; padding: 4px; }")
        self.input_line.returnPressed.connect(self.send_input)
        layout.addWidget(self.input_line)

        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.workspace_path)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.on_process_finished)
        self.process.started.connect(self._on_process_started)
        self.process.errorOccurred.connect(self._on_process_error)
        self.start_shell()

    # ------------------------------------------------------------ shell life
    def start_shell(self):
        if self._shell_started:
            return
        state = self.process.state()
        if state == QProcess.ProcessState.NotRunning:
            program, args = P.default_shell()
            self.process.start(program, args)
            self.append_output(f"[MEDHĀ Terminal] {os.path.basename(program)} started in {self.workspace_path}\n",
                               color="#8b949e")
        elif state == QProcess.ProcessState.Running:
            self._shell_started = True

    def _on_process_started(self):
        self._shell_started = True
        if P.IS_WINDOWS:
            # UTF-8 code page so Hindi file names and box characters print correctly
            self.process.write(b"chcp 65001 >nul\r\n")
        for cmd in self._pending_input:
            self._write_shell(cmd)
        self._pending_input.clear()

    def on_process_finished(self, exit_code, exit_status):
        self.append_output(f"\n[shell exited with code {exit_code}]\n", color="#8b949e")
        self._shell_started = False

    def _on_process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.append_output("[MEDHĀ Terminal] Could not start the system shell.\n", color="#f85149")

    def closeEvent(self, event):
        self.shutdown()
        super().closeEvent(event)

    def shutdown(self):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1500):
                self.process.kill()
                self.process.waitForFinished(1000)

    def set_working_directory(self, folder):
        """Opening a new workspace also moves the shell there."""
        self.workspace_path = folder
        self.process.setWorkingDirectory(folder)
        if self._shell_started:
            quoted = f'cd /d "{folder}"' if P.IS_WINDOWS else f"cd '{folder}'"
            self._write_shell(quoted)

    # ---------------------------------------------------------------- output
    def _decode(self, data: bytes) -> str:
        return data.decode("utf-8", errors="replace")

    def read_stdout(self):
        self.append_output(self._decode(self.process.readAllStandardOutput().data()))

    def read_stderr(self):
        self.append_output(self._decode(self.process.readAllStandardError().data()), color="#f85149")

    def append_output(self, text, color=None):
        if not text:
            return
        cursor = self.output_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color or "#c9d1d9"))
        cursor.setCharFormat(fmt)
        cursor.insertText(text.replace("\r\n", "\n"))
        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()
        doc = self.output_edit.document()
        if doc.characterCount() > self.MAX_CHARS:   # trim the oldest third
            c = QTextCursor(doc)
            c.movePosition(QTextCursor.MoveOperation.Start)
            c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor,
                           doc.characterCount() // 3)
            c.removeSelectedText()

    def clear(self):
        self.output_edit.clear()

    # ----------------------------------------------------------------- input
    def _write_shell(self, text):
        newline = "\r\n" if P.IS_WINDOWS else "\n"
        self.process.write((text + newline).encode("utf-8"))

    def send_input(self):
        text = self.input_line.text()
        self.input_line.clear()
        # a running program (scanf / cin / input()) gets the line first
        if self.input_override is not None and self.input_override(text):
            self.append_output(text + "\n", color="#79c0ff")
            return
        if self._shell_started and self.process.state() == QProcess.ProcessState.Running:
            self.append_output(text + "\n", color="#79c0ff")
            self._write_shell(text)
            self.command_executed.emit(text)
        else:
            self._pending_input.append(text)
            self.start_shell()

    def execute_command(self, cmd_string):
        if self._shell_started and self.process.state() == QProcess.ProcessState.Running:
            self.append_output(cmd_string + "\n", color="#79c0ff")
            self._write_shell(cmd_string)
        else:
            self._pending_input.append(cmd_string)
            self.start_shell()
