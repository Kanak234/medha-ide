"""Open the real Qt window offline; individual workbench contracts live here."""
import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from medha import settings
from medha.app import MedhaMainWindow


@pytest.fixture
def window(tmp_path, monkeypatch):
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
    win.close()
    app.processEvents()
    settings.reset_cache_for_tests()


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
