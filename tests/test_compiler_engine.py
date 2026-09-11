import os
import tempfile
import pytest
from pathlib import Path
from medha.compiler_engine import DiagnosticIssue, UniversalCompilerEngine

def test_diagnostic_issue():
    issue = DiagnosticIssue("/path/to/file.c", "42", "10", "ERROR", "syntax error")
    assert issue.file_path == "/path/to/file.c"
    assert issue.line == 42
    assert issue.col == 10
    assert issue.severity == "error"
    assert issue.message == "syntax error"

def test_universal_compiler_engine_diagnostics_parser(qapp):
    engine = UniversalCompilerEngine()
    engine.active_file = "/workspace/main.c"

    sample_output = """
main.c:15:8: error: expected ';' before 'return'
main.c:20:12: warning: unused variable 'x'
    """
    engine._parse_diagnostics(sample_output)
    assert len(engine.diagnostics) == 2
    assert engine.diagnostics[0].line == 15
    assert engine.diagnostics[0].severity == "error"
    assert "expected" in engine.diagnostics[0].message
    assert engine.diagnostics[1].line == 20
    assert engine.diagnostics[1].severity == "warning"

def test_universal_compiler_engine_cancel(qapp):
    engine = UniversalCompilerEngine()
    engine.cancel()
    assert engine.stage == "idle"

def test_execute_file_validation(qapp):
    engine = UniversalCompilerEngine()
    finished_events = []
    engine.finished.connect(lambda code, diags, art: finished_events.append((code, diags, art)))

    # Missing file
    engine.execute_file("/non/existent/file.c")
    assert len(finished_events) == 1
    assert finished_events[0][0] == 1

    with tempfile.TemporaryDirectory() as tmpdir:
        # Unsupported file
        txt_file = Path(tmpdir) / "notes.txt"
        txt_file.write_text("hello")
        engine.execute_file(str(txt_file))
        assert len(finished_events) == 2
        assert finished_events[1][0] == 1

        # Python execution setup
        py_file = Path(tmpdir) / "script.py"
        py_file.write_text("print('test')\n")
        engine.execute_file(str(py_file))
        assert engine.stage == "run_binary"
        engine.cancel()

        # C execution setup
        c_file = Path(tmpdir) / "prog.c"
        c_file.write_text("int main() { return 0; }\n")
        engine.execute_file(str(c_file))
        assert engine.stage == "compile_c"
        engine.cancel()

def test_on_finished_transitions(qapp):
    engine = UniversalCompilerEngine()
    finished_calls = []
    engine.finished.connect(lambda c, d, a: finished_calls.append(c))

    # Stage transitions
    engine.stage = "compile_c"
    engine.artifact_path = "/bin/true"
    engine._on_finished(0, 0)
    assert engine.stage == "run_binary"
    engine.cancel()

    engine.stage = "compile_java"
    engine.active_file = "/tmp/App.java"
    engine._on_finished(0, 0)
    assert engine.stage == "run_binary"
    engine.cancel()

    engine.stage = "run_binary"
    engine._on_finished(0, 0)
    assert engine.stage == "idle"
    assert len(finished_calls) >= 1
