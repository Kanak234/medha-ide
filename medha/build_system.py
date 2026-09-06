"""
MEDHĀ IDE — Multi-Target Build System Engine
Handles GCC, G++, Clang, CMake, and Make multi-target builds (Debug vs Release).
Provides asynchronous QProcess build runner with GCC/Clang diagnostic error parsing.
"""

import os
import re
import shutil
from PySide6.QtCore import QProcess, QObject, Signal, Qt


class BuildDiagnostic:
    """Diagnostic item produced by compiler output parsing."""
    def __init__(self, file_path, line, col, severity, message):
        self.file_path = file_path
        self.line = int(line)
        self.col = int(col) if col else 1
        self.severity = severity.lower()
        self.message = message.strip()

    def __repr__(self):
        return f"<BuildDiagnostic {self.severity.upper()} {self.file_path}:{self.line}:{self.col} - {self.message}>"


class MultiTargetBuildEngine(QObject):
    """
    Non-blocking Build Engine using QProcess.
    Emits live stdout/stderr streams and parsed error diagnostics.
    """

    output_stream = Signal(str, str) # text, stream_type ('stdout' | 'stderr')
    build_finished = Signal(int, list, str) # exit_code, diagnostics, artifact_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)

        self.active_config = "Debug"  # "Debug" | "Release"
        self.active_file = ""
        self.artifact_path = ""
        self.diagnostics = []
        self.last_output = ""
        self.build_stage = "idle"

    def set_build_config(self, config_name):
        self.active_config = config_name

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.last_output += data
        self.output_stream.emit(data, "stdout")

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.last_output += data
        self.parse_compiler_output(data)
        self.output_stream.emit(data, "stderr")

    def parse_compiler_output(self, text):
        """Parse GCC / Clang error diagnostic format: file:line:col: error/warning: msg"""
        gcc_regex = re.compile(
            r'^([^:\n]+):(\d+):(?:(\d+):)?\s*(error|warning|fatal error|note):\s*(.+)$',
            re.MULTILINE | re.IGNORECASE
        )
        for match in gcc_regex.finditer(text):
            fpath, line, col, sev, msg = match.groups()
            abs_path = fpath if os.path.isabs(fpath) else os.path.join(
                os.path.dirname(self.active_file) if self.active_file else os.getcwd(), fpath
            )
            self.diagnostics.append(BuildDiagnostic(
                file_path=abs_path,
                line=line,
                col=col if col else 1,
                severity=sev,
                message=msg
            ))

    def _handle_finished(self, exit_code, exit_status):
        if self.build_stage == "compile_c" and exit_code == 0 and self.artifact_path:
            # Chain binary execution on successful compilation if requested
            self.build_stage = "run_binary"
            self.output_stream.emit(f"\n[MEDHĀ Build] Running compiled binary: {self.artifact_path}\n", "stdout")
            self.process.start(self.artifact_path, [])
            return

        self.build_finished.emit(exit_code, self.diagnostics, self.artifact_path)
        self.build_stage = "idle"

    def build_and_run_file(self, file_path, config="Debug", extra_flags=None):
        self.active_file = file_path
        self.active_config = config
        self.diagnostics = []
        self.last_output = ""
        ext = os.path.splitext(file_path)[1].lower()
        dir_name = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        self.artifact_path = os.path.join(dir_name, base_name)

        self.process.setWorkingDirectory(dir_name)

        # Base flags for Debug vs Release
        if config == "Release":
            flags = ["-O2", "-s", "-DNDEBUG", "-Wall"]
        else:
            flags = ["-g", "-O0", "-DDEBUG", "-Wall"]

        if extra_flags:
            flags.extend(extra_flags)

        if ext == ".c":
            compiler = shutil.which("gcc") or "gcc"
            cmd_args = flags + [file_path, "-o", self.artifact_path]
            self.build_stage = "compile_c"
            self.output_stream.emit(f"[MEDHĀ Build ({config})] {compiler} {' '.join(cmd_args)}\n", "stdout")
            self.process.start(compiler, cmd_args)
        elif ext in [".cpp", ".cc", ".cxx"]:
            compiler = shutil.which("g++") or shutil.which("clang++") or "g++"
            cmd_args = flags + [file_path, "-o", self.artifact_path]
            self.build_stage = "compile_c"
            self.output_stream.emit(f"[MEDHĀ Build ({config})] {compiler} {' '.join(cmd_args)}\n", "stdout")
            self.process.start(compiler, cmd_args)
        elif ext == ".py":
            python = shutil.which("python3") or "python3"
            self.build_stage = "run_binary"
            self.output_stream.emit(f"[MEDHĀ Build] Running Python script: {python} {file_path}\n", "stdout")
            self.process.start(python, [file_path])
        else:
            self.output_stream.emit(f"[MEDHĀ Build] Unsupported extension for direct run: {ext}\n", "stderr")
            self.build_finished.emit(1, [], "")

    def cancel_build(self):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
