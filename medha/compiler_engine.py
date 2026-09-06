"""
MEDHĀ IDE — Multi-Language Compiler & Execution Engine
Asynchronous, thread-safe process execution manager supporting C, C++, Python, and Java.
Emits live output streams and regex-parsed compiler diagnostics via Qt Signals & Slots.
"""

import os
import re
import shutil
from PySide6.QtCore import QProcess, QObject, Signal


class DiagnosticIssue:
    def __init__(self, file_path, line, col, severity, message):
        self.file_path = file_path
        self.line = int(line) if line else 1
        self.col = int(col) if col else 1
        self.severity = severity.lower()
        self.message = message.strip()


class UniversalCompilerEngine(QObject):
    """
    Non-blocking execution manager for C, C++, Python, and Java.
    Streams stdout/stderr in real-time and parses error diagnostics.
    """

    output_stream = Signal(str, str) # text, stream_type ('stdout' | 'stderr')
    finished = Signal(int, list, str) # exit_code, diagnostics_list, artifact_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)

        self.active_file = ""
        self.artifact_path = ""
        self.diagnostics = []
        self.stage = "idle"
        self.build_config = "Debug"

    def _on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.output_stream.emit(data, "stdout")

    def _on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self._parse_diagnostics(data)
        self.output_stream.emit(data, "stderr")

    def _parse_diagnostics(self, text):
        # GCC / Clang / Javac / Python trace parser
        gcc_pattern = re.compile(
            r'^([^:\n]+):(\d+):(?:(\d+):)?\s*(error|warning|fatal error|note):\s*(.+)$',
            re.MULTILINE | re.IGNORECASE
        )
        for m in gcc_pattern.finditer(text):
            fpath, line, col, sev, msg = m.groups()
            abs_p = fpath if os.path.isabs(fpath) else os.path.join(
                os.path.dirname(self.active_file) if self.active_file else os.getcwd(), fpath
            )
            self.diagnostics.append(DiagnosticIssue(abs_p, line, col, sev, msg))

    def _on_finished(self, exit_code, exit_status):
        if self.stage == "compile_c" and exit_code == 0 and self.artifact_path:
            self.stage = "run_binary"
            self.output_stream.emit(f"\n[MEDHĀ Engine] Running binary: {self.artifact_path}\n", "stdout")
            self.process.start(self.artifact_path, [])
            return
        elif self.stage == "compile_java" and exit_code == 0:
            self.stage = "run_binary"
            class_name = os.path.splitext(os.path.basename(self.active_file))[0]
            dir_name = os.path.dirname(self.active_file)
            java_bin = shutil.which("java") or "java"
            self.output_stream.emit(f"\n[MEDHĀ Engine] Running Java class: {class_name}\n", "stdout")
            self.process.setWorkingDirectory(dir_name)
            self.process.start(java_bin, ["-cp", ".", class_name])
            return

        self.finished.emit(exit_code, self.diagnostics, self.artifact_path)
        self.stage = "idle"

    def execute_file(self, file_path, build_config="Debug"):
        if not file_path or not os.path.exists(file_path):
            self.output_stream.emit(f"[MEDHĀ Engine] Error: File not found: {file_path}\n", "stderr")
            self.finished.emit(1, [], "")
            return

        self.active_file = file_path
        self.build_config = build_config
        self.diagnostics = []
        ext = os.path.splitext(file_path)[1].lower()
        dir_name = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        self.artifact_path = os.path.join(dir_name, base_name)

        self.process.setWorkingDirectory(dir_name)
        flags = ["-O2", "-s", "-DNDEBUG", "-Wall"] if build_config == "Release" else ["-g", "-O0", "-DDEBUG", "-Wall"]

        if ext == ".c":
            compiler = shutil.which("gcc") or "gcc"
            cmd_args = flags + [file_path, "-o", self.artifact_path]
            self.stage = "compile_c"
            self.output_stream.emit(f"[MEDHĀ Engine ({build_config})] {compiler} {' '.join(cmd_args)}\n", "stdout")
            self.process.start(compiler, cmd_args)
        elif ext in [".cpp", ".cc", ".cxx"]:
            compiler = shutil.which("g++") or "g++"
            cmd_args = flags + [file_path, "-o", self.artifact_path]
            self.stage = "compile_c"
            self.output_stream.emit(f"[MEDHĀ Engine ({build_config})] {compiler} {' '.join(cmd_args)}\n", "stdout")
            self.process.start(compiler, cmd_args)
        elif ext == ".py":
            python = shutil.which("python3") or "python3"
            self.stage = "run_binary"
            self.output_stream.emit(f"[MEDHĀ Engine] Executing Python: {python} -u {file_path}\n", "stdout")
            self.process.start(python, ["-u", file_path])
        elif ext == ".java":
            javac = shutil.which("javac") or "javac"
            self.stage = "compile_java"
            self.output_stream.emit(f"[MEDHĀ Engine] Compiling Java: {javac} {file_path}\n", "stdout")
            self.process.start(javac, [file_path])
        else:
            self.output_stream.emit(f"[MEDHĀ Engine] Unsupported file type: {ext}\n", "stderr")
            self.finished.emit(1, [], "")

    def cancel(self):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
