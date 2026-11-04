"""Welcome actions use existing handlers; merely launching never creates a file."""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from medha import settings


class WelcomePage(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 40, 64, 40)
        layout.setSpacing(6)
        title = QLabel('Medhā')
        title.setObjectName('WelcomeTitle')
        subtitle = QLabel('Build something. Understand how it works.')
        subtitle.setObjectName('WelcomeSubtitle')
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(24)

        def link(text, callback):
            button = QPushButton(text)
            button.setObjectName('welcomeLink')
            button.clicked.connect(callback)
            layout.addWidget(button)

        link('New C file', lambda: window.create_untitled_tab('untitled.c', '#include <stdio.h>\n\nint main(void) {\n    return 0;\n}\n'))
        link('Open folder…', window.action_open_folder)
        link('Open file…', window.action_open_file)
        link('Turbo C examples', window.show_turbo_examples)
        link('Learn DSA visually', window.dock_dsa.show)
        layout.addSpacing(20)
        layout.addWidget(QLabel('RECENT'))
        recent_box = QWidget()
        self.recent_layout = QVBoxLayout(recent_box)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(recent_box)
        self.refresh_recent()
        layout.addStretch()
        hint = QLabel('Ctrl+P  Open a file     ·     Ctrl+Shift+P  Find any command')
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def refresh_recent(self):
        while self.recent_layout.count():
            self.recent_layout.takeAt(0).widget().deleteLater()
        recent = [path for path in settings.get('recent_files', []) if Path(path).is_file()]
        for path in recent[:6]:
            button = QPushButton(Path(path).name + '  ·  ' + str(Path(path).parent))
            button.setObjectName('welcomeLink')
            button.clicked.connect(lambda _=False, p=path: self.window.open_file_path(p))
            self.recent_layout.addWidget(button)
        if not recent:
            self.recent_layout.addWidget(QLabel('Files you open will appear here.'))
        # Refresh on re-entry so Recent reflects files opened during this session.
