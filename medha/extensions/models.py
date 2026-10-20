"""
MEDHA Extensions — Data Models

Pure Python dataclasses for extension metadata, contributions, and classification.
No Qt dependencies — testable in isolation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class ExtensionClassification(Enum):
    """Classification of an extension based on its contributions."""
    SUPPORTED = "supported"      # Only declarative: themes, snippets, grammars
    PARTIAL = "partial"          # Declarative + JS code (JS ignored)
    UNSUPPORTED = "unsupported"  # Only JS code (no declarative contributions)


@dataclass
class ExtensionFileRef:
    """File references from Open VSX API response."""
    download: Optional[str] = None
    icon: Optional[str] = None
    sha256: Optional[str] = None
    signature: Optional[str] = None
    manifest: Optional[str] = None
    readme: Optional[str] = None
    changelog: Optional[str] = None
    license: Optional[str] = None
    vsixmanifest: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtensionFileRef":
        return cls(
            download=data.get("download"),
            icon=data.get("icon"),
            sha256=data.get("sha256"),
            signature=data.get("signature"),
            manifest=data.get("manifest"),
            readme=data.get("readme"),
            changelog=data.get("changelog"),
            license=data.get("license"),
            vsixmanifest=data.get("vsixmanifest"),
        )


@dataclass
class ExtensionInfo:
    """Lightweight extension info from search results."""
    namespace: str
    name: str
    version: str
    display_name: str
    description: str
    download_count: int
    files: ExtensionFileRef
    verified: bool = False

    @property
    def unique_id(self) -> str:
        return f"{self.namespace}.{self.name}"

    @property
    def full_id(self) -> str:
        return f"{self.namespace}.{self.name}-{self.version}"

    @classmethod
    def from_search_result(cls, data: Dict[str, Any]) -> "ExtensionInfo":
        files = ExtensionFileRef.from_dict(data.get("files", {}))
        return cls(
            namespace=data.get("namespace", ""),
            name=data.get("name", ""),
            version=data.get("version", ""),
            display_name=data.get("displayName", data.get("name", "")),
            description=data.get("description", ""),
            download_count=data.get("downloadCount", 0),
            files=files,
            verified=data.get("verified", False),
        )


@dataclass
class ExtensionDetail(ExtensionInfo):
    """Full extension detail from Open VSX API."""
    license: str = ""
    repository: str = ""
    homepage: str = ""
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    readme_content: str = ""
    publisher: str = ""
    timestamp: str = ""

    @classmethod
    def from_detail_response(cls, data: Dict[str, Any]) -> "ExtensionDetail":
        files = ExtensionFileRef.from_dict(data.get("files", {}))
        return cls(
            namespace=data.get("namespace", ""),
            name=data.get("name", ""),
            version=data.get("version", ""),
            display_name=data.get("displayName", data.get("name", "")),
            description=data.get("description", ""),
            download_count=data.get("downloadCount", 0),
            files=files,
            verified=data.get("verified", False),
            license=data.get("license", ""),
            repository=data.get("repository", ""),
            homepage=data.get("homepage", ""),
            categories=data.get("categories", []),
            tags=data.get("tags", []),
            publisher=data.get("publisher", ""),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class ThemeContribution:
    """A single theme contribution from package.json."""
    label: str
    ui_theme: str  # "vs-dark", "vs-light", "hc-black"
    path: str      # relative path to theme JSON file

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThemeContribution":
        return cls(
            label=data.get("label", "Unnamed Theme"),
            ui_theme=data.get("uiTheme", "vs-dark"),
            path=data.get("path", ""),
        )


@dataclass
class SnippetContribution:
    """A single snippet contribution from package.json."""
    language: str
    path: str  # relative path to snippet JSON file

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SnippetContribution":
        return cls(
            language=data.get("language", ""),
            path=data.get("path", ""),
        )


@dataclass
class GrammarContribution:
    """A single grammar contribution from package.json."""
    language: str
    scope_name: str
    path: str  # relative path to grammar JSON/plist file
    embedded_languages: Dict[str, str] = field(default_factory=dict)
    file_types: List[str] = field(default_factory=list)
    injection_selector: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GrammarContribution":
        return cls(
            language=data.get("language", ""),
            scope_name=data.get("scopeName", ""),
            path=data.get("path", ""),
            embedded_languages=data.get("embeddedLanguages", {}),
            file_types=data.get("fileTypes", []),
            injection_selector=data.get("injectionSelector", ""),
        )


@dataclass
class ExtensionManifest:
    """Parsed package.json from an extension's VSIX."""
    name: str
    version: str
    display_name: str
    description: str
    publisher: str
    license: str = ""
    repository: str = ""
    homepage: str = ""
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    engines: Dict[str, str] = field(default_factory=dict)
    contributes: Dict[str, Any] = field(default_factory=dict)
    main: str = ""  # JS entry point (we ignore this)
    browser: str = ""  # Web entry point (we ignore this)

    # Parsed contributions
    themes: List[ThemeContribution] = field(default_factory=list)
    snippets: List[SnippetContribution] = field(default_factory=list)
    grammars: List[GrammarContribution] = field(default_factory=list)

    @classmethod
    def from_package_json(cls, data: Dict[str, Any]) -> "ExtensionManifest":
        manifest = cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            display_name=data.get("displayName", data.get("name", "")),
            description=data.get("description", ""),
            publisher=data.get("publisher", ""),
            license=data.get("license", ""),
            repository=data.get("repository", {}).get("url", "") if isinstance(data.get("repository"), dict) else data.get("repository", ""),
            homepage=data.get("homepage", ""),
            categories=data.get("categories", []),
            keywords=data.get("keywords", []),
            engines=data.get("engines", {}),
            contributes=data.get("contributes", {}),
            main=data.get("main", ""),
            browser=data.get("browser", ""),
        )
        # Parse declarative contributions
        for t in manifest.contributes.get("themes", []):
            manifest.themes.append(ThemeContribution.from_dict(t))
        for s in manifest.contributes.get("snippets", []):
            manifest.snippets.append(SnippetContribution.from_dict(s))
        for g in manifest.contributes.get("grammars", []):
            manifest.grammars.append(GrammarContribution.from_dict(g))
        return manifest

    def classify(self) -> ExtensionClassification:
        """Classify extension based on contributions vs JS code."""
        has_declarative = bool(self.themes or self.snippets or self.grammars)
        has_js_code = bool(self.main or self.browser)

        if has_declarative and not has_js_code:
            return ExtensionClassification.SUPPORTED
        elif has_declarative and has_js_code:
            return ExtensionClassification.PARTIAL
        else:
            return ExtensionClassification.UNSUPPORTED


@dataclass
class InstalledExtension:
    """Metadata for an installed extension on disk."""
    namespace: str
    name: str
    version: str
    install_path: str  # ~/.medha/extensions/<namespace>.<name>-<version>/
    manifest: ExtensionManifest
    classification: ExtensionClassification
    enabled: bool = True
    install_time: float = 0.0  # Unix timestamp

    @property
    def unique_id(self) -> str:
        return f"{self.namespace}.{self.name}"

    @property
    def full_id(self) -> str:
        return f"{self.namespace}.{self.name}-{self.version}"

    @property
    def extension_root(self) -> str:
        """Path to the unzipped extension/ directory."""
        return f"{self.install_path}/extension"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespace": self.namespace,
            "name": self.name,
            "version": self.version,
            "install_path": self.install_path,
            "manifest": {
                "name": self.manifest.name,
                "version": self.manifest.version,
                "display_name": self.manifest.display_name,
                "description": self.manifest.description,
                "publisher": self.manifest.publisher,
                "themes": [{"label": t.label, "ui_theme": t.ui_theme, "path": t.path} for t in self.manifest.themes],
                "snippets": [{"language": s.language, "path": s.path} for s in self.manifest.snippets],
                "grammars": [{"language": g.language, "scope_name": g.scope_name, "path": g.path} for g in self.manifest.grammars],
            },
            "classification": self.classification.value,
            "enabled": self.enabled,
            "install_time": self.install_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], manifest: ExtensionManifest) -> "InstalledExtension":
        return cls(
            namespace=data["namespace"],
            name=data["name"],
            version=data["version"],
            install_path=data["install_path"],
            manifest=manifest,
            classification=ExtensionClassification(data["classification"]),
            enabled=data.get("enabled", True),
            install_time=data.get("install_time", 0.0),
        )


# VS Code Theme JSON structure (subset we care about)
@dataclass
class VSCodeTheme:
    """Parsed VS Code color theme JSON."""
    name: str
    type: str  # "dark", "light", "hc"
    colors: Dict[str, str] = field(default_factory=dict)  # Workbench colors
    token_colors: List[Dict[str, Any]] = field(default_factory=list)  # Semantic token colors
    semantic_highlighting: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VSCodeTheme":
        return cls(
            name=data.get("name", "Unnamed"),
            type=data.get("type", "dark"),
            colors=data.get("colors", {}),
            token_colors=data.get("tokenColors", []),
            semantic_highlighting=data.get("semanticHighlighting", False),
        )


# VS Code Snippet structure
@dataclass
class VSCodeSnippet:
    """A single snippet definition."""
    prefix: str
    body: List[str]  # Lines of snippet body
    description: str = ""
    scope: str = ""  # Language scope, optional

    @classmethod
    def from_dict(cls, key: str, data: Dict[str, Any]) -> "VSCodeSnippet":
        body = data.get("body", [])
        if isinstance(body, str):
            body = [body]
        return cls(
            prefix=data.get("prefix", key),
            body=body,
            description=data.get("description", ""),
            scope=data.get("scope", ""),
        )