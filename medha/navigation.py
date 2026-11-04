"""Local, incremental navigation: no indexing service or startup network traffic."""
import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel, QPushButton
from medha.command_palette import CommandPalette


IGNORED = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.medha_build', 'build', 'dist'}


def workspace_files(root):
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and not d.startswith('.'))
        for name in sorted(files):
            path = Path(folder, name)
            if not path.is_symlink():
                yield path
    # Never follow directory symlinks or scan dependency/build trees.


class QuickOpen(CommandPalette):
    def __init__(self, root, opener, parent=None):
        self.paths = []
        self.root = Path(root)
        self.opener = opener
        super().__init__([], parent)
        self.setWindowTitle('Quick Open')
        self.search.setPlaceholderText('Search workspace files…')
        self.pending = workspace_files(root)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.index_batch)
        self.finished.connect(self.timer.stop)
        self.timer.start(0)
        # Small batches keep typing and Escape responsive on large projects.

    def index_batch(self):
        for _ in range(100):
            path = next(self.pending, None)
            if path is None:
                self.timer.stop()
                break
            self.paths.append(path)
        self.refilter(self.search.text())

    def refilter(self, text):
        self.list.clear()
        words = text.casefold().split()
        for path in self.paths:
            label = str(path.relative_to(self.root))
            if all(word in label.casefold() for word in words):
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.list.addItem(item)
                if self.list.count() == 200:
                    break
        if self.list.count():
            self.list.setCurrentRow(0)

    def run_selected(self):
        item = self.list.currentItem()
        if item:
            path = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
            self.opener(path)


class SearchView(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.query = QLineEdit()
        self.query.setPlaceholderText('Search text in workspace · Enter')
        self.query.setAccessibleName('Workspace search')
        self.query.returnPressed.connect(self.search)
        self.info = QLabel('Search local text files (up to 1 MB each).')
        self.info.setWordWrap(True)
        self.results = QListWidget()
        self.results.itemActivated.connect(self.open_result)
        layout.addWidget(self.query)
        layout.addWidget(self.info)
        layout.addWidget(self.results)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scan_next)

    def search(self):
        self.timer.stop()
        self.results.clear()
        self.needle = self.query.text().casefold()
        if not self.needle:
            return
        self.pending = workspace_files(self.window.workspace_path)
        self.info.setText('Searching…')
        self.timer.start(0)

    def scan_next(self):
        path = next(self.pending, None)
        if path is None or self.results.count() >= 1000:
            self.timer.stop()
            self.info.setText(f'{self.results.count()} matches' + (' (limit reached)' if path else ''))
            return
        try:
            if path.stat().st_size > 1_000_000:
                return
            content = path.read_text(encoding='utf-8')
            if '\0' in content:
                return
        except (OSError, UnicodeError):
            return
        for number, line in enumerate(content.splitlines(), 1):
            if self.needle in line.casefold():
                item = QListWidgetItem(f'{path.relative_to(self.window.workspace_path)}:{number}  {line.strip()[:120]}')
                item.setData(Qt.ItemDataRole.UserRole, (str(path), number))
                self.results.addItem(item)
                if self.results.count() >= 1000:
                    break
        # Only plain text is opened; binary and oversized files are skipped explicitly.

    def open_result(self, item):
        path, line = item.data(Qt.ItemDataRole.UserRole)
        self.window.navigate_to_problem(path, line)


class GitView(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        self.info = QLabel('Source Control')
        self.info.setWordWrap(True)
        self.files = QListWidget()
        refresh = QPushButton('Refresh Git status')
        refresh.clicked.connect(self.refresh)
        commit = QPushButton('Stage and commit…')
        commit.clicked.connect(window.action_git_commit)
        layout.addWidget(self.info)
        layout.addWidget(refresh)
        layout.addWidget(self.files)
        layout.addWidget(commit)

    def refresh(self):
        from medha.git_backend import GitBackend
        backend = GitBackend(self.window.workspace_path)
        try:
            result = backend._run_git(['status', '--short'])
            self.files.clear()
            if result.returncode:
                self.info.setText('This folder is not a Git repository.')
            else:
                self.info.setText('Working tree changes')
                self.files.addItems(result.stdout.splitlines() or ['No changes'])
        except OSError as error:
            self.info.setText(f'Git unavailable: {error}')
        # Refresh is user initiated; entering the IDE does not invoke remote Git.
