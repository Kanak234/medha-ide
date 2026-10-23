from pathlib import Path

from medha.app import default_workspace
from medha import platform_info


def test_install_subfolder_is_never_a_workspace(tmp_path, monkeypatch):
    install = tmp_path / "installed"
    nested = install / "MEDHA" / "_internal"
    nested.mkdir(parents=True)
    home = tmp_path / "user"
    home.mkdir()
    monkeypatch.setattr(platform_info, "app_root", lambda: install)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(platform_info, "user_data_dir", lambda: home / "data")
    assert default_workspace(str(nested)) == str(home / "MEDHA Projects")
    assert not list(nested.iterdir())


def test_windows_system_directory_is_not_scanned(tmp_path, monkeypatch):
    windows = tmp_path / "Windows"
    system = windows / "System32"
    system.mkdir(parents=True)
    home = tmp_path / "user"
    home.mkdir()
    monkeypatch.setattr(platform_info, "IS_WINDOWS", True)
    monkeypatch.setenv("WINDIR", str(windows))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(platform_info, "user_data_dir", lambda: home / "data")
    assert default_workspace(str(system)) == str(home / "MEDHA Projects")
