"""
Tests for Extension Installer.

Tests zip-slip protection, install/uninstall round-trip, and SHA-256 verification.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from medha.extensions.installer import (
    install_vsix,
    uninstall_extension,
    list_installed_extensions,
    get_installed_extension,
    set_extension_enabled,
    get_enabled_extensions,
    get_install_dir,
    get_extension_root,
    get_manifest_path,
    parse_extension_manifest,
    safe_extract_zip,
    verify_sha256,
    MAX_VSIX_SIZE,
    InstallError,
    ZipSlipError,
    SHA256MismatchError,
    SizeLimitError,
    CorruptArchiveError,
)
from medha.extensions.models import (
    ExtensionManifest,
    ExtensionClassification,
    InstalledExtension,
)


# =============================================================================
# Fixtures
# =============================================================================

def create_fixture_vsix(temp_dir: Path, name: str, manifest: dict, extra_files: dict = None) -> Path:
    """Create a test VSIX file."""
    vsix_path = temp_dir / f"{name}.vsix"
    with zipfile.ZipFile(vsix_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
        zf.writestr("extension.vsixmanifest", '<?xml version="1.0"?><PackageManifest/>')
        zf.writestr("extension/package.json", json.dumps(manifest))
        if extra_files:
            for fname, content in extra_files.items():
                zf.writestr(f"extension/{fname}", json.dumps(content) if isinstance(content, dict) else content)
    return vsix_path


def create_zip_slip_vsix(temp_dir: Path) -> Path:
    """Create a VSIX with zip-slip attack (path traversal)."""
    vsix_path = temp_dir / "evil.vsix"
    with zipfile.ZipFile(vsix_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
        zf.writestr("extension.vsixmanifest", '<?xml version="1.0"?><PackageManifest/>')
        zf.writestr("extension/package.json", json.dumps({"name": "evil", "version": "1.0.0"}))
        # Malicious entry that tries to escape
        zf.writestr("../escape.txt", "malicious content")
    return vsix_path


def create_large_vsix(temp_dir: Path, size_mb: int = 60) -> Path:
    """Create a VSIX larger than 50 MB limit."""
    vsix_path = temp_dir / "large.vsix"
    with zipfile.ZipFile(vsix_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
        zf.writestr("extension.vsixmanifest", '<?xml version="1.0"?><PackageManifest/>')
        zf.writestr("extension/package.json", json.dumps({"name": "large", "version": "1.0.0"}))
        # Add a large file
        large_content = b"x" * (size_mb * 1024 * 1024)
        zf.writestr("extension/large.bin", large_content)
    return vsix_path


@pytest.fixture
def temp_extensions_dir():
    """Temporary extensions directory for testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="medha_test_ext_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def theme_only_manifest():
    """Manifest with only theme contributions."""
    return {
        "name": "theme-only",
        "version": "1.0.0",
        "displayName": "Theme Only",
        "description": "Only themes",
        "publisher": "test-pub",
        "license": "MIT",
        "categories": ["Themes"],
        "contributes": {
            "themes": [
                {"label": "Dark Theme", "uiTheme": "vs-dark", "path": "./theme/dark.json"}
            ]
        }
    }


@pytest.fixture
def snippet_only_manifest():
    """Manifest with only snippet contributions."""
    return {
        "name": "snippet-only",
        "version": "1.0.0",
        "displayName": "Snippet Only",
        "description": "Only snippets",
        "publisher": "test-pub",
        "license": "MIT",
        "categories": ["Snippets"],
        "contributes": {
            "snippets": [
                {"language": "c", "path": "./snippets/c.json"}
            ]
        }
    }


@pytest.fixture
def js_only_manifest():
    """Manifest with only JS code (no declarative contributions)."""
    return {
        "name": "js-only",
        "version": "1.0.0",
        "displayName": "JS Only",
        "description": "Only JS code",
        "publisher": "test-pub",
        "license": "MIT",
        "main": "./out/extension.js",
        "browser": "./out/extension-browser.js",
    }


@pytest.fixture
def partial_manifest():
    """Manifest with both declarative contributions and JS code."""
    return {
        "name": "partial-ext",
        "version": "1.0.0",
        "displayName": "Partial Extension",
        "description": "Has themes and JS",
        "publisher": "test-pub",
        "license": "MIT",
        "categories": ["Themes"],
        "main": "./out/extension.js",
        "contributes": {
            "themes": [
                {"label": "My Theme", "uiTheme": "vs-dark", "path": "./theme/my.json"}
            ]
        }
    }


# =============================================================================
# Tests
# =============================================================================

class TestSafeExtractZip:
    """Tests for zip-slip protection."""

    def test_safe_extract_normal(self, temp_extensions_dir):
        """Normal extraction works."""
        vsix = create_fixture_vsix(temp_extensions_dir, "test", {"name": "test", "version": "1.0.0"})
        dest = temp_extensions_dir / "extracted"
        safe_extract_zip(vsix, dest)
        assert (dest / "extension" / "package.json").exists()

    def test_zip_slip_attack_rejected(self, temp_extensions_dir):
        """Zip-slip attack is detected and rejected."""
        vsix = create_zip_slip_vsix(temp_extensions_dir)
        dest = temp_extensions_dir / "extracted"
        with pytest.raises(ZipSlipError, match="Zip-slip detected"):
            safe_extract_zip(vsix, dest)

    def test_corrupt_zip_rejected(self, temp_extensions_dir):
        """Corrupt ZIP raises CorruptArchiveError."""
        bad_zip = temp_extensions_dir / "bad.zip"
        bad_zip.write_text("not a zip")
        dest = temp_extensions_dir / "extracted"
        with pytest.raises(CorruptArchiveError):
            safe_extract_zip(bad_zip, dest)


class TestVerifySHA256:
    """Tests for SHA-256 verification."""

    def test_sha256_match(self, temp_extensions_dir):
        """Matching SHA-256 returns True."""
        content = b"test content"
        filepath = temp_extensions_dir / "test.txt"
        filepath.write_bytes(content)
        sha256 = hashlib.sha256(content).hexdigest()
        assert verify_sha256(filepath, sha256) is True

    def test_sha256_mismatch(self, temp_extensions_dir):
        """Mismatched SHA-256 returns False."""
        filepath = temp_extensions_dir / "test.txt"
        filepath.write_bytes(b"content")
        assert verify_sha256(filepath, "0" * 64) is False


class TestInstallerRoundTrip:
    """Tests for install/uninstall round-trip."""

    def test_install_theme_only(self, temp_extensions_dir, theme_only_manifest, monkeypatch):
        """Install theme-only extension succeeds."""
        # Override extensions base dir
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "theme-only", theme_only_manifest, {
                "theme/dark.json": {"name": "Dark", "type": "dark", "colors": {}}
            })
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            installed = install_vsix(vsix, sha256)

            assert isinstance(installed, InstalledExtension)
            assert installed.namespace == "test-pub"
            assert installed.name == "theme-only"
            assert installed.version == "1.0.0"
            assert installed.classification == ExtensionClassification.SUPPORTED
            assert installed.enabled is True
            assert len(installed.manifest.themes) == 1
            assert installed.manifest.themes[0].label == "Dark Theme"

            # Verify manifest.json exists
            manifest_path = get_manifest_path(Path(installed.install_path))
            assert manifest_path.exists()
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_install_snippet_only(self, temp_extensions_dir, snippet_only_manifest, monkeypatch):
        """Install snippet-only extension succeeds."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "snippet-only", snippet_only_manifest, {
                "snippets/c.json": {"for": {"prefix": "for", "body": ["for (int i = 0; i < n; i++) {", "$1", "}"]}}
            })
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            installed = install_vsix(vsix, sha256)

            assert installed.classification == ExtensionClassification.SUPPORTED
            assert len(installed.manifest.snippets) == 1
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_install_js_only_classified_unsupported(self, temp_extensions_dir, js_only_manifest, monkeypatch):
        """JS-only extension classified as UNSUPPORTED."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "js-only", js_only_manifest)
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            installed = install_vsix(vsix, sha256)

            assert installed.classification == ExtensionClassification.UNSUPPORTED
            assert len(installed.manifest.themes) == 0
            assert len(installed.manifest.snippets) == 0
            assert len(installed.manifest.grammars) == 0
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_install_partial_classified_partial(self, temp_extensions_dir, partial_manifest, monkeypatch):
        """Extension with JS + themes classified as PARTIAL."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "partial", partial_manifest, {
                "theme/my.json": {"name": "My", "type": "dark", "colors": {}}
            })
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            installed = install_vsix(vsix, sha256)

            assert installed.classification == ExtensionClassification.PARTIAL
            assert len(installed.manifest.themes) == 1
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_sha256_mismatch_refused(self, temp_extensions_dir, theme_only_manifest, monkeypatch):
        """SHA-256 mismatch refuses installation."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "theme-only", theme_only_manifest)
            wrong_sha256 = "0" * 64

            with pytest.raises(SHA256MismatchError):
                install_vsix(vsix, wrong_sha256)
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_oversize_vsix_refused(self, temp_extensions_dir, monkeypatch):
        """VSIX larger than 50 MB is refused."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        original_limit = installer_mod.MAX_VSIX_SIZE
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            # Patch size limit to small value for test
            installer_mod.MAX_VSIX_SIZE = 500  # Very small limit (500 bytes)
            # Create a VSIX with a large file to exceed 500 bytes
            vsix = create_fixture_vsix(temp_extensions_dir, "large", {"name": "large", "version": "1.0.0"}, {
                "large.bin": "x" * 1000  # 1 KB file
            })
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            with pytest.raises(SizeLimitError):
                install_vsix(vsix, sha256)
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base
            installer_mod.MAX_VSIX_SIZE = original_limit

    def test_uninstall_removes_extension(self, temp_extensions_dir, theme_only_manifest, monkeypatch):
        """Uninstall removes extension directory."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "theme-only", theme_only_manifest)
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            installed = install_vsix(vsix, sha256)
            install_path = Path(installed.install_path)
            assert install_path.exists()

            result = uninstall_extension("test-pub", "theme-only", "1.0.0")
            assert result is True
            assert not install_path.exists()
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_uninstall_nonexistent_returns_false(self, monkeypatch):
        """Uninstall non-existent returns False."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = Path(tempfile.mkdtemp(prefix="medha_test_"))
        try:
            result = uninstall_extension("nonexistent", "ext", "1.0.0")
            assert result is False
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_list_installed_extensions(self, temp_extensions_dir, theme_only_manifest, snippet_only_manifest, monkeypatch):
        """List installed extensions returns all installed."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            # Install two extensions
            vsix1 = create_fixture_vsix(temp_extensions_dir, "theme-only", theme_only_manifest)
            sha256_1 = hashlib.sha256(vsix1.read_bytes()).hexdigest()
            install_vsix(vsix1, sha256_1)

            vsix2 = create_fixture_vsix(temp_extensions_dir, "snippet-only", snippet_only_manifest)
            sha256_2 = hashlib.sha256(vsix2.read_bytes()).hexdigest()
            install_vsix(vsix2, sha256_2)

            installed = list_installed_extensions()
            assert len(installed) == 2
            names = {ext.name for ext in installed}
            assert names == {"theme-only", "snippet-only"}
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_get_enabled_extensions(self, temp_extensions_dir, theme_only_manifest, monkeypatch):
        """Get enabled extensions filters by enabled flag."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "theme-only", theme_only_manifest)
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            installed = install_vsix(vsix, sha256)
            assert len(get_enabled_extensions()) == 1

            set_extension_enabled("test-pub", "theme-only", "1.0.0", False)
            assert len(get_enabled_extensions()) == 0

            set_extension_enabled("test-pub", "theme-only", "1.0.0", True)
            assert len(get_enabled_extensions()) == 1
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base

    def test_get_installed_extension(self, temp_extensions_dir, theme_only_manifest, monkeypatch):
        """Get specific installed extension by ID."""
        import medha.extensions.installer as installer_mod
        original_base = installer_mod.EXTENSIONS_BASE_DIR
        installer_mod.EXTENSIONS_BASE_DIR = temp_extensions_dir
        try:
            vsix = create_fixture_vsix(temp_extensions_dir, "theme-only", theme_only_manifest)
            sha256 = hashlib.sha256(vsix.read_bytes()).hexdigest()

            install_vsix(vsix, sha256)
            ext = get_installed_extension("test-pub", "theme-only", "1.0.0")
            assert ext is not None
            assert ext.name == "theme-only"

            ext = get_installed_extension("test-pub", "nonexistent", "1.0.0")
            assert ext is None
        finally:
            installer_mod.EXTENSIONS_BASE_DIR = original_base


class TestParseExtensionManifest:
    """Tests for parsing package.json."""

    def test_parse_valid_manifest(self, temp_extensions_dir):
        """Parse valid package.json."""
        manifest_data = {
            "name": "test-ext",
            "version": "1.0.0",
            "displayName": "Test Extension",
            "publisher": "test-pub",
            "contributes": {
                "themes": [{"label": "Test", "uiTheme": "vs-dark", "path": "./theme/test.json"}]
            }
        }
        ext_root = temp_extensions_dir / "extension"
        ext_root.mkdir()
        (ext_root / "package.json").write_text(json.dumps(manifest_data))

        manifest = parse_extension_manifest(ext_root)
        assert manifest.name == "test-ext"
        assert manifest.version == "1.0.0"
        assert len(manifest.themes) == 1

    def test_parse_missing_package_json_raises(self, temp_extensions_dir):
        """Missing package.json raises CorruptArchiveError."""
        ext_root = temp_extensions_dir / "extension"
        ext_root.mkdir()
        with pytest.raises(CorruptArchiveError, match="Missing package.json"):
            parse_extension_manifest(ext_root)

    def test_parse_invalid_json_raises(self, temp_extensions_dir):
        """Invalid JSON raises CorruptArchiveError."""
        ext_root = temp_extensions_dir / "extension"
        ext_root.mkdir()
        (ext_root / "package.json").write_text("{ invalid json }")
        with pytest.raises(CorruptArchiveError, match="Invalid JSON"):
            parse_extension_manifest(ext_root)


# =============================================================================
# Run as script
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])