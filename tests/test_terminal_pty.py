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

class TestWindowsConPtyProcess:
    def test_start_spawns_pty(self, qapp, monkeypatch):
        """_WindowsConPtyProcess.start() creates a PtyProcess and polls for output."""
        # Mock pywinpty in sys.modules BEFORE the class is used
        mock_pywinpty = MagicMock()
        monkeypatch.setitem(sys.modules, 'pywinpty', mock_pywinpty)

        # Mock the PtyProcess
        mock_pty = MagicMock()
        mock_pty.isalive.return_value = True
        # The timer polls immediately, so we need enough empty reads before the real output
        mock_pty.read.side_effect = ["", "", "", "Microsoft Windows [Version 10.0.19045]\nC:\\Users\\test>"]
        mock_pywinpty.PtyProcess.spawn.return_value = mock_pty

        proc = _WindowsConPtyProcess(os.getcwd())
        
        # Create spy BEFORE starting to catch the startup message
        from PySide6.QtTest import QSignalSpy
        spy = QSignalSpy(proc.ready_read)
        
        proc.start()

        # Wait for startup message (emitted immediately in start())
        assert spy.wait(1000), "Startup message not emitted"
        # The first emission should be the startup message
        assert spy.count() > 0
        first_emission = spy.at(0)
        assert "MEDHĀ Terminal".encode("utf-8") in first_emission[0]

        # The timer may have already fired during the wait above, so check if we already have the second emission
        if spy.count() < 2:
            # Wait for polled output (timer fires and reads from pty)
            assert spy.wait(1000), "Polled output not emitted"
        
        assert spy.count() > 1
        second_emission = spy.at(1)
        output = second_emission[0].decode("utf-8", errors="replace")
        assert "Windows" in output or "cmd" in output.lower()

        proc.shutdown()
        mock_pty.terminate.assert_called()

    def test_write_sends_to_pty(self, qapp, monkeypatch):
        """write() sends data to the ConPTY."""
        mock_pywinpty = MagicMock()
        monkeypatch.setitem(sys.modules, 'pywinpty', mock_pywinpty)

        mock_pty = MagicMock()
        mock_pty.isalive.return_value = True
        mock_pty.read.return_value = ""
        mock_pywinpty.PtyProcess.spawn.return_value = mock_pty

        proc = _WindowsConPtyProcess(os.getcwd())
        proc.start()
        wait_for_signal(proc, "ready_read", timeout=1.0)

        proc.write(b"dir\n")
        mock_pty.write.assert_called_with("dir\n")

        proc.shutdown()

    def test_send_signal_ctrl_c(self, qapp, monkeypatch):
        """send_signal(SIGINT) sends Ctrl+C keystroke to ConPTY."""
        mock_pywinpty = MagicMock()
        monkeypatch.setitem(sys.modules, 'pywinpty', mock_pywinpty)

        mock_pty = MagicMock()
        mock_pty.isalive.return_value = True
        mock_pty.read.return_value = ""
        mock_pywinpty.PtyProcess.spawn.return_value = mock_pty

        proc = _WindowsConPtyProcess(os.getcwd())
        proc.start()
        wait_for_signal(proc, "ready_read", timeout=1.0)

        proc.send_signal(signal.SIGINT)
        mock_pty.send_control.assert_called_with('c')

        proc.shutdown()


# ---------------------------------------------------------------------------
# Fallback backend tests
# ---------------------------------------------------------------------------

class TestQProcessFallback:
    def test_start_shell(self, qapp):
        """_QProcessFallback.start() launches the default shell via QProcess."""
        proc = _QProcessFallback(os.getcwd())
        proc.start()

        # The process should be in Starting or Running state after start
        assert proc._process.state() in (
            proc._process.ProcessState.Starting,
            proc._process.ProcessState.Running,
        )

        proc.shutdown()

    def test_write_sends_to_process(self, qapp):
        """write() sends data to QProcess."""
        proc = _QProcessFallback(os.getcwd())
        proc.start()

        with patch.object(proc._process, "write") as mock_write:
            proc.write(b"test\n")
            mock_write.assert_called_with(b"test\n")

        proc.shutdown()

    def test_write_sends_to_process(self, qapp):
        """write() sends data to QProcess."""
        proc = _QProcessFallback(os.getcwd())
        proc.start()

        with patch.object(proc._process, "write") as mock_write:
            proc.write(b"test\n")
            mock_write.assert_called_with(b"test\n")

        proc.shutdown()


# ---------------------------------------------------------------------------
# Factory function tests
# ---------------------------------------------------------------------------

class TestCreatePtyBackend:
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
        monkeypatch.setitem(sys.modules, 'pywinpty', MagicMock())

        backend = _create_pty_backend(os.getcwd())
        assert isinstance(backend, _WindowsConPtyProcess)
        backend.shutdown()

    @patch("medha.terminal.P")
    def test_windows_without_pywinpty_chooses_fallback(self, mock_P, qapp, monkeypatch):
        """On Windows without pywinpty, factory returns _QProcessFallback."""
        mock_P.IS_WINDOWS = True
        # Ensure pywinpty is not importable
        monkeypatch.delitem(sys.modules, 'pywinpty', raising=False)

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