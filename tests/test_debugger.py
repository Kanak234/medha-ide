"""
Unit tests for medha/debugger.py — DebugSession (GDB MI2 + debugpy/DAP).

Tests cover:
- DebugSession initialization
- GDB MI2 command/response handling
- DAP protocol message framing
- Breakpoint setting (GDB and debugpy)
- Program execution control (run, continue, wait_for_stop)
- Variable evaluation
- Clean termination
"""

import os
import json
import socket
import time
from unittest.mock import MagicMock, patch, call

import pytest

from medha.debugger import DebugSession


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_gdb_proc():
    """Create a mock GDB process."""
    proc = MagicMock()
    proc.poll.return_value = None  # Still running
    proc.stdin = MagicMock()
    proc.stdout = MagicMock()
    return proc


@pytest.fixture
def mock_dap_socket():
    """Create a mock DAP socket."""
    sock = MagicMock()
    return sock


# ---------------------------------------------------------------------------
# GDB MI2 tests
# ---------------------------------------------------------------------------

class TestDebugSessionGDB:
    @patch("medha.toolchains.find")
    @patch("medha.debugger.subprocess.Popen")
    def test_gdb_start_spawns_process(self, mock_popen, mock_find, tmp_path):
        """DebugSession.start() spawns gdb with MI2 interpreter."""
        mock_find.return_value = MagicMock(path="/usr/bin/gdb")
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.stdin = MagicMock()
        mock_proc.stdout = MagicMock()
        mock_proc.stdout.readline.side_effect = [
            "=thread-group-added,id=\"i1\"\n",
            "(gdb)\n"
        ]
        mock_popen.return_value = mock_proc

        target = tmp_path / "test_program"
        target.write_text("")

        session = DebugSession(str(target), kind="gdb")
        session.start()

        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert args[0] == "/usr/bin/gdb"
        assert "--interpreter=mi2" in args
        assert str(target) in args
        assert session.proc is mock_proc

    def test_send_gdb_cmd_writes_and_reads(self, mock_gdb_proc):
        """_send_gdb_cmd() writes command and reads until prompt."""
        mock_gdb_proc.stdout.readline.side_effect = [
            "^done,bkpt={number=\"1\",type=\"breakpoint\",disp=\"keep\",enabled=\"y\",addr=\"0x00401136\",func=\"main\",file=\"test.c\",line=\"10\"}\n",
            "(gdb)\n"
        ]

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session._send_gdb_cmd("-break-insert test.c:10")

        mock_gdb_proc.stdin.write.assert_called_with("-break-insert test.c:10\n")
        assert "^done" in result
        assert "bkpt=" in result

    def test_set_breakpoint_gdb_returns_true_on_success(self, mock_gdb_proc):
        """set_breakpoint() returns True when GDB reports ^done."""
        mock_gdb_proc.stdout.readline.side_effect = [
            "^done,bkpt={number=\"1\"}\n",
            "(gdb)\n"
        ]

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session.set_breakpoint("/tmp/test.c", 10)

        assert result is True
        mock_gdb_proc.stdin.write.assert_called()

    def test_set_breakpoint_gdb_returns_false_on_error(self, mock_gdb_proc):
        """set_breakpoint() returns False when GDB reports error."""
        mock_gdb_proc.stdout.readline.side_effect = [
            "^error,msg=\"No symbol table is loaded\"\n",
            "(gdb)\n"
        ]

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session.set_breakpoint("/tmp/test.c", 10)

        assert result is False

    def test_run_gdb_sends_exec_run(self, mock_gdb_proc):
        """run() sends -exec-run to GDB."""
        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        session.run()
        mock_gdb_proc.stdin.write.assert_called_with("-exec-run\n")

    def test_wait_for_stop_gdb_detects_stopped(self, mock_gdb_proc):
        """wait_for_stop() returns True when *stopped record received."""
        mock_gdb_proc.stdout.readline.side_effect = [
            "*stopped,reason=\"breakpoint-hit\",thread-id=\"1\"\n",
            "(gdb)\n"
        ]

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session.wait_for_stop(timeout=1.0)

        assert result is True
        assert session.stopped is True

    def test_wait_for_stop_gdb_timeout_returns_false(self, mock_gdb_proc):
        """wait_for_stop() returns False on timeout."""
        mock_gdb_proc.stdout.readline.return_value = ""  # No output

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session.wait_for_stop(timeout=0.1)

        assert result is False

    def test_evaluate_gdb_parses_value(self, mock_gdb_proc):
        """evaluate() extracts value from GDB response."""
        mock_gdb_proc.stdout.readline.side_effect = [
            '^done,value="42"\n',
            "(gdb)\n"
        ]

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session.evaluate("my_var")

        assert result == "42"

    def test_evaluate_gdb_returns_raw_on_no_match(self, mock_gdb_proc):
        """evaluate() returns raw response when value pattern not found."""
        # Response without value="..." pattern
        mock_gdb_proc.stdout.readline.side_effect = [
            "^done,some_other_data\n",
            "(gdb)\n"
        ]

        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        result = session.evaluate("complex_expr")

        assert "some_other_data" in result

    def test_continue_gdb_sends_exec_continue(self, mock_gdb_proc):
        """continue_() sends -exec-continue to GDB."""
        mock_gdb_proc.stdout.readline.side_effect = [
            "(gdb)\n"
        ]
        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        session.continue_()
        mock_gdb_proc.stdin.write.assert_called_with("-exec-continue\n")

    def test_terminate_gdb_sends_exit_and_terminates(self, mock_gdb_proc):
        """terminate() asks GDB to exit and terminates process."""
        session = DebugSession("/tmp/test", kind="gdb")
        session.proc = mock_gdb_proc
        session.terminate()

        mock_gdb_proc.stdin.write.assert_called_with("-gdb-exit\n")
        mock_gdb_proc.terminate.assert_called_once()
        assert session.proc is None


# ---------------------------------------------------------------------------
# debugpy/DAP tests
# ---------------------------------------------------------------------------

class TestDebugSessionDebugpy:
    @patch("medha.toolchains.find")
    @patch("medha.debugger.subprocess.Popen")
    @patch("socket.socket")
    def test_debugpy_start_binds_socket_and_connects(self, mock_socket_class, mock_popen, mock_find, tmp_path):
        """DebugSession.start() for debugpy binds socket, spawns adapter, and connects."""
        mock_find.return_value = MagicMock(path="/usr/bin/python3")
        
        # Mock socket
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ("127.0.0.1", 12345)
        mock_socket_class.return_value = mock_sock

        # Mock debugpy process
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        # Mock DAP connection socket
        mock_dap_sock = MagicMock()
        mock_socket_class.side_effect = [mock_sock, mock_dap_sock]  # First for bind, second for connect

        # Mock DAP responses
        mock_dap_sock.recv.side_effect = [
            b"Content-Length: 2\n\r\n{}",  # initialize response
            b"Content-Length: 2\n\r\n{}",  # attach response
        ]

        target = tmp_path / "test.py"
        target.write_text("print('hello')")

        session = DebugSession(str(target), kind="debugpy")
        session.start()

        # Verify socket bind
        mock_sock.bind.assert_called_with(('127.0.0.1', 0))
        mock_sock.close.assert_called()  # Socket is closed after getting port

        # Verify debugpy spawned
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert "/usr/bin/python3" in args[0]
        assert "-m" in args
        assert "debugpy" in args
        assert "--listen" in " ".join(args)
        assert "--wait-for-client" in args
        assert str(target) in args

        # Verify DAP initialize and attach sent
        assert mock_dap_sock.sendall.called

    def test_send_dap_request_formats_correctly(self):
        """send_dap_request() formats DAP request with Content-Length header."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.req_seq = 0

        seq = session.send_dap_request("initialize", {"clientID": "test"})

        assert seq == 1
        session.sock.sendall.assert_called_once()
        sent_data = session.sock.sendall.call_args[0][0]
        assert b"Content-Length:" in sent_data
        assert b"initialize" in sent_data
        assert b"clientID" in sent_data

    def test_read_dap_response_parses_content_length(self):
        """read_dap_response() parses Content-Length header and reads body."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        
        # Simulate receiving a complete response in one chunk
        response = json.dumps({"seq": 1, "type": "response", "request_seq": 1, "success": True})
        header = f"Content-Length: {len(response)}\r\n\r\n"
        full = header.encode() + response.encode()
        
        session.sock.recv.return_value = full

        result = session.read_dap_response(target_seq=1, timeout=1.0)

        assert result["request_seq"] == 1
        assert result["success"] is True

    def test_read_dap_response_handles_stopped_event(self):
        """read_dap_response() sets stopped=True on 'stopped' event."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        
        event = json.dumps({"seq": 1, "type": "event", "event": "stopped", "body": {"threadId": 2}})
        header = f"Content-Length: {len(event)}\r\n\r\n"
        full = header.encode() + event.encode()
        
        session.sock.recv.return_value = full

        result = session.read_dap_response(timeout=1.0)

        assert session.stopped is True
        assert session.stopped_thread_id == 2

    def test_set_breakpoint_debugpy_sends_setBreakpoints(self):
        """set_breakpoint() sends setBreakpoints request for debugpy."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.req_seq = 5
        session.send_dap_request = MagicMock(return_value=6)
        
        # Mock read_dap_response to return verified breakpoint
        with patch.object(session, "read_dap_response") as mock_read:
            mock_read.return_value = {
                "request_seq": 6,
                "body": {"breakpoints": [{"verified": True}]}
            }
            result = session.set_breakpoint("/tmp/test.py", 42)

            assert result is True
            # Verify send_dap_request was called with correct arguments
            session.send_dap_request.assert_called_once()
            args = session.send_dap_request.call_args[0]
            assert args[0] == "setBreakpoints"
            assert args[1]["source"]["path"] == os.path.abspath("/tmp/test.py")
            assert args[1]["breakpoints"][0]["line"] == 42

    def test_set_breakpoint_debugpy_fails_on_unverified(self):
        """set_breakpoint() returns False when breakpoint not verified."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.req_seq = 5

        with patch.object(session, "read_dap_response") as mock_read:
            mock_read.return_value = {
                "request_seq": 6,
                "body": {"breakpoints": [{"verified": False}]}
            }
            result = session.set_breakpoint("/tmp/test.py", 42)
            assert result is False

    def test_run_debugpy_sends_configurationDone(self):
        """run() sends configurationDone for debugpy."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.send_dap_request = MagicMock()

        session.run()

        session.send_dap_request.assert_called_with("configurationDone")

    def test_wait_for_stop_debugpy_fetches_stack_trace(self):
        """wait_for_stop() fetches stack trace to get frameId after stop."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.stopped = True
        session.stopped_thread_id = 1
        session.send_dap_request = MagicMock(return_value=10)
        
        with patch.object(session, "read_dap_response") as mock_read:
            # First call returns stackTrace response
            mock_read.side_effect = [
                {"request_seq": 10, "body": {"stackFrames": [{"id": 100, "name": "main"}]}},
                {}  # Subsequent calls
            ]
            result = session.wait_for_stop(timeout=1.0)

            assert result is True
            assert session.frame_id == 100
            session.send_dap_request.assert_called_with("stackTrace", {"threadId": 1})

    def test_evaluate_debugpy_uses_frame_id(self):
        """evaluate() includes frameId when available."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.frame_id = 100
        session.send_dap_request = MagicMock(return_value=20)
        session.read_dap_response = MagicMock(return_value={"body": {"result": "42"}})

        result = session.evaluate("my_var")

        assert result == "42"
        session.send_dap_request.assert_called()
        args = session.send_dap_request.call_args[0]
        assert args[0] == "evaluate"
        assert args[1]["frameId"] == 100

    def test_continue_debugpy_sends_continue(self):
        """continue_() sends continue request with threadId."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        session.stopped_thread_id = 1
        session.send_dap_request = MagicMock()

        session.continue_()

        session.send_dap_request.assert_called_with("continue", {"threadId": 1})

    def test_terminate_debugpy_disconnects_and_terminates(self):
        """terminate() sends disconnect, closes socket, terminates process."""
        session = DebugSession("/tmp/test", kind="debugpy")
        session.sock = MagicMock()
        mock_proc = MagicMock()
        session.proc = mock_proc
        session.send_dap_request = MagicMock()

        session.terminate()

        session.send_dap_request.assert_called_with("disconnect")
        session.sock.close.assert_called_once()
        mock_proc.terminate.assert_called_once()
        assert session.proc is None


# ---------------------------------------------------------------------------
# Common tests
# ---------------------------------------------------------------------------

class TestDebugSessionCommon:
    def test_init_sets_attributes(self):
        """DebugSession.__init__ sets target path and kind."""
        session = DebugSession("/tmp/test", kind="gdb")
        assert session.target == os.path.abspath("/tmp/test")
        assert session.kind == "gdb"
        assert session.proc is None
        assert session.sock is None
        assert session.stopped is False
        assert session.req_seq == 0

    def test_init_normalizes_kind(self):
        """DebugSession normalizes kind to lowercase."""
        session = DebugSession("/tmp/test", kind="GDB")
        assert session.kind == "gdb"

        session = DebugSession("/tmp/test", kind="DebugPy")
        assert session.kind == "debugpy"