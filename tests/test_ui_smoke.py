"""
Offscreen UI smoke test — opens the main window and exercises every menu action.

This test runs with QT_QPA_PLATFORM=offscreen to avoid needing a display.
Every QAction in the menu bar is triggered once. Dialogs are auto-closed
to keep the test non-interactive. Any exception = test failure.
"""
from __future__ import annotations
import os
import sys

# Force offscreen rendering BEFORE importing Qt
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog, QFileDialog
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

# Create QApplication instance (or get existing)
app = QApplication.instance() or QApplication(sys.argv)


def close_dialogs():
    """Close any open dialogs (message boxes, file dialogs, etc.)."""
    for widget in app.topLevelWidgets():
        if isinstance(widget, (QMessageBox, QDialog, QFileDialog)):
            if widget.isVisible():
                # Accept/close the dialog
                if isinstance(widget, QMessageBox):
                    widget.done(QMessageBox.StandardButton.Ok)
                elif isinstance(widget, QFileDialog):
                    widget.done(QDialog.DialogCode.Rejected)
                else:
                    widget.done(QDialog.DialogCode.Rejected)
                widget.close()
    app.processEvents()


def trigger_action(action, window):
    """Trigger a QAction and close any resulting dialogs."""
    # Some actions may show dialogs; close them after a brief moment
    QTimer.singleShot(50, close_dialogs)
    action.trigger()
    app.processEvents()
    QTest.qWait(100)  # Let any async operations settle
    close_dialogs()
    app.processEvents()


class TestUISmoke:
    """Smoke test: open window, trigger every menu action, assert no crash."""

    @pytest.fixture(scope="class")
    def window(self):
        """Create and show the main window."""
        # Import here to ensure QT_QPA_PLATFORM is set first
        from medha.app import MedhaMainWindow

        win = MedhaMainWindow()
        win.show()
        app.processEvents()
        QTest.qWait(200)  # Let window fully initialize

        yield win

        # Cleanup
        win.close()
        app.processEvents()

    def test_window_opens(self, window):
        """Verify the main window opens without exception."""
        assert window.isVisible()
        assert window.windowTitle()

    def _should_skip_action(self, action) -> bool:
        """Return True if this action should be skipped (e.g., Exit)."""
        text = action.text().replace("&", "").lower()
        # Skip Exit/Quit - it closes the window
        if text in ("exit", "quit"):
            return True
        return False

    def test_file_menu_actions(self, window):
        """Trigger all File menu actions except Exit."""
        file_menu = self._find_menu(window, "File")
        assert file_menu is not None, "File menu not found"

        for action in file_menu.actions():
            if action.menu():  # Submenu (e.g., "Open Lab Program")
                self._trigger_submenu_actions(action.menu(), window)
            elif not self._should_skip_action(action):
                trigger_action(action, window)

        assert window.isVisible()

    def test_edit_menu_actions(self, window):
        """Trigger all Edit menu actions."""
        edit_menu = self._find_menu(window, "Edit")
        assert edit_menu is not None, "Edit menu not found"

        for action in edit_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_view_menu_actions(self, window):
        """Trigger all View menu actions (dock toggles)."""
        view_menu = self._find_menu(window, "View")
        assert view_menu is not None, "View menu not found"

        for action in view_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_run_menu_actions(self, window):
        """Trigger all Run menu actions."""
        run_menu = self._find_menu(window, "Run")
        assert run_menu is not None, "Run menu not found"

        for action in run_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_analyze_menu_actions(self, window):
        """Trigger all Analyze menu actions."""
        analyze_menu = self._find_menu(window, "Analyze")
        assert analyze_menu is not None, "Analyze menu not found"

        for action in analyze_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_debug_menu_actions(self, window):
        """Trigger all Debug menu actions (skip Start Debugging which needs a debug server)."""
        debug_menu = self._find_menu(window, "Debug")
        assert debug_menu is not None, "Debug menu not found"

        for action in debug_menu.actions():
            text = action.text().replace("&", "").lower()
            # Skip "Start Debugging" - it tries to connect to a debug server
            if "start debugging" in text:
                continue
            trigger_action(action, window)
        assert window.isVisible()

    def test_lsp_menu_actions(self, window):
        """Trigger all LSP menu actions."""
        lsp_menu = self._find_menu(window, "LSP")
        assert lsp_menu is not None, "LSP menu not found"

        for action in lsp_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_git_menu_actions(self, window):
        """Trigger all Git menu actions."""
        git_menu = self._find_menu(window, "Git")
        assert git_menu is not None, "Git menu not found"

        for action in git_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_build_menu_actions(self, window):
        """Trigger all Build menu actions."""
        build_menu = self._find_menu(window, "Build")
        assert build_menu is not None, "Build menu not found"

        for action in build_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_tools_menu_actions(self, window):
        """Trigger all Tools menu actions."""
        tools_menu = self._find_menu(window, "Tools")
        assert tools_menu is not None, "Tools menu not found"

        for action in tools_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_help_menu_actions(self, window):
        """Trigger all Help menu actions."""
        help_menu = self._find_menu(window, "Help")
        assert help_menu is not None, "Help menu not found"

        for action in help_menu.actions():
            trigger_action(action, window)
        assert window.isVisible()

    def test_all_actions_collectively(self, window):
        """Collect every QAction from menu bar and trigger each once (skipping Exit/Start Debugging)."""
        menu_bar = window.menuBar()
        all_actions = []

        for menu_action in menu_bar.actions():
            menu = menu_action.menu()
            if menu:
                self._collect_actions(menu, all_actions)

        for action in all_actions:
            text = action.text().replace("&", "").lower()
            if text in ("exit", "quit", "start debugging"):
                continue
            trigger_action(action, window)

        assert window.isVisible()

    def _find_menu(self, window, title: str):
        """Find a menu by its title (with & stripped)."""
        menu_bar = window.menuBar()
        clean_title = title.replace("&", "")
        for action in menu_bar.actions():
            menu = action.menu()
            if menu and menu.title().replace("&", "") == clean_title:
                return menu
        return None

    def _collect_actions(self, menu, action_list: list):
        """Recursively collect all QActions from a menu and its submenus."""
        for action in menu.actions():
            if action.menu():
                self._collect_actions(action.menu(), action_list)
            else:
                action_list.append(action)

    def _trigger_submenu_actions(self, menu, window):
        """Trigger all actions in a submenu."""
        for action in menu.actions():
            if action.menu():
                self._trigger_submenu_actions(action.menu(), window)
            elif not self._should_skip_action(action):
                trigger_action(action, window)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])