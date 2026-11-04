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
