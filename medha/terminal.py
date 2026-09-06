import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PySide6.QtGui import QFont, QTextCursor, QColor
from PySide6.QtCore import QProcess, Qt, Signal

class IntegratedTerminalWidget(QWidget):
    command_executed = Signal(str)

    def __init__(self, workspace_path="/home/kanak/Desktop/ide", parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        font = QFont("Monospace", 10)
        self.output_edit.setFont(font)
        self.output_edit.setStyleSheet("""
            QTextEdit {
                background-color: #090d16;
                color: #58a6ff;
                border: none;
                padding: 4px;
            }
        """)
        layout.addWidget(self.output_edit)

        # Input line for real interactive process stdin
        self.input_line = QLineEdit()
        self.input_line.setFont(font)
        self.input_line.setPlaceholderText("Enter command or process input...")
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                padding: 4px;
            }
        """)
        self.input_line.returnPressed.connect(self.send_input)
        layout.addWidget(self.input_line)

        # Real QProcess bash shell
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.workspace_path)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.on_process_finished)

        self.start_shell()

    def closeEvent(self, event):
        if hasattr(self, 'process') and self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
        super().closeEvent(event)

    def on_process_finished(self, exit_code, exit_status):
        self.append_output(f"\n[Process exited with code {exit_code}]\n", color="#8b949e")

    def start_shell(self):
        if self.process.state() == QProcess.ProcessState.NotRunning:
            shell = os.environ.get("SHELL", "/bin/bash")
            self.process.start(shell, ["-i"])
            self.append_output(f"[MEDHĀ Real Terminal] Started shell: {shell}\n")

    def read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.append_output(data)

    def read_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.append_output(data, color="#f85149")

    def append_output(self, text, color=None):
        cursor = self.output_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if color:
            fmt = cursor.charFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()

    def send_input(self):
        text = self.input_line.text()
        self.input_line.clear()

        if self.process.state() == QProcess.ProcessState.Running:
            self.append_output(f"{text}\n", color="#79c0ff")
            self.process.write((text + "\n").encode("utf-8"))
            self.command_executed.emit(text)
        else:
            self.start_shell()
            self.process.write((text + "\n").encode("utf-8"))

    def execute_command(self, cmd_string):
        self.start_shell()
        self.append_output(f"{cmd_string}\n", color="#79c0ff")
        self.process.write((cmd_string + "\n").encode("utf-8"))
