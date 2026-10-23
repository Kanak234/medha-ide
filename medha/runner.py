"""
MEDHĀ IDE — runner.py  — the Run button (Ctrl+F5)
==================================================

WHAT:  Compiles and runs the active file with REAL tools, asynchronously:
         C / C++  → gcc / g++  (normal mode, or Turbo mode for graphics.h/conio.h/iostream.h)
         Java     → javac + java
         Python   → python -u
         JS       → node
       Streams stdout/stderr to the terminal, turns compiler errors into clickable
       Problems (with a beginner explanation), explains crashes, and forwards the
       student's typed input to the running program's stdin.
WHY:   v1 only knew `gcc file -o file` on Linux and had no way to type input into a
       running program (the terminal sent it to bash instead). v2 adds Windows
       (.exe, bundled MinGW via toolchains.py), Java packages, Turbo mode, the
       error explainer and interactive stdin — the things C-Lite users expect,
       plus what C-Lite cannot do (Java, Python, explanations).
USED BY: app.py (Run menu, terminal input routing), verify_medha.py (C3/C4 checks).
FLOW:  run_file(path) → build steps (QProcess, one after another) → start program
       → output()/output_received() … → finished(exit_code, diagnostics)
       Turbo programs: stdout → turbo.protocol.ProtocolDecoder → turbo_frame signal
       → turbo/panel.py redraws the 640×480 screen.
"""

import os
import re
import time

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, Signal

from medha import explain, settings, toolchains
from medha import platform_info as P
from medha.turbo import adapt as turbo_adapt
from medha.turbo import builder as turbo_builder
from medha.turbo.protocol import ProtocolDecoder


class ProblemDiagnostic:
    """One compiler/interpreter message for the Problems panel."""

    def __init__(self, file_path, line, col, severity, message, tip=None):
        self.file_path = file_path
        self.line = line
        self.col = col
        self.severity = severity          # "error" | "warning"
        self.message = message
        self.tip = tip                    # beginner explanation (explain.py) or None
        self.notes = []                   # GCC "note:" lines that belong to this one


# GCC / Clang / javac:  file:line[:col]: (fatal error|error|warning|note): message
# The optional drive letter handles Windows paths like C:\Users\x\a.c:12:5:
DIAG_RE = re.compile(
    r"^(?P<file>(?:[A-Za-z]:)?[^:\n]+?):(?P<line>\d+):(?:(?P<col>\d+):)?\s*"
    r"(?P<sev>fatal error|error|warning|note):\s*(?P<msg>.*)$")
LINK_RE = re.compile(r"undefined reference to|undefined symbol|ld: symbol\(s\) not found")
PY_FRAME_RE = re.compile(r'File "([^"]+)", line (\d+)')
PY_ERROR_RE = re.compile(r"^(\w+(?:Error|Exception|Exit|Interrupt)\b.*)$", re.M)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class ProcessRunner(QObject):
    output = Signal(str)                    # every piece of text (kept for verify_medha.py)
    output_received = Signal(str, str)      # text, "stdout" | "stderr" | "info"
    finished = Signal(int, list)            # exit_code, [ProblemDiagnostic]
    running_changed = Signal(bool)          # True while a build/program is active
    turbo_started = Signal(bool)            # Turbo program started; arg = needs graphics panel
    turbo_frame = Signal(object)            # ProtocolDecoder after a frame update
    turbo_message = Signal(dict)            # other protocol messages (input, sound, ...)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.errorOccurred.connect(self.handle_error)
        self.diagnostics = []
        self.active_file = ""
        self.last_output = ""
        self.stage = "idle"         # "build" while compiling, "run" while the program runs
        self.binary_to_run = None
        self._steps = []            # remaining build steps [(program, args, cwd, label)]
        self._run_cmd = None        # (program, args, cwd, env) started after the build
        self._source_map = {}       # temp build path → the user's real file
        self._decoder = None        # ProtocolDecoder while a Turbo program runs
        self._compile_text = ""     # compiler output, parsed for diagnostics at the end of a step
        self._t0 = 0.0
        self.lang = settings.get("explain_lang", "en")

    # ------------------------------------------------------------------ output
    def _emit_output(self, text, stream_type="stdout"):
        if not text:
            return
        self.last_output += text
        self.output.emit(text)
        self.output_received.emit(text, stream_type)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data()
        if self.stage == "build":
            text = data.decode("utf-8", errors="replace")
            self._compile_text += text
            self._emit_output(text, "stderr" if "error" in text else "stdout")
            return
        if self._decoder is not None:
            text, messages = self._decoder.feed(data)
            self._emit_output(text, "stdout")
            framed = False
            for m in messages:
                if m.get("t") == "frame":
                    framed = True
                else:
                    self.turbo_message.emit(m)
            if framed:
                self.turbo_frame.emit(self._decoder)
            return
        self._emit_output(data.decode("utf-8", errors="replace"), "stdout")

    def handle_stderr(self):
        text = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        if self.stage == "build":
            self._compile_text += text
        else:
            self._compile_text += text if self._is_python_or_java_run() else ""
        self._emit_output(text, "stderr")

    def _is_python_or_java_run(self):
        ext = os.path.splitext(self.active_file)[1].lower()
        return ext in (".py", ".java")

    # ------------------------------------------------------------ diagnostics
    def _map_file(self, path):
        """Compiler paths → the student's real file (Turbo mode compiles a temp copy)."""
        path = path.strip()
        cwd = os.path.dirname(self.active_file)
        full = path if os.path.isabs(path) else os.path.join(cwd, path)
        key = os.path.normcase(os.path.abspath(full))
        return self._source_map.get(key, full)

    def parse_diagnostics(self, text):
        """Fill self.diagnostics from compiler/interpreter output (kept public for tests)."""
        text = ANSI_RE.sub("", text.replace("\r\n", "\n"))
        for raw in text.split("\n"):
            m = DIAG_RE.match(raw)
            if m:
                sev = m.group("sev")
                msg = m.group("msg").strip()
                if sev == "note":
                    if self.diagnostics:
                        self.diagnostics[-1].notes.append(msg)
                    continue
                self.diagnostics.append(ProblemDiagnostic(
                    self._map_file(m.group("file")), int(m.group("line")),
                    int(m.group("col") or 1), "warning" if sev == "warning" else "error",
                    msg, explain.tip_for(msg, self.lang)))
            elif LINK_RE.search(raw) and "ld returned" not in raw and "collect2" not in raw:
                msg = re.sub(r"^.*?(undefined reference to|undefined symbol)", r"\1", raw).strip()
                self.diagnostics.append(ProblemDiagnostic(
                    self.active_file, 1, 1, "error", msg, explain.tip_for(raw, self.lang)))

    def parse_python_traceback(self, text):
        """Last frame inside the user's own files + the exception line → one diagnostic."""
        frames = [(f, int(l)) for f, l in PY_FRAME_RE.findall(text)
                  if not f.startswith("<") and os.path.abspath(f).startswith(os.path.dirname(self.active_file))]
        errs = PY_ERROR_RE.findall(text)
        if not errs:
            return
        msg = errs[-1].strip()
        fpath, line = frames[-1] if frames else (self.active_file, 1)
        # SyntaxError reports "line N" in the frame itself
        self.diagnostics.append(ProblemDiagnostic(fpath, line, 1, "error", msg,
                                                  explain.tip_for(msg, self.lang)))

    def parse_java_exception(self, text):
        """`Exception in thread "main" java.lang.X: msg` + `at Main.main(Main.java:7)`."""
        head = re.search(r'Exception in thread "[^"]+" ([\w.$]+(?::.*)?)', text)
        if not head:
            return
        where = re.findall(r"\(([\w$]+\.java):(\d+)\)", text)
        mine = [(f, int(l)) for f, l in where if f == os.path.basename(self.active_file)]
        line = mine[0][1] if mine else 1
        msg = head.group(1).strip()
        tip = explain.tip_for(msg, self.lang)
        if tip is None and "ArrayIndexOutOfBounds" in msg:
            tip = ("Index is outside the array: an array of length n has indexes 0 to n-1."
                   if self.lang != "hi" else "Index array ke bahar hai: length n ke array mein 0 se n-1 tak index hote hain.")
        elif tip is None and "NullPointerException" in msg:
            tip = ("An object variable is null — create it with `new` before calling its methods."
                   if self.lang != "hi" else "Object variable null hai — method call se pehle `new` se object banao.")
        elif tip is None and "InputMismatchException" in msg:
            tip = ("Scanner expected a number but got text — type a number."
                   if self.lang != "hi" else "Scanner ko number chahiye tha par text mila — number type karo.")
        self.diagnostics.append(ProblemDiagnostic(self.active_file, line, 1, "error", msg, tip))

    # ------------------------------------------------------------------ steps
    def _start(self, program, args, cwd, env=None):
        self.process.setWorkingDirectory(cwd)
        penv = QProcessEnvironment.systemEnvironment()
        for k, v in (env or {}).items():
            penv.insert(k, v)
        self.process.setProcessEnvironment(penv)
        self.process.start(program, args)

    def _next_step(self):
        """Run the next build step, or start the program when all steps passed."""
        if self._steps:
            program, args, cwd, label = self._steps.pop(0)
            self.stage = "build"
            self._compile_text = ""
            self._emit_output(f"[MEDHĀ] {label}: {os.path.basename(program)} {' '.join(args)}\n", "info")
            self._start(program, args, cwd)
            return
        if self._run_cmd:
            program, args, cwd, env = self._run_cmd
            self._run_cmd = None
            self.stage = "run"
            self._compile_text = ""
            self._t0 = time.monotonic()
            self._emit_output(f"[MEDHĀ] Running: {os.path.basename(program)} {' '.join(args)}\n", "info")
            self._start(program, args, cwd, env)
            return
        self._done(0)

    def handle_finished(self, exit_code, exit_status):
        crashed = exit_status == QProcess.ExitStatus.CrashExit
        if self.stage == "build":
            self.parse_diagnostics(self._compile_text)
            if exit_code == 0 and not crashed:
                self._next_step()
                return
            self._emit_output("[MEDHĀ] Build failed — see the Problems tab for each error and how to fix it.\n", "stderr")
            self._done(exit_code if exit_code else 1)
            return
        # program finished
        if self._decoder is not None:
            self._emit_output(self._decoder.flush_text(), "stdout")
        if self._is_python_or_java_run() and self._compile_text:
            if self.active_file.endswith(".py"):
                self.parse_python_traceback(self._compile_text)
            else:
                self.parse_java_exception(self._compile_text)
        secs = time.monotonic() - self._t0 if self._t0 else 0.0
        code = exit_code
        why = explain.explain_exit(code, crashed=crashed, windows=P.IS_WINDOWS, lang=self.lang)
        if crashed and not why:
            self._emit_output(f"\n[MEDHĀ] Program crashed (signal/code {code}).\n", "stderr")
        if why:
            self._emit_output(f"\n[MEDHĀ] {why['title']}\n        Why: {why['why']}\n        Fix: {why['fix']}\n", "stderr")
        self._emit_output(f"\n[MEDHĀ] Process exited after {secs:.2f} s with return value {code}\n", "info")
        self._done(code if not crashed else (code or 1))

    def handle_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            prog = self.process.program()
            self._emit_output(f"[MEDHĀ] Could not start '{prog}'. Is it installed? See Tools → Toolchains.\n", "stderr")
            self._done(1)

    def _done(self, code):
        was_active = self.stage != "idle"
        self.stage = "idle"
        self._decoder = None
        self._steps, self._run_cmd = [], None
        if was_active:
            self.running_changed.emit(False)
        self.finished.emit(code, self.diagnostics)

    # ------------------------------------------------------------ public API
    def is_running(self):
        return self.process.state() != QProcess.ProcessState.NotRunning

    def write_stdin(self, data):
        """Send typed input (str → a line, bytes → raw keys) to the running program."""
        if self.stage != "run" or not self.is_running():
            return False
        if isinstance(data, str):
            data = (data + ("\r\n" if self._decoder is not None else "\n")).encode("utf-8")
        self.process.write(data)
        return True

    def stop(self):
        if self.is_running():
            self.process.kill()
            self.process.waitForFinished(2000)

    def _fail(self, message):
        self._emit_output(f"[MEDHĀ] {message}\n", "stderr")
        self.stage = "idle"
        self.finished.emit(1, [])

    def run_file(self, file_path):
        """Compile (if needed) and run one file. Returns immediately; work is async."""
        if self.is_running():
            self.stop()
        file_path = os.path.abspath(file_path)
        self.active_file = file_path
        self.diagnostics, self.last_output = [], ""
        self.binary_to_run = None
        self._steps, self._run_cmd, self._source_map = [], None, {}
        self._decoder = None
        self._t0 = 0.0
        self.lang = settings.get("explain_lang", "en")
        ext = os.path.splitext(file_path)[1].lower()
        folder = os.path.dirname(file_path)
        base = os.path.splitext(os.path.basename(file_path))[0]
        try:
            if ext in (".c", ".cpp", ".cc", ".cxx", ".c++"):
                self._plan_c_cpp(file_path, ext, folder, base)
            elif ext == ".java":
                self._plan_java(file_path, folder, base)
            elif ext == ".py":
                py = toolchains.require("python")
                args = ["-u", file_path] if not py.endswith("py.exe") else ["-3", "-u", file_path]
                self._run_cmd = (py, args, folder, {"PYTHONIOENCODING": "utf-8"})
            elif ext in (".js", ".mjs"):
                node = __import__("shutil").which("node")
                if not node:
                    raise toolchains.ToolMissing("node")
                self._run_cmd = (node, [file_path], folder, None)
            else:
                self._fail(f"MEDHĀ cannot run '{ext}' files yet (C, C++, Java, Python, JavaScript are supported).")
                return
        except toolchains.ToolMissing as e:
            self._fail(str(e))
            return
        self.running_changed.emit(True)
        self._next_step()

    # ---------------------------------------------------------------- planners
    def _build_dir(self, folder):
        """`.medha_build/` next to the source, or an ASCII temp folder (Hindi paths on Windows)."""
        if P.IS_WINDOWS and not folder.isascii():
            d = os.path.join(str(P.ascii_work_dir()), "build")
        else:
            d = os.path.join(folder, ".medha_build")
        os.makedirs(d, exist_ok=True)
        return d

    def _plan_c_cpp(self, file_path, ext, folder, base):
        is_cpp = ext != ".c"
        cc = toolchains.require("gcc")
        cxx = toolchains.require("g++") if is_cpp else cc
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        if settings.get("turbo_mode", True) and turbo_adapt.needs_turbo(src):
            bp = turbo_builder.plan(file_path, cc, cxx)
            self._steps = list(bp.steps)
            self._source_map = bp.source_map
            self.binary_to_run = bp.binary
            for note in bp.notes:
                self._emit_output(f"[MEDHĀ] Turbo mode: {note} (only in a temp copy — your file is unchanged)\n", "info")
            self._decoder = ProtocolDecoder()
            self._run_cmd = (bp.binary, [], folder, turbo_builder.run_env({}))
            self.turbo_started.emit(bp.uses_panel)
            return
        out = os.path.join(self._build_dir(folder), base + P.EXE)
        self.binary_to_run = out
        std = settings.get("cpp_std" if is_cpp else "c_std")
        unbuffered = os.path.join(turbo_builder.RUNTIME_DIR, "prabha_unbuffered.h")
        args = [f"-std={std}", "-Wall", "-g",
                # stdout unbuffered → "Enter a number: " shows before scanf waits
                "-include", unbuffered, file_path, "-o", out]
        if not is_cpp:
            args.append("-lm")          # sqrt/pow link without the student knowing -lm
        if P.IS_WINDOWS:
            args.append("-static")      # runs on a PC without MinGW DLLs
        label = "Compiling C++" if is_cpp else "Compiling C"
        self._steps = [(cxx if is_cpp else cc, args, folder, label)]
        self._run_cmd = (out, [], folder, None)

    def _plan_java(self, file_path, folder, base):
        javac = toolchains.require("javac")
        java = toolchains.find("java").path or javac.replace("javac", "java")
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        m = re.search(r"public\s+(?:final\s+)?class\s+([A-Za-z_]\w*)", content) or \
            re.search(r"\bclass\s+([A-Za-z_]\w*)[^{]*\{[^}]*?static\s+void\s+main", content, re.S)
        cls = m.group(1) if m else base
        pkg = re.search(r"^\s*package\s+([\w.]+)\s*;", content, re.M)
        main_class = f"{pkg.group(1)}.{cls}" if pkg else cls
        out = self._build_dir(folder)
        self.binary_to_run = f"java -cp {out} {main_class}"
        self._steps = [(javac, ["-encoding", "UTF-8", "-Xlint:all", "-d", out, file_path], folder, "Compiling Java")]
        self._run_cmd = (java, ["-Dfile.encoding=UTF-8", "-cp", out, main_class], folder, None)
