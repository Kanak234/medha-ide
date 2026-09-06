"""
MEDHĀ IDE — Live Disassembly & Assembly Inspector Module
Runs gcc -S -fverbose-asm or objdump -d in background to render
real-time x86_64 assembly code corresponding to active C code functions.
"""

import os
import shutil
from PySide6.QtCore import QProcess, QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QFontDialog, QPushButton, QHBoxLayout
from PySide6.QtGui import QFont, QColor, QTextCursor


class DisassemblyInspectorWidget(QWidget):
    """Side-by-side Live Assembly Inspector Panel (Compiler Explorer)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_file = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel(" LIVE DISASSEMBLY & ASSEMBLY INSPECTOR (gcc -S -fverbose-asm)")
        header.setStyleSheet("background-color: #161b22; color: #79c0ff; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        # Output Assembly Editor
        self.asm_edit = QTextEdit()
        self.asm_edit.setReadOnly(True)
        self.asm_edit.setFont(QFont("Monospace", 9))
        self.asm_edit.setStyleSheet("""
            QTextEdit {
                background-color: #090d16;
                color: #e6edf3;
                border: none;
                padding: 4px;
            }
        """)
        layout.addWidget(self.asm_edit)

        # Control Bar
        ctrl_layout = QHBoxLayout()
        btn_refresh = QPushButton("⚡ Disassemble Active File")
        btn_refresh.setStyleSheet("background-color: #1f6feb; color: white; font-weight: bold; padding: 4px 8px;")
        btn_refresh.clicked.connect(self.disassemble_active_file)
        ctrl_layout.addWidget(btn_refresh)
        ctrl_layout.addStretch()

        layout.addLayout(ctrl_layout)

        # QProcess background disassembly runner
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)

    def set_active_file(self, file_path):
        self.active_file = file_path
        if file_path and os.path.exists(file_path):
            self.disassemble_active_file()

    def disassemble_active_file(self):
        if not self.active_file or not os.path.exists(self.active_file):
            self.asm_edit.setPlainText("// No active saved C/C++ file selected.")
            return

        ext = os.path.splitext(self.active_file)[1].lower()
        if ext not in ['.c', '.cpp', '.cc', '.cxx']:
            self.asm_edit.setPlainText(f"// Disassembly not supported for extension: {ext}")
            return

        compiler = shutil.which("gcc") or "gcc"
        dir_name = os.path.dirname(self.active_file)
        asm_out_path = os.path.splitext(self.active_file)[0] + ".s"

        cmd_args = ["-S", "-fverbose-asm", "-O0", self.active_file, "-o", asm_out_path]
        self.process.setWorkingDirectory(dir_name)
        self.asm_edit.setPlainText(f"; [MEDHĀ Disassembler] Generating x86_64 assembly for {self.active_file}...\n")
        self.process.start(compiler, cmd_args)

    def _read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.asm_edit.append(data)

    def _read_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.asm_edit.append(f"; Error: {data}")

    def on_disassembly_finished(self, exit_code):
        asm_out_path = os.path.splitext(self.active_file)[0] + ".s"
        if os.path.exists(asm_out_path):
            try:
                with open(asm_out_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                filtered = [ln for ln in lines if not ln.strip().startswith('.cfi') and not ln.strip().startswith('.L')]
                self.asm_edit.setPlainText("".join(filtered[:300]))
            except Exception as e:
                self.asm_edit.append(f"; Error reading disassembly file: {e}")
