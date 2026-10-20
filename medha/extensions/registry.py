"""
MEDHA Extensions — Open VSX Registry Client

Pure Python HTTP client for Open VSX registry.
No Qt dependencies — testable in isolation.
All network calls have 10 second timeout.
"""
from __future__ import annotations
import json
import hashlib
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional, List, Tuple
from urllib.parse import urlencode, urljoin

import requests

from medha.extensions.models import ExtensionInfo, ExtensionDetail, ExtensionFileRef

logger = logging.getLogger(__name__)

# Open VSX API base URL
OPEN_VSX_API_BASE = "https://open-vsx.org/api/"

# Maximum download size (50 MB)
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024

# Request timeout (10 seconds)
REQUEST_TIMEOUT = 10


class RegistryError(Exception):
    """Base exception for registry errors."""
    pass


class NetworkError(RegistryError):
    """Network-related error."""
    pass


class NotFoundError(RegistryError):
    """Extension not found."""
    pass


class ValidationError(RegistryError):
    """Data validation error."""
    pass


class DownloadError(RegistryError):
    """Download/verification error."""
    pass


@dataclass
class SearchResult:
    """Search results container."""
    extensions: List[ExtensionInfo]
    total_size: int
    offset: int


class OpenVSXRegistryClient:
    """
    Pure Python client for Open VSX registry.

    Usage:
        client = OpenVSXRegistryClient()
        results = client.search("dracula")
        detail = client.detail("dracula-theme", "theme-dracula")
        vsix_path = client.download(detail.files.download, detail.files.sha256)
    """

    def __init__(self, base_url: str = OPEN_VSX_API_BASE, timeout: int = REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()
        # Set a reasonable user agent
        self.session.headers.update({
            "User-Agent": "MEDHA-IDE/1.0 (OpenVSX Client)",
            "Accept": "application/json",
        })

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with timeout and error handling."""
        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout}s: {url}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Resource not found: {url}")
            raise NetworkError(f"HTTP error {e.response.status_code}: {e}")

    def search(self, query: str, offset: int = 0, size: int = 20) -> SearchResult:
        """
        Search extensions on Open VSX.

        Args:
            query: Search query string
            offset: Pagination offset
            size: Number of results (max 50)

        Returns:
            SearchResult with extensions list and metadata
        """
        params = {
            "query": query,
            "offset": offset,
            "size": min(size, 50),  # API max is typically 50
        }
        url = f"{self.base_url}-/search?{urlencode(params)}"

        response = self._request("GET", url)
        data = response.json()

        extensions = [
            ExtensionInfo.from_search_result(item)
            for item in data.get("extensions", [])
        ]

        return SearchResult(
            extensions=extensions,
            total_size=data.get("totalSize", 0),
            offset=data.get("offset", 0),
        )

    def detail(self, namespace: str, name: str) -> ExtensionDetail:
        """
        Get detailed extension information.

        Args:
            namespace: Extension publisher/namespace
            name: Extension name

        Returns:
            ExtensionDetail with full metadata
        """
        url = f"{self.base_url}{namespace}/{name}"
        response = self._request("GET", url)
        data = response.json()
        return ExtensionDetail.from_detail_response(data)

    def download_vsix(
        self,
        download_url: str,
        expected_sha256: Optional[str] = None,
        dest_dir: Optional[str] = None,
    ) -> str:
        """
        Download a VSIX file with streaming, size limit, and SHA-256 verification.

        Args:
            download_url: Full URL to the .vsix file
            expected_sha256: Expected SHA-256 hex string (from registry)
            dest_dir: Destination directory (default: temp dir)

        Returns:
            Path to downloaded .vsix file

        Raises:
            DownloadError: On size limit exceeded, SHA-256 mismatch
            NetworkError: On network/connection error
        """
        if dest_dir is None:
            dest_dir = tempfile.gettempdir()

        os.makedirs(dest_dir, exist_ok=True)

        # Stream download to avoid loading entire file in memory
        try:
            response = self.session.get(download_url, stream=True, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise NetworkError(f"Download timeout after {self.timeout}s: {download_url}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error during download: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"VSIX not found: {download_url}")
            raise NetworkError(f"HTTP error {e.response.status_code}: {e}")

        # Determine filename from URL or Content-Disposition
        filename = self._extract_filename(response, download_url)
        filepath = os.path.join(dest_dir, filename)

        # Incremental SHA-256 and size tracking
        sha256 = hashlib.sha256()
        total_size = 0

        try:
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        total_size += len(chunk)
                        if total_size > MAX_DOWNLOAD_SIZE:
                            raise DownloadError(
                                f"Download exceeds {MAX_DOWNLOAD_SIZE / 1024 / 1024} MB limit"
                            )
                        sha256.update(chunk)
                        f.write(chunk)
        except Exception as e:
            # Clean up partial download on any error
            if os.path.exists(filepath):
                os.remove(filepath)
            raise DownloadError(f"Download failed: {e}")

        # Verify SHA-256 if provided
        if expected_sha256:
            actual_sha256 = sha256.hexdigest()
            # Registry may provide SHA-256 as URL to .sha256 file or direct hex
            expected_hex = self._resolve_sha256(expected_sha256)
            if actual_sha256.lower() != expected_hex.lower():
                os.remove(filepath)
                raise DownloadError(
                    f"SHA-256 mismatch: expected {expected_hex}, got {actual_sha256}"
                )
            logger.info(f"SHA-256 verified for {filename}")

        logger.info(f"Downloaded {filename} ({total_size} bytes) to {filepath}")
        return filepath

    def _extract_filename(self, response: requests.Response, url: str) -> str:
        """Extract filename from response headers or URL."""
        # Try Content-Disposition header
        cd = response.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            # Simple extraction: filename="name.vsix"
            import re
            match = re.search(r'filename="?([^";]+)"?', cd)
            if match:
                return match.group(1)

        # Fallback to URL basename
        return os.path.basename(url).split("?")[0] or "extension.vsix"

    def _resolve_sha256(self, sha256_ref: str) -> str:
        """
        Resolve SHA-256 reference to hex string.

        Open VSX provides SHA-256 as either:
        - Direct hex string
        - URL to a .sha256 file containing the hex

        This handles both cases.
        """
        if not sha256_ref:
            return ""

        # If it looks like a URL, fetch it
        if sha256_ref.startswith("http"):
            try:
                resp = self._request("GET", sha256_ref)
                return resp.text.strip()
            except Exception as e:
                logger.warning(f"Failed to fetch SHA-256 from {sha256_ref}: {e}")
                return ""

        # Otherwise assume it's already a hex string
        return sha256_ref.strip()

    def get_sha256_from_url(self, sha256_url: str) -> str:
        """Fetch SHA-256 hex from a .sha256 URL."""
        return self._resolve_sha256(sha256_url)

    def close(self):
        """Close the underlying session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for simple usage
def search_extensions(query: str, offset: int = 0, size: int = 20) -> SearchResult:
    """Convenience function for one-off searches."""
    with OpenVSXRegistryClient() as client:
        return client.search(query, offset, size)


def get_extension_detail(namespace: str, name: str) -> ExtensionDetail:
    """Convenience function for one-off detail fetch."""
    with OpenVSXRegistryClient() as client:
        return client.detail(namespace, name)


def download_extension(
    download_url: str,
    expected_sha256: Optional[str] = None,
    dest_dir: Optional[str] = None,
) -> str:
    """Convenience function for one-off download."""
    with OpenVSXRegistryClient() as client:
        return client.download_vsix(download_url, expected_sha256, dest_dir)