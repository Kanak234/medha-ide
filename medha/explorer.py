from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel, QHeaderView, QFileSystemModel
from PySide6.QtCore import QDir, Signal, Qt

class ProjectExplorerWidget(QWidget):
    file_selected = Signal(str)

    def __init__(self, workspace_path="/home/kanak/Desktop/ide", parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(" WORKSPACE EXPLORER")
        header.setStyleSheet("background-color: #161b22; color: #8b949e; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        self.model = QFileSystemModel()
        self.model.setRootPath(workspace_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(workspace_path))
        self.tree.hideColumn(1) # Size
        self.tree.hideColumn(2) # Type
        self.tree.hideColumn(3) # Date Modified

        self.tree.header().setVisible(False)
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
            }
            QTreeView::item:hover {
                background-color: #161b22;
            }
            QTreeView::item:selected {
                background-color: #1f6feb;
                color: #ffffff;
            }
        """)

        self.tree.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.tree)

    def set_workspace(self, path):
        self.workspace_path = path
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))

    def on_double_click(self, index):
        path = self.model.filePath(index)
        if not self.model.isDir(index):
            self.file_selected.emit(path)
