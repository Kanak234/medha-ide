DARK_QSS = """
QMainWindow, QWidget {
    background-color: #1e1f22;
    color: #bcbec4;
    font-family: "JetBrains Mono", "Cascadia Code", "DejaVu Sans Mono", monospace;
}

QMainWindow::separator {
    background-color: #393b40;
    width: 1px;
    height: 1px;
}

QMenuBar {
    background-color: #2b2d30;
    color: #bcbec4;
    border-bottom: 1px solid #393b40;
    padding: 2px;
}

QMenuBar::item:selected {
    background-color: #2e436e;
    color: #ffffff;
}

QMenu {
    background-color: #2b2d30;
    color: #bcbec4;
    border: 1px solid #393b40;
}

QMenu::item:selected {
    background-color: #2e436e;
    color: #ffffff;
}

QStatusBar {
    background-color: #2b2d30;
    color: #bcbec4;
    border-top: 1px solid #393b40;
}

QDockWidget {
    color: #bcbec4;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    border: 1px solid #393b40;
}

QDockWidget::title {
    background-color: #2b2d30;
    padding: 6px;
    border-bottom: 1px solid #393b40;
}

QPlainTextEdit, QTextEdit, QLineEdit {
    background-color: #1e1f22;
    color: #bcbec4;
    border: 1px solid #393b40;
    font-family: "JetBrains Mono", "Cascadia Code", "DejaVu Sans Mono", monospace;
    font-size: 13px;
    selection-background-color: #214283;
}

QTreeView, QListView, QTableWidget {
    background-color: #1e1f22;
    color: #bcbec4;
    border: 1px solid #393b40;
    selection-background-color: #214283;
}

QTreeView::item:hover, QListView::item:hover {
    background-color: #2e436e;
}

QPushButton {
    background-color: #365880;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 5px 12px;
    font-family: "JetBrains Mono", "Cascadia Code", "DejaVu Sans Mono", monospace;
}

QPushButton:hover {
    background-color: #2e436e;
}

QTabBar::tab {
    background-color: #2b2d30;
    color: #bcbec4;
    border: 1px solid #393b40;
    padding: 6px 12px;
}

QTabBar::tab:selected {
    background-color: #1e1f22;
    color: #ffffff;
    border-bottom: 2px solid #365880;
}

QSplitter::handle {
    background-color: #393b40;
}
"""
