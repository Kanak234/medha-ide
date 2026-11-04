"""
MEDHĀ IDE — terminal.py — integrated terminal (real shell, real program input)
===============================================================================

WHAT:  A text area + input line backed by a REAL pseudo-terminal:
          Linux/macOS → pty.openpty() + QSocketNotifier (master fd) → bash/zsh -i
          Windows     → pywinpty (ConPTY) if available, else QProcess fallback
        While a program started by the Run button is running, whatever the student
        types goes to THAT program's stdin (scanf / cin / input() / Scanner) instead
        of the shell.
WHY:   v1 hardcoded `/bin/bash -i` (no terminal on Windows) and always sent typed
       text to bash, so a program waiting in scanf() could never receive input —
       the most basic thing a C-Lite/Dev-C++ user expects. The QProcess-only approach
       also made bash print "cannot set terminal process group / no job control"
       and broke interactive programs (vim, top, colours, Ctrl+C). A real pty fixes
       all of this.
USED BY: app.py (bottom dock), verify_medha.py C5 (real shell check).
FLOW:  typed line → send_input() → input_override(text) if a program runs
       (runner.write_stdin) else shell stdin → shell/program output → append_output()
"""

import logging
import os
import signal

from PySide6.QtCore import QObject, QSocketNotifier, QProcess, Signal
from PySide6.QtGui import QColor, QFontDatabase, QTextCursor
from PySide6.QtWidgets import QLineEdit, QTextEdit, QVBoxLayout, QWidget

from medha import platform_info as P
from medha.terminal_text import TerminalText

logger = logging.getLogger(__name__)


class _PtyProcess(QObject):
    """
    Base class for pseudo-terminal backends.
    Subclasses implement: start(), write(), shutdown(), _on_ready_read().
    """
    ready_read = Signal(bytes)
    finished = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, workspace_path, parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path
        self._shell_started = False

    def start(self):
        raise NotImplementedError

    def write(self, data: bytes):
        raise NotImplementedError

    def shutdown(self):
        raise NotImplementedError


class _UnixPtyProcess(_PtyProcess):
    """
    Linux/macOS pseudo-terminal using pty.openpty() + QSocketNotifier.

    WHY pty.openpty(): it allocates a real pseudo-terminal pair (master, slave).
    The slave side becomes the child's controlling terminal (setsid + ioctl TIOCSCTTY),
    so bash thinks it has a real TTY → job control works, colours work, Ctrl+C sends
    SIGINT to the foreground process group, and the "cannot set terminal process group"
    message disappears.

    WHY QSocketNotifier: it integrates the master fd into Qt's event loop so we get
    readyRead notifications without a separate thread. The notifier watches the master
    fd for readability and calls _on_ready_read() which reads and emits ready_read.
    """

    def __init__(self, workspace_path, parent=None):
        super().__init__(workspace_path, parent)
        self._master_fd = -1
        self._slave_fd = -1
        self._notifier = None
        self._child_pid = 0

    def start(self):
        import pty

        # Determine the shell to use (needed for the startup message)
        shell = os.environ.get("SHELL", "/bin/bash")

        # Allocate a new pseudo-terminal pair
        self._master_fd, self._slave_fd = pty.openpty()

        # Fork the child process
        self._child_pid = os.fork()
        if self._child_pid == 0:
            # CHILD: becomes session leader, slave fd becomes controlling terminal
            os.setsid()
            # Make the slave fd the controlling terminal
            try:
                import fcntl
                import termios
                fcntl.ioctl(self._slave_fd, termios.TIOCSCTTY, 0)
            except Exception:
                pass
            # Redirect stdin, stdout, stderr to the slave pty
            os.dup2(self._slave_fd, 0)
            os.dup2(self._slave_fd, 1)
            os.dup2(self._slave_fd, 2)
            # Close the master fd in the child
            os.close(self._master_fd)
            # Close the slave fd (dupped to 0,1,2)
            if self._slave_fd > 2:
                os.close(self._slave_fd)
            # Change to workspace directory
            os.chdir(self.workspace_path)
            # Execute the shell
            os.execvpe(shell, [shell, "-i"], os.environ)
            # If execvpe returns, it failed
            os._exit(1)

        # PARENT: close the slave fd, keep the master
        os.close(self._slave_fd)
        self._slave_fd = -1

        # Set the master fd to non-blocking
        import fcntl
        flags = fcntl.fcntl(self._master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self._master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        # Create a QSocketNotifier to watch the master fd for readability
        self._notifier = QSocketNotifier(self._master_fd, QSocketNotifier.Type.Read, self)
        self._notifier.activated.connect(self._on_ready_read)

        self._shell_started = True
        self.ready_read.emit(f"[MEDHĀ Terminal] {os.path.basename(shell)} started in {self.workspace_path}\n".encode("utf-8"))

    def _on_ready_read(self):
        try:
            data = os.read(self._master_fd, 4096)
            if data:
                self.ready_read.emit(data)
            else:
                # EOF — shell exited
                self._cleanup()
                self.finished.emit(0)
        except OSError as e:
            if e.errno == 5:  # EIO — happens when the slave side closes
                self._cleanup()
                self.finished.emit(0)
            else:
                self.error_occurred.emit(str(e))

    def write(self, data: bytes):
        if self._master_fd >= 0:
            try:
                os.write(self._master_fd, data)
            except OSError:
                pass  # Ignore write errors (shell may have exited)

    def send_signal(self, sig):
        """Ctrl+C → SIGINT to whatever is running in the FOREGROUND of the terminal.
        WHY not killpg(shell): with job control the shell puts each command (e.g. `sleep 30`, a C program
        stuck in a loop) in its OWN process group; signalling the shell's group only reached bash, which
        ignores SIGINT, so Ctrl+C did nothing (found in review, 2026-11-05). A real terminal does it by
        sending the interrupt character: the kernel's tty line discipline then signals the foreground
        group — exactly what we do here. Other signals go to the foreground group via tcgetpgrp()."""
        if self._master_fd < 0:
            return
        try:
            if sig == signal.SIGINT:
                os.write(self._master_fd, b"\x03")          # ^C → kernel delivers SIGINT to the foreground job
            else:
                os.killpg(os.tcgetpgrp(self._master_fd), sig)
        except OSError:
            pass

    def shutdown(self):
        if self._child_pid > 0:
            try:
                os.killpg(os.getpgid(self._child_pid), signal.SIGTERM)
            except OSError:
                pass
        self._cleanup()

    def _cleanup(self):
        if self._notifier:
            self._notifier.setEnabled(False)
            self._notifier.deleteLater()
            self._notifier = None
        if self._master_fd >= 0:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = -1
        if self._slave_fd >= 0:
            try:
                os.close(self._slave_fd)
            except OSError:
                pass
            self._slave_fd = -1
        self._shell_started = False


class _WindowsConPtyProcess(_PtyProcess):
    """
    Windows ConPTY backend using pywinpty.

    WHY ConPTY: Windows 10 1809+ introduced the ConPTY API (CreatePseudoConsole)
    which provides a real pseudo-console. pywinpty is a thin wrapper around it.
    This gives us proper terminal semantics (colours, Ctrl+C, line editing) on Windows.

    If pywinpty is not importable, we fall back to _QProcessFallback.
    """

    # Chunks read on the background reader thread are handed to the Qt (GUI)
    # thread through these signals — Qt queues them automatically because the
    # receiver lives in the GUI thread. WHY: winpty's read() BLOCKS until the
    # shell prints something, so it must never run on the GUI thread.
    _chunk = Signal(bytes)
    _eof = Signal()

    def __init__(self, workspace_path, parent=None):
        super().__init__(workspace_path, parent)
        self._pty = None
        self._process = None
        self._reader = None
        self._chunk.connect(self._on_chunk)         # reader thread → GUI thread (queued)
        self._eof.connect(self._on_eof)             # shell exited → finished signal

    def start(self):
        # The pip package is "pywinpty" but the importable module is "winpty".
        from winpty import PtyProcess
        import threading

        # Real ConPTY pseudo-console, 24 rows x 80 cols (winpty takes (rows, cols)).
        self._pty = PtyProcess.spawn(
            [os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe"), "/Q"],
            cwd=self.workspace_path,
            dimensions=(24, 80),
        )
        self._process = self._pty

        # Daemon thread: blocks on read(), forwards every chunk to the GUI thread.
        self._reader = threading.Thread(target=self._read_loop, name="medha-conpty-reader", daemon=True)
        self._reader.start()

        self._shell_started = True
        self.ready_read.emit("[MEDHĀ Terminal] cmd.exe started\n".encode("utf-8"))

    def _read_loop(self):
        # Runs on the reader thread. read() returns str; EOFError means the shell closed.
        pty = self._pty
        while pty is not None:
            try:
                data = pty.read(4096)
            except EOFError:
                logger.warning("ConPTY EOF: child_alive=%s exitstatus=%s", pty.isalive(), pty.exitstatus)
                break
            except Exception:
                logger.exception("ConPTY read failed")
                break
            if data:
                self._chunk.emit(data.encode("utf-8", errors="replace"))
        self._eof.emit()

    def _on_chunk(self, data: bytes):
        # GUI thread: pass the shell output on to the terminal widget.
        self.ready_read.emit(data)

    def _on_eof(self):
        # GUI thread: the shell process has ended.
        self._shell_started = False
        self.finished.emit(0)

    def write(self, data: bytes):
        if self._pty and self._pty.isalive():
            try:
                self._pty.write(data.decode("utf-8", errors="replace"))
            except Exception:
                logger.exception("ConPTY write failed")

    def send_signal(self, sig):
        # ConPTY has no Unix signals: Ctrl+C is sent as the ^C keystroke, which the
        # pseudo-console turns into CTRL_C_EVENT for the foreground program only.
        if sig == signal.SIGINT and self._pty and self._pty.isalive():
            try:
                self._pty.sendintr()
            except Exception:
                logger.exception("ConPTY Ctrl+C failed")

    def shutdown(self):
        if self._pty and self._pty.isalive():
            try:
                self._pty.terminate()
            except Exception:
                pass
        self._shell_started = False


class _QProcessFallback(_PtyProcess):
    """
    Fallback backend using QProcess (original behaviour).

    Used when:
      - pywinpty is not available on Windows
      - pty.openpty() fails on Unix (should not happen, but safety net)
    This retains the old behaviour so the IDE never loses terminal functionality.
    """

    def __init__(self, workspace_path, parent=None):
        super().__init__(workspace_path, parent)
        self._process = QProcess(self)
        self._process.setWorkingDirectory(self.workspace_path)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_error)

    def start(self):
        program, args = P.default_shell()
        self._process.start(program, args)
        # WHY: the widget queues typed commands until _shell_started is True.
        # Without this the fallback (no pywinpty) never ran any command.
        self._shell_started = True
        if P.IS_WINDOWS:
            # UTF-8 code page
            self._process.write(b"chcp 65001 >nul\r\n")

    def _on_stdout(self):
        data = self._process.readAllStandardOutput().data()
        self.ready_read.emit(data)

    def _on_stderr(self):
        data = self._process.readAllStandardError().data()
        self.ready_read.emit(data)

    def _on_finished(self, exit_code, exit_status):
        self._shell_started = False
        self.finished.emit(exit_code)

    def _on_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.error_occurred.emit("Could not start the system shell.")

    def write(self, data: bytes):
        self._process.write(data)

    def send_signal(self, sig):
        # WHAT: Ctrl+C stops the command running INSIDE the shell, not the shell.
        # HOW: a QProcess has no pseudo-terminal, so we find the shell's child
        # processes with psutil and terminate them; the shell itself survives
        # and prints its next prompt. If nothing is running, Ctrl+C is a no-op.
        if self._process.state() == QProcess.ProcessState.NotRunning:
            return
        try:
            import psutil
            children = psutil.Process(self._process.processId()).children(recursive=True)
        except Exception:
            logger.exception("Could not list terminal child processes")
            return
        for child in children:
            try:
                child.terminate()
            except Exception:
                pass  # already exited between listing and terminating
        if children:
            _, alive = psutil.wait_procs(children, timeout=1.0)
            for child in alive:
                try:
                    child.kill()
                except Exception:
                    pass

    def shutdown(self):
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            if not self._process.waitForFinished(1500):
                self._process.kill()
                self._process.waitForFinished(1000)


def _create_pty_backend(workspace_path, parent=None) -> _PtyProcess:
    """
    Factory: pick the best available backend for the current platform.

    Linux/macOS → _UnixPtyProcess (pty.openpty + QSocketNotifier)
    Windows     → _WindowsConPtyProcess if pywinpty importable, else _QProcessFallback
    """
    if P.IS_WINDOWS:
        try:
            import winpty  # module of the "pywinpty" package
            _ = winpty  # silence pyflakes "imported but unused"
            return _WindowsConPtyProcess(workspace_path, parent)
        except ImportError:
            # pywinpty not installed — fall back to QProcess
            return _QProcessFallback(workspace_path, parent)
    else:
        # Linux/macOS — pty.openpty should always be available
        try:
            import pty
            _ = pty  # silence pyflakes "imported but unused"
            return _UnixPtyProcess(workspace_path, parent)
        except ImportError:
            # Extremely unlikely, but fallback exists
            return _QProcessFallback(workspace_path, parent)


class IntegratedTerminalWidget(QWidget):
    command_executed = Signal(str)

    MAX_CHARS = 400_000   # keep memory bounded for programs that print forever

    def __init__(self, workspace_path=None, parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path or os.getcwd()
        self._pending_input = []
        self._terminal_text = TerminalText()
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

        # Create the pty backend
        self._pty = _create_pty_backend(self.workspace_path, self)
        self._pty.ready_read.connect(self._on_pty_output)
        self._pty.finished.connect(self._on_pty_finished)
        self._pty.error_occurred.connect(self._on_pty_error)
        self._pty.start()

        # Install event filter on input_line to catch Ctrl+C
        self.input_line.installEventFilter(self)

    # ------------------------------------------------------------ shell life
    def _on_pty_finished(self, exit_code):
        self.append_output(f"\n[shell exited with code {exit_code}]\n", color="#8b949e")
        self._pty._shell_started = False

    def _on_pty_error(self, msg):
        self.append_output(f"[MEDHĀ Terminal] {msg}\n", color="#f85149")

    def closeEvent(self, event):
        self.shutdown()
        super().closeEvent(event)

    def shutdown(self):
        self._pty.shutdown()

    def set_working_directory(self, folder):
        """Opening a new workspace also moves the shell there."""
        self.workspace_path = folder
        # Send a cd command to the shell
        quoted = f'cd /d "{folder}"' if P.IS_WINDOWS else f"cd '{folder}'"
        self._write_shell(quoted)

    # ---------------------------------------------------------------- output
    def _decode(self, data: bytes) -> str:
        return data.decode("utf-8", errors="replace")

    def _on_pty_output(self, data: bytes):
        self.append_output(self._terminal_text.feed(self._decode(data)))

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
        self._pty.write((text + newline).encode("utf-8"))

    def send_input(self):
        text = self.input_line.text()
        self.input_line.clear()
        # a running program (scanf / cin / input()) gets the line first
        if self.input_override is not None and self.input_override(text):
            self.append_output(text + "\n", color="#79c0ff")
            return
        if self._pty._shell_started:
            self.append_output(text + "\n", color="#79c0ff")
            self._write_shell(text)
            self.command_executed.emit(text)
        else:
            self._pending_input.append(text)
            # Shell not ready yet — will be sent when started

    def execute_command(self, cmd_string):
        if self._pty._shell_started:
            self.append_output(cmd_string + "\n", color="#79c0ff")
            self._write_shell(cmd_string)
        else:
            self._pending_input.append(cmd_string)

    # ---------------------------------------------------------------- Ctrl+C
    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent, Qt
        from PySide6.QtGui import QKeySequence
        if obj is self.input_line and event.type() == QEvent.Type.KeyPress:
            # Check for Ctrl+C FIRST (before Copy) — Ctrl+C must send SIGINT
            if event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Send SIGINT to the foreground process group (Unix) or Ctrl+C keystroke (Windows ConPTY)
                self._pty.send_signal(signal.SIGINT)
                self.append_output("^C\n", color="#f85149")
                return True  # Event handled
            # Allow standard Copy (Ctrl+Insert or Ctrl+C on some platforms) to pass through
            if event.matches(QKeySequence.StandardKey.Copy):
                return False  # Let the default copy handling proceed
        return super().eventFilter(obj, event)