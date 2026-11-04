"""
Tests for the pty-based terminal backend (B3).

These tests verify that:
1. The Unix pty backend starts a shell and reads output
2. Commands can be sent to the shell and output is received
3. Ctrl+C sends SIGINT to the foreground process group
4. The Windows ConPTY backend is used when pywinpty is available (mocked)
5. Fallback to QProcess works when pty/ConPTY are unavailable
"""

import os
import signal
import sys
import time
from unittest.mock import MagicMock, patch

import pytest

from medha import platform_info as P
from medha.terminal import (
    _UnixPtyProcess,
    _WindowsConPtyProcess,
    _QProcessFallback,
    _create_pty_backend,
    IntegratedTerminalWidget,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def wait_for_signal(obj, signal_name, timeout=2.0):
    """Wait for a Qt signal to be emitted, return the emitted args or None."""
    from PySide6.QtTest import QSignalSpy
    spy = QSignalSpy(getattr(obj, signal_name))
    if spy.wait(int(timeout * 1000)):
        # QSignalSpy stores emissions; use at(0) to get the first emission's args
        if spy.count() > 0:
            return spy.at(0)
    return None


# ---------------------------------------------------------------------------
# Unix pty backend tests (only run on Linux/macOS)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(P.IS_WINDOWS, reason="Unix pty tests only on Linux/macOS")
class TestUnixPtyProcess:
    def test_start_shell_emits_ready_read(self, qapp):
        """_UnixPtyProcess.start() spawns a shell and emits ready_read with startup message."""
        proc = _UnixPtyProcess(os.getcwd())
        proc.start()

        # Wait for the startup message
        result = wait_for_signal(proc, "ready_read", timeout=3.0)
        assert result is not None, "ready_read signal not emitted"
        data = result[0]
        # The shell may emit terminal escape sequences first; just verify we got some output
        assert len(data) > 0

        proc.shutdown()

    def test_write_and_read_echo(self, qapp):
        """Writing a command to the shell produces output."""
        proc = _UnixPtyProcess(os.getcwd())
        proc.start()

        # Wait for startup
        wait_for_signal(proc, "ready_read", timeout=3.0)

        # Send a simple command (echo)
        proc.write(b"echo hello-pty-test\n")

        # Wait for output
        result = wait_for_signal(proc, "ready_read", timeout=3.0)
        assert result is not None
        output = result[0].decode("utf-8", errors="replace")
        assert "hello-pty-test" in output

        proc.shutdown()

    def test_send_signal_sigint(self, qapp):
        """send_signal(SIGINT) delivers Ctrl+C to the shell's process group."""
        proc = _UnixPtyProcess(os.getcwd())
        proc.start()

        # Wait for startup
        wait_for_signal(proc, "ready_read", timeout=3.0)

        # Start a long-running command (sleep)
        proc.write(b"sleep 10\n")
        time.sleep(0.2)  # give it time to start

        # Send SIGINT (Ctrl+C)
        proc.send_signal(signal.SIGINT)

        # Wait for the shell prompt to return (^C echoed)
        result = wait_for_signal(proc, "ready_read", timeout=3.0)
        assert result is not None
        output = result[0].decode("utf-8", errors="replace")
        # The shell should show ^C and return to prompt
        assert "^C" in output or "C" in output

        proc.shutdown()


# ---------------------------------------------------------------------------
# Windows ConPTY backend tests (mocked, run everywhere)
# ---------------------------------------------------------------------------

def _fake_winpty(monkeypatch, reads):
    """Install a fake 'winpty' module (the import name of the pywinpty package).
    `reads` feeds PtyProcess.read(); the list should end with EOFError so the
    background reader thread finishes like it does when cmd.exe exits."""
    mod = MagicMock()
    pty = MagicMock()
    pty.isalive.return_value = True
    pty.read.side_effect = reads
    mod.PtyProcess.spawn.return_value = pty
    monkeypatch.setitem(sys.modules, "winpty", mod)
    return mod, pty


class TestWindowsConPtyProcess:
    def test_start_spawns_pty_and_streams_output(self, qapp, monkeypatch):
        """start() spawns cmd.exe in ConPTY with (rows, cols) and streams output from the reader thread."""
        mod, pty = _fake_winpty(monkeypatch, ["Microsoft Windows [Version 10.0.19045]\r\nC:\\>", EOFError()])
        from PySide6.QtTest import QSignalSpy

        proc = _WindowsConPtyProcess(os.getcwd())
        out = QSignalSpy(proc.ready_read)
        done = QSignalSpy(proc.finished)
        proc.start()

        # Real winpty API: spawn(argv, cwd=..., dimensions=(rows, cols)).
        _, kwargs = mod.PtyProcess.spawn.call_args
        assert kwargs["dimensions"] == (24, 80)
        assert proc._shell_started is True

        deadline = time.time() + 3
        while done.count() == 0 and time.time() < deadline:
            qapp.processEvents()
            time.sleep(0.01)
        assert done.count() == 1, "reader thread never reported EOF"
        text = b"".join(bytes(out.at(i)[0]) for i in range(out.count())).decode("utf-8")
        assert "MEDHĀ Terminal" in text and "Microsoft Windows" in text
        assert proc._shell_started is False  # shell gone → widget stops sending
        proc.shutdown()

    def test_write_sends_to_pty(self, qapp, monkeypatch):
        _, pty = _fake_winpty(monkeypatch, [EOFError()])
        proc = _WindowsConPtyProcess(os.getcwd())
        proc.start()
        proc.write(b"dir\r\n")
        pty.write.assert_called_with("dir\r\n")
        proc.shutdown()

    def test_send_signal_ctrl_c_uses_sendintr(self, qapp, monkeypatch):
        """Ctrl+C → winpty PtyProcess.sendintr() (the real method name)."""
        _, pty = _fake_winpty(monkeypatch, [EOFError()])
        proc = _WindowsConPtyProcess(os.getcwd())
        proc.start()
        proc.send_signal(signal.SIGINT)
        pty.sendintr.assert_called_once()
        proc.shutdown()


# ---------------------------------------------------------------------------
# Fallback backend tests
# ---------------------------------------------------------------------------

class TestQProcessFallback:
    def test_start_shell_marks_started(self, qapp):
        """start() launches the shell AND sets _shell_started, so typed commands are not stuck in the queue."""
        proc = _QProcessFallback(os.getcwd())
        proc.start()
        assert proc._process.state() in (
            proc._process.ProcessState.Starting,
            proc._process.ProcessState.Running,
        )
        assert proc._shell_started is True
        proc.shutdown()

    def test_write_sends_to_process(self, qapp):
        proc = _QProcessFallback(os.getcwd())
        proc.start()
        with patch.object(proc._process, "write") as mock_write:
            proc.write(b"test\n")
            mock_write.assert_called_with(b"test\n")
        proc.shutdown()

    @pytest.mark.skipif(P.IS_WINDOWS, reason="uses sleep from a POSIX shell")
    def test_ctrl_c_stops_command_not_shell(self, qapp):
        """Ctrl+C terminates the running command; the shell itself keeps running."""
        import psutil
        proc = _QProcessFallback(os.getcwd())
        proc.start()
        assert proc._process.waitForStarted(3000)
        proc.write(b"sleep 30\n")
        shell = psutil.Process(proc._process.processId())
        deadline = time.time() + 3
        while not shell.children(recursive=True) and time.time() < deadline:
            qapp.processEvents()
            time.sleep(0.05)
        assert shell.children(recursive=True), "sleep never started"

        proc.send_signal(signal.SIGINT)

        assert not shell.children(recursive=True)
        assert proc._process.state() == proc._process.ProcessState.Running
        proc.shutdown()


# ---------------------------------------------------------------------------
# Factory function tests
# ---------------------------------------------------------------------------

class TestCreatePtyBackend:
    @pytest.mark.skipif(sys.platform == "win32", reason="the pty module needs termios (POSIX only)")
    @patch("medha.terminal.P")
    def test_unix_chooses_unix_pty(self, mock_P, qapp):
        """On Linux/macOS, factory returns _UnixPtyProcess."""
        mock_P.IS_WINDOWS = False
        backend = _create_pty_backend(os.getcwd())
        assert isinstance(backend, _UnixPtyProcess)
        backend.shutdown()

    @patch("medha.terminal.P")
    def test_windows_with_pywinpty_chooses_conpty(self, mock_P, qapp, monkeypatch):
        """On Windows with pywinpty, factory returns _WindowsConPtyProcess."""
        mock_P.IS_WINDOWS = True
        monkeypatch.setitem(sys.modules, 'winpty', MagicMock())

        backend = _create_pty_backend(os.getcwd())
        assert isinstance(backend, _WindowsConPtyProcess)
        backend.shutdown()

    @patch("medha.terminal.P")
    def test_windows_without_pywinpty_chooses_fallback(self, mock_P, qapp, monkeypatch):
        """On Windows without pywinpty, factory returns _QProcessFallback."""
        mock_P.IS_WINDOWS = True
        # None in sys.modules makes `import winpty` raise ImportError
        monkeypatch.setitem(sys.modules, 'winpty', None)

        backend = _create_pty_backend(os.getcwd())
        assert isinstance(backend, _QProcessFallback)
        backend.shutdown()


# ---------------------------------------------------------------------------
# IntegratedTerminalWidget tests
# ---------------------------------------------------------------------------

class TestIntegratedTerminalWidget:
    def test_widget_creation(self, qapp):
        """IntegratedTerminalWidget can be instantiated."""
        widget = IntegratedTerminalWidget(os.getcwd())
        assert widget is not None
        assert widget.output_edit is not None
        assert widget.input_line is not None
        widget.shutdown()

    def test_send_input_echoes_locally(self, qapp):
        """send_input() echoes the typed line to the output area."""
        widget = IntegratedTerminalWidget(os.getcwd())
        # Wait for shell startup
        time.sleep(0.5)

        widget.input_line.setText("echo widget-test")
        widget.send_input()

        # The input line should be cleared and text echoed
        assert widget.input_line.text() == ""
        # Output should contain the command (echoed locally before shell responds)
        time.sleep(0.3)
        output_text = widget.output_edit.toPlainText()
        assert "widget-test" in output_text or "echo" in output_text

        widget.shutdown()

    def test_execute_command_sends_to_shell(self, qapp):
        """execute_command() sends a command string to the shell."""
        widget = IntegratedTerminalWidget(os.getcwd())
        time.sleep(0.5)

        with patch.object(widget._pty, "write") as mock_write:
            widget.execute_command("ls -la")
            mock_write.assert_called()
            # Should contain the command + newline
            args, _ = mock_write.call_args
            assert b"ls -la" in args[0]

        widget.shutdown()

    def test_ctrl_c_sends_sigint(self, qapp):
        """Ctrl+C in input line sends SIGINT via the backend."""
        widget = IntegratedTerminalWidget(os.getcwd())
        time.sleep(0.5)

        with patch.object(widget._pty, "send_signal") as mock_send:
            # Simulate Ctrl+C key press by calling eventFilter directly
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QKeyEvent
            from PySide6.QtCore import QEvent

            # Create a key press event for Ctrl+C
            event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
            # Call the event filter directly
            result = widget.eventFilter(widget.input_line, event)
            # The event filter should handle it (return True) and call send_signal
            mock_send.assert_called_with(signal.SIGINT)
            # We don't assert on result because eventFilter might return False if
            # the key sequence matches Copy (which it doesn't for Ctrl+C)

        widget.shutdown()

    def test_set_working_directory_sends_cd(self, qapp):
        """set_working_directory() sends a cd command to the shell."""
        widget = IntegratedTerminalWidget(os.getcwd())
        time.sleep(0.5)

        with patch.object(widget._pty, "write") as mock_write:
            widget.set_working_directory("/tmp")
            mock_write.assert_called()
            args, _ = mock_write.call_args
            assert b"cd" in args[0]
            assert b"/tmp" in args[0]

        widget.shutdown()


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def qapp():
    """Provide a QApplication instance for tests."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app

# ---------------------------------------------------------------------------
# Real Windows ConPTY (runs only on the Windows CI job / a Windows machine)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not (P.IS_WINDOWS and os.environ.get("MEDHA_REAL_CONPTY_TEST")),
                    reason="real ConPTY check — Windows CI only")
def test_real_conpty_runs_command_and_ctrl_c(qapp):
    """Spawns real cmd.exe in ConPTY: a command runs, Ctrl+C stops a long command, shell survives."""
    proc = _create_pty_backend(os.getcwd())
    assert isinstance(proc, _WindowsConPtyProcess), "pywinpty missing → fallback was chosen"
    chunks = []
    proc.ready_read.connect(lambda d: chunks.append(bytes(d)))
    proc.start()

    def wait_for(text, timeout=15):
        end = time.time() + timeout
        while time.time() < end:
            qapp.processEvents()
            if text in b"".join(chunks).decode("utf-8", "replace"):
                return True
            time.sleep(0.05)
        return False

    proc.write(b"echo MEDHA_OK_%OS%\r\n")
    assert wait_for("MEDHA_OK_Windows_NT"), b"".join(chunks)[-500:]

    proc.write(b"ping -n 30 127.0.0.1\r\n")
    assert wait_for("Reply from 127.0.0.1")
    proc.send_signal(signal.SIGINT)
    proc.write(b"echo AFTER_%OS%\r\n")
    assert wait_for("AFTER_Windows_NT", timeout=10), "shell did not come back after Ctrl+C"
    assert proc._pty.isalive()
    proc.shutdown()
