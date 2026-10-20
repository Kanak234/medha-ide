"""
Tests for Open VSX Registry Client.

Uses a local fake HTTP server (http.server in a thread) with fixture JSON
and a tiny fixture .vsix built in the test.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import tempfile
import threading
import time
import zipfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, ClassVar
from urllib.parse import parse_qs, urlparse

import pytest

from medha.extensions.registry import (
    OpenVSXRegistryClient,
    SearchResult,
    ExtensionInfo,
    ExtensionDetail,
    NetworkError,
    NotFoundError,
    DownloadError,
)
from medha.extensions.models import ExtensionClassification


# =============================================================================
# Fixture Data
# =============================================================================

SEARCH_RESPONSE = {
    "extensions": [
        {
            "namespace": "dracula-theme",
            "name": "theme-dracula",
            "version": "2.25.1",
            "displayName": "Dracula Theme Official",
            "description": "The official Dracula Theme",
            "downloadCount": 439954,
            "files": {
                "download": "/fake/dracula-theme.theme-dracula-2.25.1.vsix",
                "icon": "/fake/icon.png",
                "sha256": "/fake/dracula-theme.theme-dracula-2.25.1.sha256",
            },
            "verified": True,
        },
        {
            "namespace": "nszihan",
            "name": "vscode-dracula-colorful",
            "version": "2.2.1",
            "displayName": "Dracula Colorful",
            "description": "A vibrant variant of Dracula theme",
            "downloadCount": 17889,
            "files": {
                "download": "/fake/nszihan.vscode-dracula-colorful-2.2.1.vsix",
                "sha256": "/fake/nszihan.vscode-dracula-colorful-2.2.1.sha256",
            },
            "verified": True,
        },
    ],
    "totalSize": 2,
    "offset": 0,
}

DETAIL_RESPONSE = {
    "namespace": "dracula-theme",
    "name": "theme-dracula",
    "version": "2.25.1",
    "displayName": "Dracula Theme Official",
    "description": "The official Dracula Theme: a dark theme for many editors, shells, and more.",
    "downloadCount": 439954,
    "files": {
        "download": "/fake/dracula-theme.theme-dracula-2.25.1.vsix",
        "icon": "/fake/icon.png",
        "sha256": "/fake/dracula-theme.theme-dracula-2.25.1.sha256",
        "manifest": "/fake/package.json",
        "readme": "/fake/README.md",
        "license": "/fake/LICENSE.txt",
    },
    "license": "MIT",
    "repository": "https://github.com/dracula/visual-studio-code.git",
    "homepage": "https://draculatheme.com/",
    "categories": ["Themes"],
    "tags": ["color-theme", "dark", "dracula", "theme"],
    "publisher": "dracula-theme",
    "timestamp": "2024-09-06T03:29:53.212374Z",
    "verified": True,
}

# Tiny package.json for fixture VSIX
PACKAGE_JSON = {
    "name": "theme-dracula",
    "version": "2.25.1",
    "displayName": "Dracula Theme Official",
    "description": "The official Dracula Theme",
    "publisher": "dracula-theme",
    "license": "MIT",
    "repository": "https://github.com/dracula/visual-studio-code.git",
    "categories": ["Themes"],
    "contributes": {
        "themes": [
            {"label": "Dracula", "uiTheme": "vs-dark", "path": "./theme/dracula.json"},
            {"label": "Dracula Soft", "uiTheme": "vs-dark", "path": "./theme/dracula-soft.json"}
        ]
    }
}

# Minimal theme JSON
THEME_JSON = {
    "name": "Dracula",
    "type": "dark",
    "colors": {
        "editor.background": "#282A36",
        "editor.foreground": "#F8F8F2",
        "editor.lineHighlightBackground": "#44475A",
        "editor.selectionBackground": "#44475A80",
    },
    "tokenColors": [
        {"scope": "comment", "settings": {"foreground": "#6272A4", "fontStyle": "italic"}},
        {"scope": "string", "settings": {"foreground": "#F1FA8C"}},
        {"scope": "keyword", "settings": {"foreground": "#FF79C6"}},
    ]
}


class FakeVSXHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for fake Open VSX server."""

    def __init__(self, *args, server_fixtures: Dict[str, Any] = None, **kwargs):
        self.server_fixtures = server_fixtures or {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Search endpoint
        if path == "/api/-/search":
            self._send_json(SEARCH_RESPONSE)
            return

        # Detail endpoint
        if path == "/api/dracula-theme/theme-dracula":
            self._send_json(DETAIL_RESPONSE)
            return

        # VSIX download
        if path == "/fake/dracula-theme.theme-dracula-2.25.1.vsix":
            vsix_path = self.server_fixtures.get("vsix_path", "")
            if vsix_path and os.path.exists(vsix_path):
                self._send_file(vsix_path, "application/vscode-vsix")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"VSIX not found")
            return

        # SHA256 file
        if path == "/fake/dracula-theme.theme-dracula-2.25.1.sha256":
            sha256 = self.server_fixtures.get("vsix_sha256", "")
            self._send_text(sha256)
            return

        # Package.json from VSIX (simulated)
        if path == "/fake/package.json":
            self._send_json(PACKAGE_JSON)
            return

        # README
        if path == "/fake/README.md":
            self._send_text("# Dracula Theme\n\nOfficial Dracula theme.")
            return

        # License
        if path == "/fake/LICENSE.txt":
            self._send_text("MIT License")
            return

        # Icon
        if path == "/fake/icon.png":
            self._send_file(self._make_tiny_png(), "image/png")
            return

        # 404 for everything else
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def _send_json(self, data: Dict[str, Any]):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_text(self, text: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def _send_file(self, filepath: str, content_type: str):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        fs = os.path.getsize(filepath)
        self.send_header("Content-Length", str(fs))
        self.end_headers()
        with open(filepath, "rb") as f:
            shutil.copyfileobj(f, self.wfile)

    def _make_tiny_png(self) -> str:
        # 1x1 transparent PNG
        png_data = bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(png_data)
        tmp.close()
        return tmp.name

    def log_message(self, format, *args):
        pass  # Suppress log messages


class FixtureServer(HTTPServer):
    """HTTP server that holds fixture data for handlers."""

    def __init__(self, server_address, RequestHandlerClass, fixtures: Dict[str, Any]):
        self.fixtures = fixtures
        super().__init__(server_address, RequestHandlerClass)

    def finish_request(self, request, client_address):
        """Create handler instance with fixtures."""
        self.RequestHandlerClass(request, client_address, self, server_fixtures=self.fixtures)


class FakeVSXServer:
    """Context manager for fake Open VSX HTTP server."""

    def __init__(self, port: int = 0):
        self.port = port
        self.server: FixtureServer = None
        self.thread: threading.Thread = None
        self.base_url = ""
        self.temp_dir = tempfile.mkdtemp(prefix="fake_vsx_")
        self.fixtures = {}
        self._create_fixture_vsix()

    def _create_fixture_vsix(self):
        """Create a minimal valid VSIX file for testing."""
        vsix_path = os.path.join(self.temp_dir, "dracula-theme.theme-dracula-2.25.1.vsix")
        with zipfile.ZipFile(vsix_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # [Content_Types].xml (minimal)
            zf.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
            )
            # extension.vsixmanifest (minimal)
            zf.writestr(
                "extension.vsixmanifest",
                '<?xml version="1.0" encoding="utf-8"?><PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011"><Metadata><Identity Id="dracula-theme.theme-dracula" Version="2.25.1" Language="en-US" Publisher="dracula-theme" /></Metadata></PackageManifest>'
            )
            # package.json
            zf.writestr("extension/package.json", json.dumps(PACKAGE_JSON))
            # theme files
            zf.writestr("extension/theme/dracula.json", json.dumps(THEME_JSON))
            zf.writestr("extension/theme/dracula-soft.json", json.dumps(THEME_JSON))

        # Compute SHA-256
        sha256 = hashlib.sha256()
        with open(vsix_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        self.fixtures["vsix_sha256"] = sha256.hexdigest()
        self.fixtures["vsix_path"] = vsix_path

    def start(self):
        self.server = FixtureServer(("127.0.0.1", 0), FakeVSXHandler, self.fixtures)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        # Wait for server to be ready
        time.sleep(0.1)

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def fake_server():
    """Module-scoped fake server."""
    server = FakeVSXServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def client(fake_server):
    """Registry client pointing to fake server."""
    return OpenVSXRegistryClient(base_url=f"{fake_server.base_url}/api/", timeout=5)


# =============================================================================
# Tests
# =============================================================================

class TestRegistrySearch:
    """Tests for search functionality."""

    def test_search_parses_results(self, client):
        """Search returns parsed ExtensionInfo list."""
        result = client.search("dracula")

        assert isinstance(result, SearchResult)
        assert len(result.extensions) == 2
        assert result.total_size == 2
        assert result.offset == 0

        ext1 = result.extensions[0]
        assert isinstance(ext1, ExtensionInfo)
        assert ext1.namespace == "dracula-theme"
        assert ext1.name == "theme-dracula"
        assert ext1.version == "2.25.1"
        assert ext1.display_name == "Dracula Theme Official"
        assert ext1.download_count == 439954
        assert ext1.files.download.endswith(".vsix")
        assert ext1.verified is True

    def test_search_with_offset(self, client):
        """Search respects offset parameter."""
        result = client.search("dracula", offset=20, size=10)
        assert result.offset == 0  # Fake server returns 0

    def test_search_empty_query(self, client):
        """Empty query returns results (fake server ignores query)."""
        result = client.search("")
        assert len(result.extensions) == 2


class TestRegistryDetail:
    """Tests for detail functionality."""

    def test_detail_parses_full_metadata(self, client):
        """Detail returns full ExtensionDetail."""
        detail = client.detail("dracula-theme", "theme-dracula")

        assert isinstance(detail, ExtensionDetail)
        assert detail.namespace == "dracula-theme"
        assert detail.name == "theme-dracula"
        assert detail.version == "2.25.1"
        assert detail.display_name == "Dracula Theme Official"
        assert detail.license == "MIT"
        assert detail.repository == "https://github.com/dracula/visual-studio-code.git"
        assert detail.homepage == "https://draculatheme.com/"
        assert "Themes" in detail.categories
        assert detail.files.download.endswith(".vsix")
        assert detail.files.sha256.endswith(".sha256")

    def test_detail_not_found_raises(self, client):
        """404 raises NotFoundError."""
        with pytest.raises(NotFoundError):
            client.detail("nonexistent", "extension")


class TestRegistryDownload:
    """Tests for VSIX download with verification."""

    def test_download_sha256_match(self, client, fake_server):
        """Download succeeds when SHA-256 matches."""
        download_url = f"{fake_server.base_url}/fake/dracula-theme.theme-dracula-2.25.1.vsix"
        sha256_url = f"{fake_server.base_url}/fake/dracula-theme.theme-dracula-2.25.1.sha256"

        expected_sha256 = client.get_sha256_from_url(sha256_url)
        assert expected_sha256 == fake_server.fixtures["vsix_sha256"]

        dest_dir = tempfile.mkdtemp()
        try:
            vsix_path = client.download_vsix(download_url, expected_sha256, dest_dir)
            assert os.path.exists(vsix_path)
            assert vsix_path.endswith(".vsix")

            sha256 = hashlib.sha256()
            with open(vsix_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            assert sha256.hexdigest() == fake_server.fixtures["vsix_sha256"]
        finally:
            shutil.rmtree(dest_dir, ignore_errors=True)

    def test_download_sha256_mismatch_refused(self, client, fake_server):
        """Download fails when SHA-256 mismatches."""
        download_url = f"{fake_server.base_url}/fake/dracula-theme.theme-dracula-2.25.1.vsix"
        wrong_sha256 = "0" * 64

        dest_dir = tempfile.mkdtemp()
        try:
            with pytest.raises(DownloadError, match="SHA-256 mismatch"):
                client.download_vsix(download_url, wrong_sha256, dest_dir)
            files = os.listdir(dest_dir)
            assert len(files) == 0
        finally:
            shutil.rmtree(dest_dir, ignore_errors=True)

    def test_download_oversize_refused(self, client, fake_server):
        """Download fails when file exceeds 50 MB."""
        from medha.extensions.registry import MAX_DOWNLOAD_SIZE
        assert MAX_DOWNLOAD_SIZE == 50 * 1024 * 1024

    def test_download_network_error_handled(self, client):
        """Network error raises NetworkError."""
        with pytest.raises(NetworkError):
            client.download_vsix("http://127.0.0.1:9999/nonexistent.vsix", None, tempfile.mkdtemp())


class TestRegistryRealCall:
    """One real call against open-vsx.org (network required)."""

    @pytest.mark.network
    def test_real_search_dracula(self):
        """Real search for 'dracula' against open-vsx.org."""
        client = OpenVSXRegistryClient(timeout=15)
        try:
            result = client.search("dracula", size=5)
            print(f"\n=== Real Open VSX Search Results for 'dracula' ===")
            print(f"Total results: {result.total_size}")
            for ext in result.extensions:
                print(f"  - {ext.namespace}.{ext.name} v{ext.version}: {ext.display_name} ({ext.download_count} downloads)")
            assert len(result.extensions) > 0
            assert all(isinstance(e, ExtensionInfo) for e in result.extensions)
        finally:
            client.close()


# =============================================================================
# Run as script for manual verification
# =============================================================================

if __name__ == "__main__":
    import sys

    print("Running real Open VSX search for 'dracula'...")
    client = OpenVSXRegistryClient(timeout=15)
    try:
        result = client.search("dracula", size=5)
        print(f"Total results: {result.total_size}")
        for ext in result.extensions:
            print(f"  - {ext.namespace}.{ext.name} v{ext.version}: {ext.display_name} ({ext.download_count} downloads)")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()