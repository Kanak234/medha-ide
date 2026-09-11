import os
import tempfile
from pathlib import Path
from medha.analyzers.linter import SafetyDiagnostic, StaticAnalyzerEngine, SafetyDiagnosticsPanelWidget

def test_safety_diagnostic():
    diag = SafetyDiagnostic("foo.c", "12", "WARNING", "cppcheck", "Resource leak: fp")
    assert diag.file_path == "foo.c"
    assert diag.line == 12
    assert diag.severity == "warning"
    assert diag.tool == "cppcheck"
    assert diag.message == "Resource leak: fp"

def test_static_analyzer_engine_parsing(qapp):
    engine = StaticAnalyzerEngine()

    engine.active_tool = "cppcheck"
    cppcheck_text = "test.c:25:warning:Memory leak: ptr\nmain.c:10:error:Array index out of bounds\n"
    engine._parse_output(cppcheck_text)
    assert len(engine.diagnostics) == 2
    assert engine.diagnostics[0].tool == "cppcheck"
    assert engine.diagnostics[0].line == 25
    assert engine.diagnostics[0].message == "Memory leak: ptr"

    engine.diagnostics = []
    engine.active_tool = "clang-tidy"
    clang_tidy_text = "test.c:30:5: warning: implicit conversion loses integer precision [clang-diagnostic-conversion]\n"
    engine._parse_output(clang_tidy_text)
    assert len(engine.diagnostics) == 1
    assert engine.diagnostics[0].tool == "clang-tidy"
    assert engine.diagnostics[0].line == 30

def test_static_analyzer_engine_analyze_file(qapp):
    engine = StaticAnalyzerEngine()
    # Non-existent file does nothing
    engine.analyze_file("/does/not/exist.c")
    assert engine.active_file == ""

    with tempfile.TemporaryDirectory() as tmpdir:
        c_file = Path(tmpdir) / "test.c"
        c_file.write_text("int main() { return 0; }\n")
        engine.analyze_file(str(c_file))
        assert engine.active_file == str(c_file)
        engine._on_finished(0, 0)

def test_safety_diagnostics_panel_widget(qapp):
    panel = SafetyDiagnosticsPanelWidget()
    diags = [
        SafetyDiagnostic("foo.c", 10, "error", "cppcheck", "Critical bug"),
        SafetyDiagnostic("bar.c", 20, "warning", "clang-tidy", "Style warning"),
    ]
    panel.set_diagnostics(diags)
    assert panel.table.rowCount() == 2
    assert panel.table.item(0, 0).text() == "cppcheck"
    assert panel.table.item(0, 1).text() == "ERROR"
    assert panel.table.item(0, 2).text() == "10"

    selected = []
    panel.diagnostic_selected.connect(lambda f, l: selected.append((f, l)))
    panel._on_cell_double_clicked(0, 3)
    assert selected == [("foo.c", 10)]
