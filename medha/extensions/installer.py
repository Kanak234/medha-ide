"""
MEDHA Extensions — Secure VSIX Installer

Handles installation, uninstallation, and listing of extensions.
Security-first: HTTPS only, SHA-256 verification, zip-slip protection, 50 MB limit.
No code execution from extensions — treats .vsix as untrusted data.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import shutil
import tempfile
import time
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Tuple

from medha.extensions.models import (
    ExtensionManifest,
    InstalledExtension,
    ExtensionClassification,
)

logger = logging.getLogger(__name__)

# Base directory for installed extensions
EXTENSIONS_BASE_DIR = Path.home() / ".medha" / "extensions"

# Maximum VSIX size (50 MB)
MAX_VSIX_SIZE = 50 * 1024 * 1024


class InstallError(Exception):
    """Base exception for installer errors."""
    pass


class ZipSlipError(InstallError):
    """Zip-slip attack detected."""
    pass


class SHA256MismatchError(InstallError):
    """SHA-256 verification failed."""
    pass


class SizeLimitError(InstallError):
    """Download size limit exceeded."""
    pass


class CorruptArchiveError(InstallError):
    """Corrupt or invalid VSIX archive."""
    pass


def get_extensions_dir() -> Path:
    """Get the base extensions directory, creating if needed."""
    EXTENSIONS_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return EXTENSIONS_BASE_DIR


def get_install_dir(namespace: str, name: str, version: str) -> Path:
    """Get the installation directory for an extension version."""
    return get_extensions_dir() / f"{namespace}.{name}-{version}"


def get_manifest_path(install_dir: Path) -> Path:
    """Get the path to our manifest.json metadata file."""
    return install_dir / "manifest.json"


def get_extension_root(install_dir: Path) -> Path:
    """Get the path to the unzipped extension/ directory."""
    return install_dir / "extension"


def verify_sha256(filepath: Path, expected_sha256: str) -> bool:
    """
    Verify SHA-256 hash of a file against expected value.

    Args:
        filepath: Path to file to verify
        expected_sha256: Expected SHA-256 hex string

    Returns:
        True if match, False otherwise
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual = sha256.hexdigest().lower()
    expected = expected_sha256.lower()
    return actual == expected


def safe_extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """
    Extract ZIP archive with zip-slip protection.

    Args:
        zip_path: Path to .vsix file
        dest_dir: Destination directory

    Raises:
        ZipSlipError: If any entry tries to escape dest_dir
        CorruptArchiveError: If ZIP is corrupt or invalid
    """
    dest_dir = dest_dir.resolve()

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # First pass: validate all paths
            for member in zf.infolist():
                # Resolve the target path
                target_path = (dest_dir / member.filename).resolve()

                # Check for path traversal (zip-slip)
                try:
                    target_path.relative_to(dest_dir)
                except ValueError:
                    raise ZipSlipError(
                        f"Zip-slip detected: {member.filename} escapes destination"
                    )

            # Second pass: extract all (now safe)
            zf.extractall(dest_dir)

    except zipfile.BadZipFile as e:
        raise CorruptArchiveError(f"Invalid or corrupt VSIX: {e}")


def parse_extension_manifest(extension_root: Path) -> ExtensionManifest:
    """
    Parse package.json from unzipped extension.

    Args:
        extension_root: Path to extension/ directory

    Returns:
        Parsed ExtensionManifest

    Raises:
        CorruptArchiveError: If package.json missing or invalid JSON
    """
    package_json = extension_root / "package.json"
    if not package_json.exists():
        raise CorruptArchiveError("Missing package.json in extension")

    try:
        with open(package_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CorruptArchiveError(f"Invalid JSON in package.json: {e}")

    return ExtensionManifest.from_package_json(data)


def install_vsix(
    vsix_path: Path,
    expected_sha256: Optional[str] = None,
) -> InstalledExtension:
    """
    Install a VSIX extension package.

    Args:
        vsix_path: Path to downloaded .vsix file
        expected_sha256: Expected SHA-256 from registry (optional but recommended)

    Returns:
        InstalledExtension metadata

    Raises:
        InstallError: On any installation failure (cleanup performed)
    """
    # Verify file exists and size
    if not vsix_path.exists():
        raise InstallError(f"VSIX not found: {vsix_path}")

    file_size = vsix_path.stat().st_size
    if file_size > MAX_VSIX_SIZE:
        raise SizeLimitError(f"VSIX exceeds {MAX_VSIX_SIZE / 1024 / 1024} MB limit")

    # Verify SHA-256 if provided
    if expected_sha256:
        if not verify_sha256(vsix_path, expected_sha256):
            raise SHA256MismatchError("SHA-256 verification failed")

    # Create temporary extraction directory
    with tempfile.TemporaryDirectory(prefix="medha_ext_") as tmpdir:
        tmp_extract = Path(tmpdir) / "extract"

        # Extract with zip-slip protection
        safe_extract_zip(vsix_path, tmp_extract)

        # VSIX files have an "extension/" subdirectory containing the actual extension
        extension_root = tmp_extract / "extension"
        if not extension_root.exists():
            # Fallback: maybe the VSIX extracts directly (unusual but possible)
            extension_root = tmp_extract

        # Parse manifest
        manifest = parse_extension_manifest(extension_root)

        # Determine install directory
        install_dir = get_install_dir(manifest.publisher, manifest.name, manifest.version)

        # Clean up any existing installation
        if install_dir.exists():
            shutil.rmtree(install_dir)

        # Move to final location
        install_dir.mkdir(parents=True)
        shutil.move(str(extension_root), str(install_dir / "extension"))

        # Create our metadata manifest
        classification = manifest.classify()
        installed = InstalledExtension(
            namespace=manifest.publisher,
            name=manifest.name,
            version=manifest.version,
            install_path=str(install_dir),
            manifest=manifest,
            classification=classification,
            enabled=True,
            install_time=time.time(),
        )

        # Write manifest.json
        with open(get_manifest_path(install_dir), "w", encoding="utf-8") as f:
            json.dump(installed.to_dict(), f, indent=2)

        logger.info(f"Installed {installed.unique_id} v{manifest.version} to {install_dir}")
        return installed


def uninstall_extension(namespace: str, name: str, version: str) -> bool:
    """
    Uninstall an extension.

    Args:
        namespace: Extension namespace/publisher
        name: Extension name
        version: Extension version

    Returns:
        True if uninstalled, False if not found
    """
    install_dir = get_install_dir(namespace, name, version)
    if not install_dir.exists():
        return False

    shutil.rmtree(install_dir)
    logger.info(f"Uninstalled {namespace}.{name}-{version}")
    return True


def list_installed_extensions() -> List[InstalledExtension]:
    """
    List all installed extensions.

    Returns:
        List of InstalledExtension (only valid ones with readable manifests)
    """
    installed = []
    base_dir = get_extensions_dir()

    for item in base_dir.iterdir():
        if not item.is_dir():
            continue

        manifest_path = get_manifest_path(item)
        if not manifest_path.exists():
            logger.warning(f"Skipping {item.name}: no manifest.json")
            continue

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Re-parse the actual package.json to get fresh manifest
            ext_root = get_extension_root(item)
            if not ext_root.exists():
                logger.warning(f"Skipping {item.name}: extension/ directory missing")
                continue

            manifest = parse_extension_manifest(ext_root)
            installed_ext = InstalledExtension.from_dict(data, manifest)
            installed.append(installed_ext)

        except (json.JSONDecodeError, KeyError, CorruptArchiveError) as e:
            logger.warning(f"Skipping {item.name}: invalid manifest ({e})")
            continue

    return installed


def get_installed_extension(namespace: str, name: str, version: str) -> Optional[InstalledExtension]:
    """Get a specific installed extension by full ID."""
    install_dir = get_install_dir(namespace, name, version)
    manifest_path = get_manifest_path(install_dir)

    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        ext_root = get_extension_root(install_dir)
        manifest = parse_extension_manifest(ext_root)
        return InstalledExtension.from_dict(data, manifest)
    except Exception:
        return None


def set_extension_enabled(namespace: str, name: str, version: str, enabled: bool) -> bool:
    """Enable or disable an installed extension."""
    installed = get_installed_extension(namespace, name, version)
    if not installed:
        return False

    installed.enabled = enabled
    with open(get_manifest_path(Path(installed.install_path)), "w", encoding="utf-8") as f:
        json.dump(installed.to_dict(), f, indent=2)
    return True


def get_enabled_extensions() -> List[InstalledExtension]:
    """Get all enabled installed extensions."""
    return [ext for ext in list_installed_extensions() if ext.enabled]