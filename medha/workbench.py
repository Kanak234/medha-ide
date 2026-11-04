"""The workbench owns placement; existing tools continue to own their behavior.

WHY: docking every tool on the right imposes all their minimum sizes on the
editor. Scrollable sidebar pages and one bottom panel keep those tools reachable
without stealing the editing surface. Legacy dock actions route to their new home.
"""
from PySide6.QtCore import Qt, QSettings, QTimer, QSize
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDockWidget, QSplitter, QStackedWidget,
    QScrollArea, QToolButton, QStyle, QComboBox, QSizePolicy, QTextEdit, QLineEdit,
)


def activity_icon(title, color):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtGui import QPixmap, QPainter, QIcon
    paths = {
        'Explorer': '<path d="M8 3h11v15H8zM5 7H3v14h12v-2"/>',
        'Search': '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
        'Run and Debug': '<path d="m6 3 15 9-15 9z"/>',
        'Git': '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M6 7v10m12-10v3c0 4-12 1-12 7"/>',
        'Extensions': '<path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z"/>',
        'DSA': '<circle cx="12" cy="4" r="2"/><circle cx="4" cy="19" r="2"/><circle cx="20" cy="19" r="2"/><path d="m11 6-6 11m8-11 6 11"/>',
        'AI': '<path d="m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3z"/>',
        'Outline': '<path d="M8 5h13M8 12h10M8 19h13M3 5h1m-1 7h1m-1 7h1"/>',
    }
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
           f'<g fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round">'
           + paths.get(title, paths['Explorer']) + '</g></svg>')
    image = QPixmap(24, 24)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    QSvgRenderer(svg.encode()).render(painter)
    painter.end()
    return QIcon(image)
    # Neutral line icons remain legible in both themes, unlike platform-colored icons.


class ToolDock(QDockWidget):
    """Compatibility bridge for the existing show/raise/toggle call sites."""
    host = None

    def toggleViewAction(self):
        if not hasattr(self, '_view_action'):
            self._view_action = QAction(self.windowTitle(), self)
            self._view_action.triggered.connect(self.show)
        return self._view_action

    def setVisible(self, visible):
        if self.host is None:
            super().setVisible(visible)
        elif visible:
            self.host.reveal(self)
        # Once moved, hiding a legacy dock must not hide its reparented tool.

    def show(self):
        self.setVisible(True)

    def raise_(self):
        if self.host is None:
            super().raise_()
        else:
            self.host.reveal(self)


def scroll_page(widget):
    page = QScrollArea()
    page.setWidgetResizable(True)
    page.setFrameShape(QScrollArea.Shape.NoFrame)
    page.setWidget(widget)
    page.setMinimumSize(0, 0)
    page.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
    return page
    # A wide tool scrolls inside its page instead of enlarging the whole window.


class Workbench(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.prefs = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, 'MEDHA', 'Workbench-v2')
        self.routes = {}
        self.buttons = {}
        self.sidebar_width = max(180, min(420, self.prefs.value('sidebar_width', 270, type=int)))
        self.panel_height = max(120, min(400, self.prefs.value('panel_height', 220, type=int)))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.activity = QWidget()
        self.activity.setObjectName('activityBar')
        self.activity.setFixedWidth(48)
        self.activity_layout = QVBoxLayout(self.activity)
        self.activity_layout.setContentsMargins(0, 4, 0, 4)
        self.activity_layout.setSpacing(0)
        layout.addWidget(self.activity)

        self.horizontal = QSplitter(Qt.Orientation.Horizontal)
        self.sidebar = QWidget()
        self.sidebar.setObjectName('sideBar')
        self.sidebar.setMinimumWidth(0)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        self.selector = QComboBox()
        self.selector.setAccessibleName('Sidebar view')
        side_layout.addWidget(self.selector)
        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(0)
        self.stack.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        side_layout.addWidget(self.stack)
        self.selector.currentIndexChanged.connect(self.select)
        self.horizontal.addWidget(self.sidebar)
        self.vertical = QSplitter(Qt.Orientation.Vertical)
        self.vertical.addWidget(window.tab_widget)
        self.vertical.addWidget(window.bottom_tabs)
        window.bottom_tabs.setMinimumSize(0, 0)
        window.bottom_tabs.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        window.bottom_tabs.setUsesScrollButtons(True)
        self.horizontal.addWidget(self.vertical)
        self.horizontal.setStretchFactor(0, 0)
        self.horizontal.setStretchFactor(1, 1)
        self.vertical.setStretchFactor(0, 1)
        self.vertical.setStretchFactor(1, 0)
        layout.addWidget(self.horizontal)
        self.horizontal.splitterMoved.connect(self.remember_sidebar)
        self.vertical.splitterMoved.connect(self.remember_panel)
        # Splitter state is stored as logical sizes, clamped again for each display.

        sidebar_tools = [
            ('Explorer', window.dock_explorer, QStyle.StandardPixmap.SP_DirIcon),
            ('Run and Debug', window.dock_gdb, QStyle.StandardPixmap.SP_MediaPlay),
            ('Extensions', window.dock_extensions, QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ('DSA', window.dock_dsa, QStyle.StandardPixmap.SP_ComputerIcon),
            ('AI', window.dock_ai, QStyle.StandardPixmap.SP_MessageBoxInformation),
            ('Outline', window.dock_outline, QStyle.StandardPixmap.SP_FileDialogListView),
        ]
        for title, dock, icon in sidebar_tools:
            widget = dock.widget()
            window.removeDockWidget(dock)
            QDockWidget.setVisible(dock, False)
            self.add_view(title, widget, icon, dock)
        for title, dock in [('Memory', window.dock_memory), ('Disassembly', window.dock_asm),
                            ('Debug Console', None), ('Turbo C screen', window.dock_turbo)]:
            if dock is None:
                console = QWidget()
                console_layout = QVBoxLayout(console)
                self.debug_log = QTextEdit()
                self.debug_log.setReadOnly(True)
                self.debug_input = QLineEdit()
                self.debug_input.setPlaceholderText('Evaluate an expression in the active debug session')
                self.debug_input.returnPressed.connect(self.evaluate)
                window.gdb_engine.state_changed.connect(self.debug_log.append)
                console_layout.addWidget(self.debug_log)
                console_layout.addWidget(self.debug_input)
                window.bottom_tabs.addTab(console, title)
                continue
            widget = dock.widget()
            window.removeDockWidget(dock)
            QDockWidget.setVisible(dock, False)
            page = scroll_page(widget)
            window.bottom_tabs.addTab(page, title)
            self.routes[dock] = ('panel', page)
            dock.host = self
        window.removeDockWidget(window.dock_bottom)
        QDockWidget.setVisible(window.dock_bottom, False)
        window.dock_bottom.host = self
        self.routes[window.dock_bottom] = ('panel', window.terminal)
        self.activity_layout.addStretch()
        self.add_toggle('Toggle Side Bar', 'Ctrl+B', self.toggle_sidebar)
        self.add_toggle('Toggle Panel', 'Ctrl+J', self.toggle_panel)
        self.selector.setCurrentIndex(0)
        self.sidebar.setVisible(self.prefs.value('sidebar_visible', True, type=bool))
        window.bottom_tabs.setVisible(self.prefs.value('panel_visible', True, type=bool))
        QTimer.singleShot(0, self.restore_sizes)

    def evaluate(self):
        expression = self.debug_input.text().strip()
        if not expression:
            return
        if not self.window.gdb_engine.session:
            self.debug_log.append('Start debugging before evaluating an expression.')
            return
        result = self.window.gdb_engine.evaluate_expression(expression)
        self.debug_log.append(f'> {expression}\n{result}')
        self.debug_input.clear()
        # The console uses the existing engine so watches and evaluations agree.

    def add_toggle(self, title, shortcut, slot):
        action = QAction(title, self.window)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        self.window.menuBar().actions()[2].menu().addAction(action)
        return action

    def add_view(self, title, widget, icon, dock=None):
        page = scroll_page(widget)
        index = self.stack.addWidget(page)
        self.selector.addItem(title)
        button = QToolButton()
        button.setFixedSize(48, 48)
        button.setIconSize(QSize(24, 24))
        button.setIcon(self.style().standardIcon(icon))
        button.setToolTip(title)
        button.setAccessibleName(title)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.activate(index))
        self.activity_layout.insertWidget(index, button)
        self.buttons[index] = button
        if dock:
            self.routes[dock] = ('side', index)
            dock.host = self
        return index

    def select(self, index):
        self.stack.setCurrentIndex(index)
        for number, button in self.buttons.items():
            button.setChecked(number == index)

    def activate(self, index):
        self.sidebar.show()
        self.selector.setCurrentIndex(index)
        self.select(index)
        self.restore_sizes()

    def reveal(self, dock):
        location, target = self.routes[dock]
        if location == 'side':
            self.activate(target)
        else:
            self.window.bottom_tabs.show()
            self.window.bottom_tabs.setCurrentWidget(target)
            self.restore_sizes()

    def toggle_sidebar(self):
        self.sidebar.setVisible(self.sidebar.isHidden())
        self.restore_sizes()

    def toggle_panel(self):
        self.window.bottom_tabs.setVisible(self.window.bottom_tabs.isHidden())
        self.restore_sizes()

    def restore_sizes(self):
        # Keep at least 60% of the whole window available to the editor at ≥1366px.
        maximum = max(160, int(self.window.width() * .4) - 56)
        width = min(self.sidebar_width, maximum)
        self.horizontal.setSizes([width, max(200, self.width() - width - 52)])
        self.vertical.setSizes([max(180, self.height() - self.panel_height), self.panel_height])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.restore_sizes()

    def remember_sidebar(self, position, index):
        width = self.horizontal.sizes()[0]
        if width > 0:
            self.sidebar_width = width
        self.restore_sizes()

    def remember_panel(self, position, index):
        height = self.vertical.sizes()[1]
        if height > 0:
            self.panel_height = height

    def save(self):
        self.prefs.setValue('sidebar_width', self.sidebar_width)
        self.prefs.setValue('panel_height', self.panel_height)
        self.prefs.setValue('sidebar_visible', not self.sidebar.isHidden())
        self.prefs.setValue('panel_visible', not self.window.bottom_tabs.isHidden())
        self.prefs.sync()
