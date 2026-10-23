"""
MEDHĀ IDE — command_palette.py — Ctrl+Shift+P and Help → Keyboard Shortcuts
============================================================================

WHAT:  A searchable list of every menu command (with its shortcut). Type a few
       letters, press Enter, the command runs. The same data feeds the shortcuts list.
WHY:   VS Code users expect Ctrl+Shift+P; it also makes every feature reachable by
       keyboard only (accessibility requirement in docs/UI_UX_BRIEF.md).
USED BY: app.py.
FLOW:  collect_actions(menubar) → [(label, QAction)] → filter as you type → trigger()
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QLineEdit, QListWidget, QListWidgetItem,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView)


def collect_actions(menubar):
    """Walk all menus → [(\"Menu › Item\", QAction)] for enabled, non-separator actions."""
    out = []

    def walk(menu, prefix):
        for act in menu.actions():
            if act.isSeparator():
                continue
            if act.menu():
                walk(act.menu(), f"{prefix}{act.menu().title().replace('&', '')} › ")
                continue
            text = act.text().replace("&", "")
            if text:
                out.append((prefix + text, act))

    for top in menubar.actions():
        if top.menu():
            walk(top.menu(), top.menu().title().replace("&", "") + " › ")
    return out


class CommandPalette(QDialog):
    def __init__(self, actions, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setWindowTitle("Command Palette")
        self.resize(620, 420)
        self.actions_list = actions
        lay = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Type a command… (e.g. run, modernize, toolchains)")
        self.search.textChanged.connect(self.refilter)
        self.search.returnPressed.connect(self.run_selected)
        lay.addWidget(self.search)
        self.list = QListWidget()
        self.list.itemActivated.connect(lambda _i: self.run_selected())
        lay.addWidget(self.list)
        self.refilter("")
        self.search.setFocus()

    def refilter(self, text):
        words = text.lower().split()
        self.list.clear()
        for label, act in self.actions_list:
            if all(w in label.lower() for w in words):
                sc = act.shortcut().toString()
                item = QListWidgetItem(f"{label}    {sc}" if sc else label)
                item.setData(Qt.ItemDataRole.UserRole, act)
                self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            self.list.keyPressEvent(e)
        else:
            super().keyPressEvent(e)

    def run_selected(self):
        item = self.list.currentItem()
        if item:
            act = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
            act.trigger()


class ShortcutsDialog(QDialog):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard shortcuts")
        self.resize(640, 520)
        lay = QVBoxLayout(self)
        rows = [(label, act.shortcut().toString()) for label, act in actions if act.shortcut().toString()]
        table = QTableWidget(len(rows), 2)
        table.setHorizontalHeaderLabels(["Command", "Shortcut"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for r, (label, sc) in enumerate(rows):
            table.setItem(r, 0, QTableWidgetItem(label))
            table.setItem(r, 1, QTableWidgetItem(sc))
        lay.addWidget(table)
