import os
import re
from PySide6.QtCore import QProcess, QObject, Signal

class ProblemDiagnostic:
    def __init__(self, file_path, line, col, severity, message):
        self.file_path = file_path
        self.line = line
        self.col = col
        self.severity = severity
        self.message = message


class ProcessRunner(QObject):
    output = Signal(str)
    output_received = Signal(str, str) # text, stream_type ('stdout' or 'stderr')
    finished = Signal(int, list) # exit_code, list of ProblemDiagnostic
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.diagnostics = []
        self.active_file = ""
        self.last_output = ""
        self.stage = "run"
        self.binary_to_run = None

    def _emit_output(self, text, stream_type='stdout'):
        self.last_output += text
        self.output.emit(text)
        self.output_received.emit(text, stream_type)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self._emit_output(data, 'stdout')

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.parse_diagnostics(data)
        self._emit_output(data, 'stderr')

    def parse_diagnostics(self, text):
        # GCC / G++: main.c:5:10: error: expected ';' before 'return'
        gcc_pattern = re.compile(r'^([^:\n]+):(\d+):(\d+):\s*(error|warning|note):\s*(.+)$', re.MULTILINE)
        for match in gcc_pattern.finditer(text):
            fpath, line, col, sev, msg = match.groups()
            self.diagnostics.append(ProblemDiagnostic(
                file_path=fpath if os.path.isabs(fpath) else os.path.join(os.path.dirname(self.active_file), fpath),
                line=int(line),
                col=int(col),
                severity=sev.lower(),
                message=msg.strip()
            ))

        # Python Traceback: File "main.py", line 4, in <module>
        py_pattern = re.compile(r'File "([^"]+)", line (\d+), in', re.MULTILINE)
        for match in py_pattern.finditer(text):
            fpath, line = match.groups()
            self.diagnostics.append(ProblemDiagnostic(
                file_path=fpath,
                line=int(line),
                col=1,
                severity='error',
                message='Runtime Exception / Syntax Error'
            ))

        # Javac: /path/File.java:LINE: error: MESSAGE
        javac_pattern = re.compile(r'^([^:\n]+):(\d+):\s*(error|warning):\s*(.+)$', re.MULTILINE)
        for match in javac_pattern.finditer(text):
            fpath, line, sev, msg = match.groups()
            self.diagnostics.append(ProblemDiagnostic(
                file_path=fpath if os.path.isabs(fpath) else os.path.join(os.path.dirname(self.active_file), fpath),
                line=int(line),
                col=1,
                severity=sev.lower(),
                message=msg.strip()
            ))

    def handle_finished(self, exit_code, exit_status):
        if self.stage == "compile":
            if exit_code == 0:
                self.stage = "run"
                if hasattr(self, 'java_args') and self.java_args:
                    self._emit_output(f"[VAISHNAVĪ] Compilation succeeded. Running Java class: {' '.join(self.java_args)}\n", 'stdout')
                    self.process.start(self.java_cmd, self.java_args)
                    self.java_args = None
                    return
                elif self.binary_to_run and os.path.exists(self.binary_to_run):
                    self._emit_output(f"[VAISHNAVĪ] Compilation succeeded. Running binary: {self.binary_to_run}\n", 'stdout')
                    self.process.start(self.binary_to_run, [])
                    return
            self.finished.emit(exit_code, self.diagnostics)
        else:
            self.finished.emit(exit_code, self.diagnostics)

    def run_file(self, file_path):
        import shutil
        self.active_file = file_path
        self.diagnostics = []
        self.last_output = ""
        self.binary_to_run = None
        self.java_args = None
        ext = os.path.splitext(file_path)[1].lower()
        dir_name = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        self.process.setWorkingDirectory(dir_name)

        if ext == '.c':
            bin_path = os.path.join(dir_name, base_name)
            self.binary_to_run = bin_path
            self.stage = "compile"
            cmd = "gcc"
            args = ["-g", file_path, "-o", bin_path]
            self._emit_output(f"[VAISHNAVĪ] Compiling C source: gcc -g {file_path} -o {bin_path}\n", 'stdout')
            self.process.start(cmd, args)
        elif ext in ['.cpp', '.cc', '.cxx']:
            bin_path = os.path.join(dir_name, base_name)
            self.binary_to_run = bin_path
            self.stage = "compile"
            cmd = "g++"
            args = ["-g", file_path, "-o", bin_path]
            self._emit_output(f"[VAISHNAVĪ] Compiling C++ source: g++ -g {file_path} -o {bin_path}\n", 'stdout')
            self.process.start(cmd, args)
        elif ext == '.java':
            javac_path = shutil.which("javac")
            java_path = shutil.which("java")

            if not javac_path and not java_path:
                self.stage = "run"
                self._emit_output("javac not found — install a JDK\n", 'stderr')
                self.finished.emit(1, [])
                return

            # Read public class name if declared in file
            class_name = base_name
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    m = re.search(r'public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', content)
                    if m:
                        class_name = m.group(1)
            except Exception:
                pass

            build_dir = os.path.join(dir_name, ".medha_build")
            os.makedirs(build_dir, exist_ok=True)

            if javac_path:
                self.binary_to_run = f"java -cp {build_dir} {class_name}"
                self.java_cmd = java_path or "java"
                self.java_args = ["-cp", build_dir, class_name]
                self.stage = "compile"
                self._emit_output(f"[VAISHNAVĪ] Compiling Java source: javac -d {build_dir} {file_path}\n", 'stdout')
                self.process.start(javac_path, ["-d", build_dir, file_path])
            else:
                # Direct single-file Java runtime execution (Java 11+)
                self.stage = "run"
                self.java_cmd = java_path
                self._emit_output(f"[VAISHNAVĪ] Running Java script: java {file_path}\n", 'stdout')
                self.process.start(java_path, [file_path])
        elif ext == '.py':
            self.stage = "run"
            cmd = "python3"
            args = [file_path]
            self._emit_output(f"[VAISHNAVĪ] Running Python script: python3 {file_path}\n", 'stdout')
            self.process.start(cmd, args)
        elif ext in ['.js', '.ts']:
            self.stage = "run"
            cmd = "node"
            args = [file_path]
            self._emit_output(f"[VAISHNAVĪ] Running Node.js script: node {file_path}\n", 'stdout')
            self.process.start(cmd, args)
        else:
            self.stage = "run"
            self._emit_output(f"[VAISHNAVĪ] Unsupported file extension: {ext}\n", 'stderr')
            self.finished.emit(1, [])
