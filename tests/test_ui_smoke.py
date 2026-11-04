"""Open the real Qt window offline; individual workbench contracts live here."""
import pytest
from PySide6.QtCore import QSettings, QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from medha import settings
from medha.app import MedhaMainWindow


@pytest.fixture
def window(tmp_path, monkeypatch):
    import sys
    import requests
    errors = []
    monkeypatch.setattr(sys, 'excepthook', lambda *error: errors.append(error))
    def deny_network(*args, **kwargs):
        raise AssertionError('UI startup must remain offline')
    monkeypatch.setattr(requests.Session, 'request', deny_network)
    app = QApplication.instance() or QApplication([])
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'data'))
    monkeypatch.setattr(settings, 'settings_path', lambda: str(tmp_path / 'settings.json'))
    settings.reset_cache_for_tests()
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(tmp_path))
    win = MedhaMainWindow(str(tmp_path))
    win.resize(1366, 768)
    win.show()
    QTest.qWait(150)
    yield win
    for index in range(win.tab_widget.count()):
        widget = win.tab_widget.widget(index)
        if hasattr(widget, "is_modified"):
            widget.is_modified = False
    win.close()
    win.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    settings.reset_cache_for_tests()
    assert not errors, errors


def test_window_opens(window):
    assert window.isVisible()
    assert window.tab_widget.count() > 0


def test_titles_escape_literal_ampersands(window, tmp_path):
    import re
    from PySide6.QtWidgets import QDockWidget, QTabWidget
    path = tmp_path / 'a&b.c'
    path.write_text('int main(void) {}')
    window.open_file_path(str(path))
    window.get_current_editor().insertPlainText('// edit')
    window.create_untitled_tab('x&y.c')
    titles = [dock.windowTitle() for dock in window.findChildren(QDockWidget)]
    for tabs in window.findChildren(QTabWidget):
        titles.extend(tabs.tabText(i) for i in range(tabs.count()))
    assert all(not re.search(r'(?<!&)&(?!&)', title) for title in titles)


@pytest.mark.parametrize('size', [(1366, 768), (1920, 1080)])
def test_editor_width_and_tool_routing(window, size):
    window.resize(*size)
    QTest.qWait(50)
    assert window.tab_widget.width() >= size[0] * .6
    for dock in window.workbench.routes:
        dock.toggleViewAction().trigger()
        QApplication.processEvents()
        assert window.tab_widget.width() >= size[0] * .6
    window.workbench.toggle_sidebar()
    assert window.workbench.sidebar.isHidden()
    window.workbench.toggle_panel()
    assert window.bottom_tabs.isHidden()
    window.dock_turbo.show()
    assert not window.bottom_tabs.isHidden()


def test_layout_preferences_roundtrip(window):
    shell = window.workbench
    shell.sidebar_width = 320
    shell.panel_height = 180
    shell.toggle_sidebar()
    shell.save()
    prefs = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, 'MEDHA', 'Workbench-v2')
    assert prefs.value('sidebar_width', type=int) == 320
    assert prefs.value('panel_height', type=int) == 180
    assert prefs.value('sidebar_visible', type=bool) is False


def test_menu_order_and_existing_actions_preserved(window):
    import json
    from pathlib import Path
    from collections import Counter
    from medha.command_palette import collect_actions
    menus = [a.text().replace('&', '') for a in window.menuBar().actions()]
    assert menus == ['File', 'Edit', 'Selection', 'View', 'Go', 'Run', 'Terminal', 'Help']
    original = json.loads((Path(__file__).parent / 'fixtures/v1_actions.json').read_text())
    before = Counter(text.replace('&', '') for text in original)
    after = Counter(action.text().replace('&', '') for _, action in collect_actions(window.menuBar()))
    assert not (before - after)
    reachable = {action for _, action in collect_actions(window.menuBar())}
    assert set(window.legacy_actions) <= reachable


def test_quick_open_and_workspace_search(window, tmp_path):
    from medha.navigation import QuickOpen
    source = tmp_path / 'unique-file.c'
    source.write_text('int find_this = 7;\n')
    opened = []
    dialog = QuickOpen(tmp_path, opened.append, window)
    for _ in range(10):
        QApplication.processEvents()
    dialog.search.setText('unique-file')
    assert dialog.list.count() == 1
    dialog.run_selected()
    assert opened == [str(source)]
    window.search_view.query.setText('find_this')
    window.search_view.search()
    for _ in range(30):
        QApplication.processEvents()
    assert window.search_view.results.count() == 1
    window.search_view.open_result(window.search_view.results.item(0))
    assert window.get_current_editor().file_path == str(source)


def test_themes_apply_to_existing_and_new_editors(window):
    from medha.theme import LIGHT, DARK
    window.create_untitled_tab(content='int value = 1;')
    editor = window.get_current_editor()
    for name, colors in [('light', LIGHT), ('dark', DARK)]:
        window.apply_theme(name)
        QApplication.processEvents()
        assert editor.theme_tokens['bg'] == colors['bg']
        assert not editor.is_modified
        assert editor.minimap.width() == 80
        window.create_untitled_tab()
        assert window.get_current_editor().theme_tokens['bg'] == colors['bg']


def test_welcome_does_not_create_files(window, tmp_path):
    from medha.welcome import WelcomePage
    assert isinstance(window.tab_widget.currentWidget(), WelcomePage)
    assert not (tmp_path / 'main.c').exists()
    window.create_untitled_tab()
    window.close_tab(window.tab_widget.currentIndex())
    assert isinstance(window.tab_widget.currentWidget(), WelcomePage)


def test_cancel_keeps_unsaved_tab(window, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    window.create_untitled_tab()
    editor = window.get_current_editor()
    editor.insertPlainText('unsaved')
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Cancel)
    window.close_tab(window.tab_widget.currentIndex())
    assert window.tab_widget.indexOf(editor) >= 0
    window.close()
    assert window.isVisible()
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Discard)
    window.close_tab(window.tab_widget.indexOf(editor))
    assert window.tab_widget.indexOf(editor) == -1


def test_status_uses_document_and_build_data(window, tmp_path):
    from types import SimpleNamespace
    source = tmp_path / 'sample.py'
    source.write_text('print(1)\nprint(2)\n')
    window.open_file_path(str(source))
    window.navigate_to_line(2)
    assert 'Ln 2' in window.lbl_cursor_pos.text()
    assert 'PYTHON' in window.lbl_cursor_pos.text()
    assert 'UTF-8' in window.lbl_cursor_pos.text()
    assert 'sample.py' in window.windowTitle()
    assert window.lbl_sys_info.isHidden()
    window.status_controller.set_diagnostics([SimpleNamespace(severity='error'), SimpleNamespace(severity='warning')])
    assert window.status_controller.diagnostics.text() == '1 errors · 1 warnings'
    window.status_controller.monitor.setChecked(True)
    window.status_controller.refresh()
    assert '%' in window.lbl_sys_info.text()


def test_every_menu_action_from_welcome(window, monkeypatch):
    """Exercise UI slots with cancelled dialogs and isolated external build calls."""
    import sys
    from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QInputDialog, QMenu
    from medha.command_palette import collect_actions
    from medha.build import BuildSystem
    errors = []
    monkeypatch.setattr(sys, 'excepthook', lambda *error: errors.append(error))
    monkeypatch.setattr(QDialog, 'exec', lambda self: QDialog.DialogCode.Rejected)
    monkeypatch.setattr(QMessageBox, 'exec', lambda self: QMessageBox.StandardButton.Cancel)
    monkeypatch.setattr(QMenu, 'exec', lambda *args: None)
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a, **k: ('', ''))
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a, **k: ('', ''))
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', lambda *a, **k: '')
    monkeypatch.setattr(QInputDialog, 'getInt', lambda *a, **k: (1, False))
    monkeypatch.setattr(BuildSystem, 'configure', lambda self: (0, 'Smoke configuration'))
    monkeypatch.setattr(BuildSystem, 'build', lambda self: (0, 'Smoke build', None))
    monkeypatch.setattr(window, 'open_lab_program', lambda path: None)
    # Each action starts in the legitimate no-active-document Welcome state.
    # Editing/build behavior with a real document is covered in the focused tests.
    actions = [action for _, action in collect_actions(window.menuBar())]
    exit_action = next(a for a in actions if a.text().replace('&', '') == 'Exit')
    for action in actions:
        if action == exit_action:
            continue
        window.show_welcome()
        action.trigger()
        QApplication.processEvents()
        assert not errors, (action.text(), errors)
        assert window.isVisible(), action.text()
    exit_action.trigger()
    assert not errors
    assert not window.isVisible()


@pytest.mark.parametrize('theme', ['dark', 'light'])
@pytest.mark.parametrize('width,height', [(1366, 768), (1920, 1080)])
def test_text_viewport_meets_width_target(window, theme, width, height):
    window.resize(width, height)
    window.apply_theme(theme)
    window.create_untitled_tab('sample.c', 'int main(void) { return 0; }')
    QTest.qWait(30)
    editor = window.get_current_editor()
    assert editor.viewport().width() >= width * .6
    assert editor.lang == 'c'
    window.workbench.toggle_panel()
    window.show_panel(window.problems)
    assert window.bottom_tabs.isVisible()
    assert window.bottom_tabs.currentWidget() == window.problems


def test_layout_restored_in_second_window(window):
    shell = window.workbench
    shell.sidebar_width = 310
    shell.panel_height = 190
    shell.sidebar.hide()
    shell.save()
    other = MedhaMainWindow(window.workspace_path)
    other.show()
    QApplication.processEvents()
    assert other.workbench.sidebar_width == 310
    assert other.workbench.panel_height == 190
    assert other.workbench.sidebar.isHidden()
    other.close()
    other.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_cancelled_save_as_preserves_unsaved_document(window, monkeypatch):
    from PySide6.QtWidgets import QMessageBox, QFileDialog
    window.create_untitled_tab()
    editor = window.get_current_editor()
    editor.insertPlainText('int x;')
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Save)
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *args: ('', ''))
    window.close_tab(window.tab_widget.currentIndex())
    assert window.get_current_editor() is editor
    assert editor.is_modified


def test_recent_files_and_minimap_navigation(window, tmp_path):
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtWidgets import QPushButton
    source = tmp_path / 'recent.c'
    source.write_text('\n'.join(f'int value_{i};' for i in range(300)))
    window.open_file_path(str(source))
    editor = window.get_current_editor()
    QTest.qWait(30)
    QTest.mouseClick(editor.minimap, Qt.MouseButton.LeftButton,
                     pos=QPoint(20, editor.minimap.height() // 2))
    assert editor.textCursor().blockNumber() > 100
    window.show_welcome()
    assert any('recent.c' in button.text() for button in window.tab_widget.currentWidget().findChildren(QPushButton))


def test_collapse_keyboard_shortcuts(window):
    from PySide6.QtCore import Qt
    window.activateWindow()
    window.setFocus()
    QTest.keyClick(window, Qt.Key.Key_B, Qt.KeyboardModifier.ControlModifier)
    assert window.workbench.sidebar.isHidden()
    QTest.keyClick(window, Qt.Key.Key_J, Qt.KeyboardModifier.ControlModifier)
    assert window.bottom_tabs.isHidden()
    QTest.keyClick(window, Qt.Key.Key_B, Qt.KeyboardModifier.ControlModifier)
    assert not window.workbench.sidebar.isHidden()
