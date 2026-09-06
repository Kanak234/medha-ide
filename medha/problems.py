from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

class ProblemsPanelWidget(QWidget):
    problem_selected = Signal(str, int, int) # file_path, line, col

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Severity", "Message", "File", "Line"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #090d16;
                color: #c9d1d9;
                border: none;
                gridline-color: #21262d;
            }
            QHeaderView::section {
                background-color: #161b22;
                color: #8b949e;
                padding: 4px;
                border: none;
            }
        """)

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        layout.addWidget(self.table)

    def set_diagnostics(self, diagnostics):
        self.table.setRowCount(0)
        for diag in diagnostics:
            row = self.table.rowCount()
            self.table.insertRow(row)

            item_sev = QTableWidgetItem(diag.severity.upper())
            if diag.severity == 'error':
                item_sev.setForeground(QColor('#f85149'))
            else:
                item_sev.setForeground(QColor('#d29922'))

            item_msg = QTableWidgetItem(diag.message)
            item_file = QTableWidgetItem(diag.file_path)
            item_line = QTableWidgetItem(str(diag.line))

            item_msg.setData(Qt.ItemDataRole.UserRole, (diag.file_path, diag.line, diag.col))

            self.table.setItem(row, 0, item_sev)
            self.table.setItem(row, 1, item_msg)
            self.table.setItem(row, 2, item_file)
            self.table.setItem(row, 3, item_line)

    def on_cell_double_clicked(self, row, col):
        item = self.table.item(row, 1)
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                fpath, line, c = data
                self.problem_selected.emit(fpath, line, c)
