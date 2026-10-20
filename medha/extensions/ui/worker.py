"""
MEDHA Extensions — Qt Worker Threads

Background threads for network operations to keep UI responsive.
All network calls run off the UI thread with 10s timeout.
"""
from __future__ import annotations
import logging
from typing import Optional, List

from PySide6.QtCore import QThread, Signal

from medha.extensions.registry import (
    OpenVSXRegistryClient,
    SearchResult,
    ExtensionDetail,
    ExtensionInfo,
    NetworkError,
    NotFoundError,
    DownloadError,
)
from medha.extensions.models import ExtensionClassification
from medha.extensions.installer import (
    install_vsix,
    uninstall_extension,
    list_installed_extensions,
    get_enabled_extensions,
    set_extension_enabled,
)
from medha.extensions.contributions import (
    load_all_themes,
    load_all_snippets,
    get_all_available_themes,
    get_all_available_snippets,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Base Worker
# =============================================================================

class BaseWorker(QThread):
    """Base worker with common error handling."""

    error = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled


# =============================================================================
# Registry Workers
# =============================================================================

class SearchWorker(BaseWorker):
    """Worker for searching extensions."""

    results_ready = Signal(object)  # SearchResult

    def __init__(self, query: str, offset: int = 0, size: int = 20, base_url: str = None):
        super().__init__()
        self.query = query
        self.offset = offset
        self.size = size
        self.base_url = base_url

    def run(self):
        try:
            client = OpenVSXRegistryClient(base_url=self.base_url) if self.base_url else OpenVSXRegistryClient()
            result = client.search(self.query, self.offset, self.size)
            if not self._cancelled:
                self.results_ready.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Search failed: {e}")
        finally:
            self.finished.emit()


class DetailWorker(BaseWorker):
    """Worker for fetching extension details."""

    detail_ready = Signal(object)  # ExtensionDetail

    def __init__(self, namespace: str, name: str, base_url: str = None):
        super().__init__()
        self.namespace = namespace
        self.name = name
        self.base_url = base_url

    def run(self):
        try:
            client = OpenVSXRegistryClient(base_url=self.base_url) if self.base_url else OpenVSXRegistryClient()
            detail = client.detail(self.namespace, self.name)
            if not self._cancelled:
                self.detail_ready.emit(detail)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Detail fetch failed: {e}")
        finally:
            self.finished.emit()


class DownloadWorker(BaseWorker):
    """Worker for downloading VSIX files."""

    download_finished = Signal(str)  # local file path
    progress = Signal(int, int)  # bytes_downloaded, total_bytes

    def __init__(
        self,
        download_url: str,
        expected_sha256: str = None,
        dest_dir: str = None,
        base_url: str = None,
    ):
        super().__init__()
        self.download_url = download_url
        self.expected_sha256 = expected_sha256
        self.dest_dir = dest_dir
        self.base_url = base_url

    def run(self):
        try:
            client = OpenVSXRegistryClient(base_url=self.base_url) if self.base_url else OpenVSXRegistryClient()

            # Resolve SHA-256 URL if needed
            sha256 = self.expected_sha256
            if sha256 and sha256.startswith("http"):
                sha256 = client.get_sha256_from_url(sha256)

            filepath = client.download_vsix(self.download_url, sha256, self.dest_dir)
            if not self._cancelled:
                self.download_finished.emit(filepath)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Download failed: {e}")
        finally:
            self.finished.emit()


# =============================================================================
# Installer Workers
# =============================================================================

class InstallWorker(BaseWorker):
    """Worker for installing extensions."""

    install_finished = Signal(object)  # InstalledExtension

    def __init__(self, vsix_path: str, expected_sha256: str = None):
        super().__init__()
        self.vsix_path = vsix_path
        self.expected_sha256 = expected_sha256

    def run(self):
        try:
            from pathlib import Path
            installed = install_vsix(Path(self.vsix_path), self.expected_sha256)
            if not self._cancelled:
                self.install_finished.emit(installed)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Install failed: {e}")
        finally:
            self.finished.emit()


class UninstallWorker(BaseWorker):
    """Worker for uninstalling extensions."""

    uninstall_finished = Signal(bool)

    def __init__(self, namespace: str, name: str, version: str):
        super().__init__()
        self.namespace = namespace
        self.name = name
        self.version = version

    def run(self):
        try:
            result = uninstall_extension(self.namespace, self.name, self.version)
            if not self._cancelled:
                self.uninstall_finished.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Uninstall failed: {e}")
        finally:
            self.finished.emit()


class ListInstalledWorker(BaseWorker):
    """Worker for listing installed extensions."""

    list_ready = Signal(list)  # List[InstalledExtension]

    def run(self):
        try:
            installed = list_installed_extensions()
            if not self._cancelled:
                self.list_ready.emit(installed)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"List failed: {e}")
        finally:
            self.finished.emit()


class ToggleEnabledWorker(BaseWorker):
    """Worker for enabling/disabling extensions."""

    toggle_finished = Signal(bool)

    def __init__(self, namespace: str, name: str, version: str, enabled: bool):
        super().__init__()
        self.namespace = namespace
        self.name = name
        self.version = version
        self.enabled = enabled

    def run(self):
        try:
            result = set_extension_enabled(self.namespace, self.name, self.version, self.enabled)
            if not self._cancelled:
                self.toggle_finished.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Toggle failed: {e}")
        finally:
            self.finished.emit()


# =============================================================================
# Contribution Workers
# =============================================================================

class LoadThemesWorker(BaseWorker):
    """Worker for loading all available themes."""

    themes_ready = Signal(list)  # List[(InstalledExtension, VSCodeTheme)]

    def run(self):
        try:
            themes = get_all_available_themes()
            if not self._cancelled:
                self.themes_ready.emit(themes)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Load themes failed: {e}")
        finally:
            self.finished.emit()


class LoadSnippetsWorker(BaseWorker):
    """Worker for loading all available snippets."""

    snippets_ready = Signal(dict)  # Dict[language, Dict[name, VSCodeSnippet]]

    def __init__(self, language: str = None):
        super().__init__()
        self.language = language

    def run(self):
        try:
            snippets = get_all_available_snippets(self.language)
            if not self._cancelled:
                self.snippets_ready.emit(snippets)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Load snippets failed: {e}")
        finally:
            self.finished.emit()


class ApplyThemeWorker(BaseWorker):
    """Worker for applying a theme to the editor."""

    theme_applied = Signal(object)  # dict of color mappings

    def __init__(self, theme: object):  # VSCodeTheme
        super().__init__()
        self.theme = theme

    def run(self):
        try:
            from medha.extensions.contributions import map_vscode_theme_to_qt
            colors = map_vscode_theme_to_qt(self.theme)
            if not self._cancelled:
                self.theme_applied.emit(colors)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(f"Apply theme failed: {e}")
        finally:
            self.finished.emit()