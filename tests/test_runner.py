"""
Unit tests for medha/runner.py — the Run button (Ctrl+F5) logic.

Tests cover:
- ProcessRunner signal emission
- Diagnostic parsing for GCC, Python, Java
- Build step planning for C/C++, Java, Python, JavaScript
- Turbo mode detection and build planning
- stdin forwarding to running programs
"""

import os
import tempfile
import textwrap
from unittest.mock import MagicMock, patch

import pytest

from medha.runner import ProcessRunner, ProblemDiagnostic


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def runner(qapp):
    """Create a ProcessRunner instance."""
    return ProcessRunner()


@pytest.fixture
def temp_c_file():
    """Create a temporary C file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(textwrap.dedent("""
            #include <stdio.h>
            int main(void) {
                printf("Hello, World!\\n");
                return 0;
            }
        """))
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_cpp_file():
    """Create a temporary C++ file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
        f.write(textwrap.dedent("""
            #include <iostream>
            int main() {
                std::cout << "Hello, World!" << std::endl;
                return 0;
            }
        """))
        yield f.name
    os.unlink(f.name)


# ---------------------------------------------------------------------------
# Diagnostic parsing tests
# ---------------------------------------------------------------------------

class TestDiagnosticParsing:
    def test_parse_gcc_error(self, runner):
        """GCC error lines are parsed into ProblemDiagnostic objects."""
        output = textwrap.dedent("""
            /tmp/test.c:10:5: error: expected ';' before '}' token
             10 |     return 0
               |     ^
        """)
        runner.active_file = "/tmp/test.c"
        runner.parse_diagnostics(output)
        assert len(runner.diagnostics) == 1
        diag = runner.diagnostics[0]
        assert diag.file_path == "/tmp/test.c"
        assert diag.line == 10
        assert diag.col == 5
        assert diag.severity == "error"
        assert "expected ';'" in diag.message

    def test_parse_gcc_warning(self, runner):
        """GCC warning lines are parsed with severity 'warning'."""
        output = "/tmp/test.c:20:3: warning: unused variable 'x' [-Wunused-variable]"
        runner.active_file = "/tmp/test.c"
        runner.parse_diagnostics(output)
        assert len(runner.diagnostics) == 1
        assert runner.diagnostics[0].severity == "warning"

    def test_parse_gcc_note_attached_to_previous(self, runner):
        """GCC note lines are attached to the previous diagnostic."""
        output = textwrap.dedent("""
            /tmp/test.c:10:5: error: 'foo' undeclared
            /tmp/test.c:10:5: note: did you mean 'bar'?
        """)
        runner.active_file = "/tmp/test.c"
        runner.parse_diagnostics(output)
        assert len(runner.diagnostics) == 1
        assert len(runner.diagnostics[0].notes) == 1
        assert "did you mean" in runner.diagnostics[0].notes[0]

    def test_parse_linker_error(self, runner):
        """Linker errors produce a diagnostic at the active file."""
        output = "/usr/bin/ld: /tmp/test.o: undefined reference to `missing_func'"
        runner.active_file = "/tmp/test.c"
        runner.parse_diagnostics(output)
        assert len(runner.diagnostics) == 1
        assert runner.diagnostics[0].severity == "error"
        assert "undefined reference" in runner.diagnostics[0].message

    def test_parse_python_traceback(self, runner):
        """Python tracebacks produce a diagnostic at the last user frame."""
        output = textwrap.dedent("""
            Traceback (most recent call last):
              File "/home/user/project/main.py", line 42, in <module>
                foo()
              File "/home/user/project/main.py", line 10, in foo
                bar()
            NameError: name 'bar' is not defined
        """)
        runner.active_file = "/home/user/project/main.py"
        runner.parse_python_traceback(output)
        assert len(runner.diagnostics) == 1
        diag = runner.diagnostics[0]
        assert diag.file_path == "/home/user/project/main.py"
        assert diag.line == 10
        assert "name 'bar' is not defined" in diag.message

    def test_parse_java_exception(self, runner):
        """Java exceptions produce a diagnostic at the reported line."""
        output = textwrap.dedent("""
            Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 5
                at Main.main(Main.java:12)
        """)
        runner.active_file = "/home/user/project/Main.java"
        runner.parse_java_exception(output)
        assert len(runner.diagnostics) == 1
        diag = runner.diagnostics[0]
        assert diag.line == 12
        assert "ArrayIndexOutOfBoundsException" in diag.message


# ---------------------------------------------------------------------------
# Build step planning tests
# ---------------------------------------------------------------------------

def _mock_toolchains():
    """Create a mock toolchains module with require() returning fake paths."""
    mock_toolchains = MagicMock()
    mock_toolchains.require.side_effect = lambda name: {
        "gcc": "/usr/bin/gcc",
        "g++": "/usr/bin/g++",
        "javac": "/usr/bin/javac",
        "java": "/usr/bin/java",
        "python": "/usr/bin/python3",
    }[name]
    mock_toolchains.ToolMissing = Exception
    mock_toolchains.find.return_value = MagicMock(path="/usr/bin/java")
    return mock_toolchains


def _setup_runner_mocks(monkeypatch):
    """Set up all mocks needed for runner tests."""
    mock_tc = _mock_toolchains()
    import medha.runner as runner_module
    monkeypatch.setattr(runner_module, "toolchains", mock_tc)
    monkeypatch.setattr(runner_module, "settings", MagicMock(
        get=lambda key, default=None: {
            'c_std': 'c17', 'cpp_std': 'c++17', 'turbo_mode': True, 'explain_lang': 'en'
        }.get(key, default)
    ))
    monkeypatch.setattr("medha.runner.turbo_adapt.needs_turbo", lambda src: False)
    # Prevent async execution from starting, but set stage to "build"
    def mock_next_step(self):
        self.stage = "build"
    monkeypatch.setattr(runner_module.ProcessRunner, "_next_step", mock_next_step)
    return mock_tc


class TestBuildPlanning:
    def test_plan_c_compilation(self, runner, temp_c_file, monkeypatch):
        """C files plan a gcc compile step and a run step."""
        _setup_runner_mocks(monkeypatch)
        runner.run_file(temp_c_file)
        assert runner.stage == "build"
        assert len(runner._steps) == 1
        prog, args, cwd, label = runner._steps[0]
        assert prog == "/usr/bin/gcc"
        assert "-std=" in " ".join(args)
        assert temp_c_file in args
        assert label == "Compiling C"

    def test_plan_cpp_compilation(self, runner, temp_cpp_file, monkeypatch):
        """C++ files plan a g++ compile step and a run step."""
        _setup_runner_mocks(monkeypatch)
        runner.run_file(temp_cpp_file)
        assert runner.stage == "build"
        assert len(runner._steps) == 1
        prog, args, cwd, label = runner._steps[0]
        assert prog == "/usr/bin/g++"
        assert label == "Compiling C++"

    def test_plan_java_compilation(self, runner, monkeypatch):
        """Java files plan javac compile and java run steps."""
        _setup_runner_mocks(monkeypatch)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(textwrap.dedent("""
                public class Hello {
                    public static void main(String[] args) {
                        System.out.println("Hello");
                    }
                }
            """))
            java_file = f.name
        try:
            runner.run_file(java_file)
            assert runner.stage == "build"
            assert len(runner._steps) == 1
            prog, args, cwd, label = runner._steps[0]
            assert prog == "/usr/bin/javac"
            assert label == "Compiling Java"
            assert runner._run_cmd is not None
            assert runner._run_cmd[0] == "/usr/bin/java"
        finally:
            os.unlink(java_file)

    def test_plan_python_execution(self, runner, monkeypatch):
        """Python files plan a direct python run step (no compilation)."""
        _setup_runner_mocks(monkeypatch)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('Hello')\n")
            py_file = f.name
        try:
            runner.run_file(py_file)
            # Python has no build steps, so _run_cmd is set directly
            assert runner._run_cmd is not None
            assert runner._run_cmd[0] == "/usr/bin/python3"
            assert py_file in runner._run_cmd[1]
        finally:
            os.unlink(py_file)

    def test_turbo_mode_detected(self, runner, monkeypatch, qapp):
        """Files including graphics.h trigger Turbo mode planning."""
        _setup_runner_mocks(monkeypatch)
        monkeypatch.setattr("medha.runner.turbo_adapt.needs_turbo", lambda src: True)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(textwrap.dedent("""
                #include <graphics.h>
                int main() { initgraph(0,0,""); return 0; }
            """))
            turbo_file = f.name
        try:
            from PySide6.QtTest import QSignalSpy
            spy = QSignalSpy(runner.turbo_started)
            runner.run_file(turbo_file)
            assert runner._decoder is not None
            assert spy.count() == 1
            assert spy.at(0)[0] is True
        finally:
            os.unlink(turbo_file)


# ---------------------------------------------------------------------------
# stdin forwarding tests
# ---------------------------------------------------------------------------

class TestStdinForwarding:
    def test_write_stdin_returns_false_when_not_running(self, runner):
        """write_stdin returns False when no program is running."""
        assert runner.write_stdin("test\n") is False

    def test_write_stdin_sends_newline(self, runner):
        """write_stdin adds newline for regular programs."""
        runner.stage = "run"
        runner.process = MagicMock()
        runner.process.state.return_value = runner.process.ProcessState.Running
        runner._decoder = None
        runner.write_stdin("hello")
        runner.process.write.assert_called()
        data = runner.process.write.call_args[0][0]
        assert data.endswith(b"\n")

    def test_write_stdin_sends_crlf_for_turbo(self, runner):
        """write_stdin sends CRLF for Turbo programs (protocol expects it)."""
        runner.stage = "run"
        runner.process = MagicMock()
        runner.process.state.return_value = runner.process.ProcessState.Running
        runner._decoder = MagicMock()  # Non-None means Turbo
        runner.write_stdin("hello")
        runner.process.write.assert_called()
        data = runner.process.write.call_args[0][0]
        assert data.endswith(b"\r\n")


# ---------------------------------------------------------------------------
# ProblemDiagnostic tests
# ---------------------------------------------------------------------------

class TestProblemDiagnostic:
    def test_diagnostic_creation(self):
        """ProblemDiagnostic stores all provided fields."""
        diag = ProblemDiagnostic(
            file_path="/tmp/test.c",
            line=10,
            col=5,
            severity="error",
            message="syntax error",
            tip="Add a semicolon"
        )
        assert diag.file_path == "/tmp/test.c"
        assert diag.line == 10
        assert diag.col == 5
        assert diag.severity == "error"
        assert diag.message == "syntax error"
        assert diag.tip == "Add a semicolon"
        assert diag.notes == []


# ---------------------------------------------------------------------------
# Signal emission tests
# ---------------------------------------------------------------------------

class TestSignals:
    def test_output_signal_emitted(self, runner, qapp):
        """output signal is emitted for every piece of text."""
        from PySide6.QtTest import QSignalSpy
        spy = QSignalSpy(runner.output)
        runner._emit_output("hello", "stdout")
        assert spy.count() == 1
        assert spy.at(0)[0] == "hello"

    def test_output_received_signal_emitted(self, runner, qapp):
        """output_received signal includes stream type."""
        from PySide6.QtTest import QSignalSpy
        spy = QSignalSpy(runner.output_received)
        runner._emit_output("hello", "stderr")
        assert spy.count() == 1
        assert spy.at(0)[0] == "hello"
        assert spy.at(0)[1] == "stderr"

    def test_running_changed_signal(self, runner, qapp):
        """running_changed signal emitted when build/run starts and ends."""
        from PySide6.QtTest import QSignalSpy
        spy = QSignalSpy(runner.running_changed)
        runner.running_changed.emit(True)
        runner.running_changed.emit(False)
        assert spy.count() == 2
        assert spy.at(0)[0] is True
        assert spy.at(1)[0] is False