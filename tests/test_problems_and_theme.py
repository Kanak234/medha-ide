from medha.theme import DARK_QSS
from medha.problems import ProblemsPanelWidget
from medha.compiler_engine import DiagnosticIssue

def test_theme():
    assert "background-color" in DARK_QSS
    assert "QMainWindow" in DARK_QSS
    assert "#1e1f22" in DARK_QSS

def test_problems_panel(qapp):
    panel = ProblemsPanelWidget()
    diags = [
        DiagnosticIssue("/tmp/a.c", 1, 2, "error", "Missing semicolon"),
        DiagnosticIssue("/tmp/b.c", 5, 1, "warning", "Unused variable"),
    ]
    panel.set_diagnostics(diags)
    assert panel.table.rowCount() == 2
    assert panel.table.item(0, 0).text() == "ERROR"
    assert panel.table.item(0, 1).text() == "Missing semicolon"
    assert panel.table.item(1, 0).text() == "WARNING"

    selected = []
    panel.problem_selected.connect(lambda f, l, c: selected.append((f, l, c)))
    panel.on_cell_double_clicked(0, 1)
    assert selected == [("/tmp/a.c", 1, 2)]
