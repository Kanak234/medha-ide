"""Cross-artifact checks for release preparation; no build or publish side effects."""
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

from medha import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_package_versions_agree():
    manifest = ET.parse(ROOT / 'packaging/windows/AppxManifest.xml')
    identity = manifest.find('{*}Identity')
    assert identity.attrib['Version'] == __version__ + '.0'
    appstream = ET.parse(ROOT / 'packaging/io.github.Kanak234.Medha.metainfo.xml')
    assert appstream.find('releases/release').attrib['version'] == __version__
    assert f'**Prepared version:** {__version__}' in (ROOT / 'store/listing.md').read_text()
    snap = (ROOT / 'snap/snapcraft.yaml').read_text()
    assert 'adopt-info: medha-app' in snap
    assert 'craftctl set version="$VERSION"' in snap
    # Snap derives its version from the same app constant instead of a second literal.


def test_partner_center_copy_is_short_and_does_not_claim_pending_terminal():
    listing = (ROOT / 'store/listing.md').read_text()
    copy = listing.split('<!-- WHATS_NEW_START -->')[1].split('<!-- WHATS_NEW_END -->')[0].strip()
    assert 0 < len(copy) < 1500
    assert all(line.startswith('- ') for line in copy.splitlines())
    assert 'ConPTY' not in copy and 'PTY' not in copy


def test_seven_store_screenshots_have_native_dimensions():
    images = sorted((ROOT / 'store/screenshots-v2').glob('*.png'))
    assert len(images) == 7
    for index, path in enumerate(images, 1):
        assert path.name.startswith(f'{index:02d}-')
        data = path.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', data[16:24]) == (1920, 1080)


def test_about_reports_app_version(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
    from medha import settings, toolchains
    from medha.app import MedhaMainWindow
    app = QApplication.instance() or QApplication([])
    parent = QWidget()
    seen = []
    monkeypatch.setattr(toolchains, 'find', lambda name: SimpleNamespace(version='local compiler'))
    monkeypatch.setattr(settings, 'settings_path', lambda: str(tmp_path / 'settings.json'))
    monkeypatch.setattr(QMessageBox, 'exec', lambda box: seen.append((box.windowTitle(), box.text())))
    MedhaMainWindow.show_about_dialog(parent)
    assert __version__ in seen[0][0] and __version__ in seen[0][1]
    parent.close()
    parent.deleteLater()
    app.processEvents()
