"""
Tests for Extension Contributions Loader.

Tests theme mapping, editor theme application, and snippet expansion.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

from medha.extensions.contributions import (
    map_vscode_theme_to_medha,
    apply_theme_to_editor,
    load_theme_file,
    load_snippets_file,
    VSCodeTheme,
    VSCodeSnippet,
)
from medha.extensions.models import (
    ThemeContribution,
    SnippetContribution,
    InstalledExtension,
    ExtensionManifest,
    ExtensionClassification,
)


# =============================================================================
# Fixtures
# =============================================================================

FIXTURE_THEME_JSON = {
    "name": "Test Theme",
    "type": "dark",
    "colors": {
        "editor.background": "#112233",
        "editor.foreground": "#ddeeff",
        "editor.lineHighlightBackground": "#334455",
        "editor.selectionBackground": "#445566",
        "editorCursor.foreground": "#ffffff",
    },
    "tokenColors": [
        {"scope": "comment", "settings": {"foreground": "#556677", "fontStyle": "italic"}},
        {"scope": "string", "settings": {"foreground": "#8899aa"}},
        {"scope": "keyword", "settings": {"foreground": "#bbccdd"}},
    ],
}

FIXTURE_SNIPPET_JSON = {
    "fori": {
        "prefix": "fori",
        "body": [
            "for i in range($1):",
            "    $0"
        ],
        "description": "For loop with range",
        "scope": "python"
    },
    "forn": {
        "prefix": "forn",
        "body": "for (int i = 0; i < $1; i++) { $0 }",
        "description": "C-style for loop",
        "scope": "c"
    }
}


@pytest.fixture
def temp_extension_dir():
    """Create a temporary extension directory with fixture files."""
    temp_dir = Path(tempfile.mkdtemp(prefix="medha_test_ext_"))
    ext_root = temp_dir / "extension"
    ext_root.mkdir()

    # package.json
    package_json = {
        "name": "test-extension",
        "version": "1.0.0",
        "displayName": "Test Extension",
        "publisher": "test-pub",
        "contributes": {
            "themes": [
                {"label": "Test Theme", "uiTheme": "vs-dark", "path": "./theme/test.json"}
            ],
            "snippets": [
                {"language": "python", "path": "./snippets/python.json"},
                {"language": "c", "path": "./snippets/c.json"}
            ]
        }
    }
    (ext_root / "package.json").write_text(json.dumps(package_json))

    # Theme file
    theme_dir = ext_root / "theme"
    theme_dir.mkdir()
    (theme_dir / "test.json").write_text(json.dumps(FIXTURE_THEME_JSON))

    # Snippet files
    snippets_dir = ext_root / "snippets"
    snippets_dir.mkdir()
    (snippets_dir / "python.json").write_text(json.dumps(FIXTURE_SNIPPET_JSON))
    (snippets_dir / "c.json").write_text(json.dumps(FIXTURE_SNIPPET_JSON))

    yield temp_dir

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def installed_extension(temp_extension_dir):
    """Create an InstalledExtension from the temp directory."""
    ext_root = temp_extension_dir / "extension"
    with open(ext_root / "package.json", "r") as f:
        package_data = json.load(f)
    manifest = ExtensionManifest.from_package_json(package_data)

    return InstalledExtension(
        namespace="test-pub",
        name="test-extension",
        version="1.0.0",
        install_path=str(temp_extension_dir),
        manifest=manifest,
        classification=ExtensionClassification.SUPPORTED,
        enabled=True,
    )


# =============================================================================
# Tests
# =============================================================================

class TestThemeMapping:
    """Tests for map_vscode_theme_to_medha function."""

    def test_map_fixture_theme_colors(self):
        """Test that fixture theme maps to exact expected colors."""
        theme = VSCodeTheme.from_dict(FIXTURE_THEME_JSON)
        mapped = map_vscode_theme_to_medha(theme)

        # Check palette colors
        palette = mapped["palette"]
        assert "editor_bg" in palette
        assert palette["editor_bg"] == "#112233", f"Expected #112233, got {palette['editor_bg']}"

        assert "editor_fg" in palette
        assert palette["editor_fg"] == "#ddeeff", f"Expected #ddeeff, got {palette['editor_fg']}"

        assert "editor_line_highlight" in palette
        assert palette["editor_line_highlight"] == "#334455"

        assert "editor_selection" in palette
        assert palette["editor_selection"] == "#445566"

        assert "editor_cursor" in palette
        assert palette["editor_cursor"] == "#ffffff"

        # Check token colors
        token_colors = mapped["token_colors"]
        assert "comment" in token_colors
        assert token_colors["comment"]["foreground"] == "#556677"
        assert token_colors["comment"]["fontStyle"] == "italic"

        assert "string" in token_colors
        assert token_colors["string"]["foreground"] == "#8899aa"

        assert "keyword" in token_colors
        assert token_colors["keyword"]["foreground"] == "#bbccdd"

    def test_load_theme_file_from_installed(self, installed_extension):
        """Test loading theme file from installed extension."""
        theme_contrib = installed_extension.manifest.themes[0]
        theme = load_theme_file(installed_extension, theme_contrib)

        assert theme is not None
        assert isinstance(theme, VSCodeTheme)
        assert theme.name == "Test Theme"
        assert theme.type == "dark"
        assert theme.colors["editor.background"] == "#112233"
        assert theme.colors["editor.foreground"] == "#ddeeff"


class TestEditorThemeApplication:
    """Tests for applying theme to real editor widget."""

    @pytest.mark.skipif(
        "QT_QPA_PLATFORM" not in os.environ or os.environ["QT_QPA_PLATFORM"] != "offscreen",
        reason="Requires QT_QPA_PLATFORM=offscreen"
    )
    def test_apply_theme_to_editor_background(self, installed_extension):
        """
        Create real MEDHA editor widget with QT_QPA_PLATFORM=offscreen,
        apply theme, assert palette/background color is #112233.
        """
        # Import here to avoid Qt initialization issues
        from PySide6.QtWidgets import QApplication
        from medha.editor_widget import AdvancedCodeEditorWidget
        from medha.highlighter import CodeHighlighter

        # Ensure QApplication exists
        app = QApplication.instance() or QApplication(sys.argv)

        # Create editor widget
        editor = AdvancedCodeEditorWidget(file_path=None, parent=None)

        # Load theme from installed extension
        theme_contrib = installed_extension.manifest.themes[0]
        theme = load_theme_file(installed_extension, theme_contrib)
        assert theme is not None

        # Apply theme to editor
        result = apply_theme_to_editor(theme, editor, editor.highlighter)

        # Check that palette was applied
        palette = result["palette"]
        assert "editor_bg" in palette
        assert palette["editor_bg"] == "#112233"

        # Check editor's stylesheet has the background color
        stylesheet = editor.styleSheet()
        assert "#112233" in stylesheet, f"Background color #112233 not found in stylesheet: {stylesheet}"

        # Check margin area also has the background
        margin_style = editor.margin_area.styleSheet()
        assert "#112233" in margin_style, f"Background color #112233 not found in margin stylesheet: {margin_style}"

        editor.deleteLater()

    def test_map_vscode_theme_returns_palette_with_editor_bg(self):
        """Test that map_vscode_theme_to_medha returns palette with editor_bg."""
        theme = VSCodeTheme.from_dict(FIXTURE_THEME_JSON)
        mapped = map_vscode_theme_to_medha(theme)

        palette = mapped["palette"]
        assert "editor_bg" in palette
        assert palette["editor_bg"] == "#112233"


class TestSnippetExpansion:
    """Tests for snippet expansion and cursor placeholder handling."""

    def test_load_snippets_file(self, installed_extension):
        """Test loading snippets file from installed extension."""
        snippet_contrib = installed_extension.manifest.snippets[0]  # python snippets
        snippets = load_snippets_file(installed_extension, snippet_contrib)

        assert "fori" in snippets
        snippet = snippets["fori"]
        assert isinstance(snippet, VSCodeSnippet)
        assert snippet.prefix == "fori"
        assert snippet.body == ["for i in range($1):", "    $0"]
        assert snippet.description == "For loop with range"
        assert snippet.scope == "python"

        assert "forn" in snippets
        snippet = snippets["forn"]
        assert snippet.prefix == "forn"
        assert snippet.body == ["for (int i = 0; i < $1; i++) { $0 }"]
        assert snippet.description == "C-style for loop"
        assert snippet.scope == "c"

    def test_snippet_body_parsing_multiline(self):
        """Test that multi-line snippet body is parsed correctly."""
        snippet_data = {
            "prefix": "fori",
            "body": [
                "for i in range($1):",
                "    $0"
            ],
            "description": "For loop with range"
        }
        snippet = VSCodeSnippet.from_dict("fori", snippet_data)

        assert snippet.body == ["for i in range($1):", "    $0"]
        assert snippet.prefix == "fori"

    def test_snippet_body_parsing_single_line(self):
        """Test that single-line snippet body is parsed as list."""
        snippet_data = {
            "prefix": "forn",
            "body": "for (int i = 0; i < $1; i++) { $0 }",
            "description": "C-style for loop"
        }
        snippet = VSCodeSnippet.from_dict("forn", snippet_data)

        assert snippet.body == ["for (int i = 0; i < $1; i++) { $0 }"]
        assert snippet.prefix == "forn"

    @pytest.mark.skipif(
        "QT_QPA_PLATFORM" not in os.environ or os.environ["QT_QPA_PLATFORM"] != "offscreen",
        reason="Requires QT_QPA_PLATFORM=offscreen"
    )
    def test_editor_snippet_expansion_tabstops(self, installed_extension):
        """
        Test snippet expansion in real editor widget with offscreen platform.
        Verifies tabstops $1 and $0 are handled correctly.
        """
        from PySide6.QtWidgets import QApplication
        from medha.editor_widget import AdvancedCodeEditorWidget

        app = QApplication.instance() or QApplication(sys.argv)

        editor = AdvancedCodeEditorWidget(file_path=None, parent=None)

        # Load snippet
        snippet_contrib = installed_extension.manifest.snippets[0]  # python
        snippets = load_snippets_file(installed_extension, snippet_contrib)
        snippet = snippets["fori"]

        # Insert snippet
        editor.set_snippet(snippet)

        # Get the text after insertion
        text = editor.toPlainText()
        expected_text = "for i in range():\n    "
        assert text == expected_text, f"Expected '{expected_text}', got '{repr(text)}'"

        # Check tabstops were created
        tabstops = editor.get_snippet_tabstops()
        assert len(tabstops) >= 2, f"Expected at least 2 tabstops, got {len(tabstops)}"

        # Check $1 tabstop exists
        tabstop_1 = [t for t in tabstops if t[0] == 1]
        assert len(tabstop_1) == 1, f"Expected exactly one $1 tabstop, got {len(tabstop_1)}"

        # Check $0 tabstop exists
        tabstop_0 = [t for t in tabstops if t[0] == 0]
        assert len(tabstop_0) == 1, f"Expected exactly one $0 tabstop, got {len(tabstop_0)}"

        # Check cursor is at $1 position (first tabstop)
        cursor = editor.textCursor()
        cursor_pos = cursor.position()
        # $1 should be at position after "for i in range(" which is 15 chars
        assert cursor_pos == 15, f"Expected cursor at position 15 ($1), got {cursor_pos}"

        editor.deleteLater()


class TestSnippetIntegration:
    """Integration tests for snippet workflow."""

    def test_snippet_token_color_mapping(self):
        """Test that token colors from theme apply to snippet-relevant scopes."""
        theme = VSCodeTheme.from_dict(FIXTURE_THEME_JSON)
        mapped = map_vscode_theme_to_medha(theme)

        token_colors = mapped["token_colors"]
        # String tokens should be mapped
        assert "string" in token_colors
        assert token_colors["string"]["foreground"] == "#8899aa"

        # Keyword tokens should be mapped
        assert "keyword" in token_colors
        assert token_colors["keyword"]["foreground"] == "#bbccdd"

    def test_multiple_snippet_files_merged(self, installed_extension):
        """Test that snippets from multiple files are merged by language."""
        from medha.extensions.contributions import load_all_snippets

        all_snippets = load_all_snippets(installed_extension)

        # Should have both python and c snippets
        assert "python" in all_snippets
        assert "c" in all_snippets

        # Python snippets
        py_snippets = all_snippets["python"]
        assert "fori" in py_snippets
        assert py_snippets["fori"].prefix == "fori"

        # C snippets
        c_snippets = all_snippets["c"]
        assert "forn" in c_snippets
        assert c_snippets["forn"].prefix == "forn"


# =============================================================================
# Run as script
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])