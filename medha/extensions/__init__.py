"""
MEDHA Extensions Package

Open VSX registry integration for themes, snippets, and grammars.
"""
from __future__ import annotations

# Public API
from medha.extensions.models import (
    ExtensionInfo,
    ExtensionDetail,
    ExtensionManifest,
    InstalledExtension,
    ExtensionClassification,
    ThemeContribution,
    SnippetContribution,
    GrammarContribution,
    VSCodeTheme,
    VSCodeSnippet,
)

from medha.extensions.registry import (
    OpenVSXRegistryClient,
    search_extensions,
    get_extension_detail,
    download_extension,
    NetworkError,
    NotFoundError,
    DownloadError,
)

from medha.extensions.installer import (
    install_vsix,
    uninstall_extension,
    list_installed_extensions,
    get_installed_extension,
    set_extension_enabled,
    get_enabled_extensions,
)

from medha.extensions.contributions import (
    load_installed_manifest,
    load_theme_file,
    load_snippets_file,
    load_grammar_file,
    load_all_themes,
    load_all_snippets,
    load_all_grammars,
    classify_extension,
    get_supported_contributions,
    map_vscode_theme_to_medha,
    apply_theme_to_editor,
    get_all_available_themes,
    get_all_available_snippets,
)

__all__ = [
    # Models
    "ExtensionInfo",
    "ExtensionDetail",
    "ExtensionManifest",
    "InstalledExtension",
    "ExtensionClassification",
    "ThemeContribution",
    "SnippetContribution",
    "GrammarContribution",
    "VSCodeTheme",
    "VSCodeSnippet",

    # Registry
    "OpenVSXRegistryClient",
    "search_extensions",
    "get_extension_detail",
    "download_extension",
    "NetworkError",
    "NotFoundError",
    "DownloadError",

    # Installer
    "install_vsix",
    "uninstall_extension",
    "list_installed_extensions",
    "get_installed_extension",
    "set_extension_enabled",
    "get_enabled_extensions",

    # Contributions
    "load_all_themes",
    "load_all_snippets",
    "load_all_grammars",
    "load_extension_contributions",
    "map_vscode_theme_to_medha",
    "apply_theme_to_editor",
    "get_all_available_themes",
    "get_all_available_snippets",
]