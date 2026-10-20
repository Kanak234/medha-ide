"""
MEDHA Extensions — Contributions Loader

Parses extension package.json and loads declarative contributions:
- themes (VS Code color theme JSON)
- snippets (VS Code snippet JSON)
- grammars (TextMate grammar JSON - subset only)

Never executes any JS code from extensions.
"""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from medha.extensions.models import (
    ExtensionManifest,
    ExtensionClassification,
    ThemeContribution,
    SnippetContribution,
    GrammarContribution,
    VSCodeTheme,
    VSCodeSnippet,
    InstalledExtension,
)

logger = logging.getLogger(__name__)


def load_installed_manifest(installed: InstalledExtension) -> ExtensionManifest:
    """
    Load and parse the extension's package.json from disk.

    Args:
        installed: InstalledExtension metadata

    Returns:
        Parsed ExtensionManifest
    """
    ext_root = Path(installed.install_path) / "extension"
    if not ext_root.exists():
        raise FileNotFoundError(f"Extension root not found: {ext_root}")

    package_json = ext_root / "package.json"
    if not package_json.exists():
        raise FileNotFoundError(f"package.json not found: {package_json}")

    with open(package_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    return ExtensionManifest.from_package_json(data)


def load_theme_file(installed: InstalledExtension, theme: ThemeContribution) -> Optional[VSCodeTheme]:
    """
    Load a theme JSON file from an installed extension.

    Args:
        installed: InstalledExtension metadata
        theme: ThemeContribution to load

    Returns:
        Parsed VSCodeTheme or None if failed
    """
    ext_root = Path(installed.install_path) / "extension"
    theme_path = ext_root / theme.path.lstrip("./")

    if not theme_path.exists():
        logger.warning(f"Theme file not found: {theme_path}")
        return None

    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return VSCodeTheme.from_dict(data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in theme {theme_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load theme {theme_path}: {e}")
        return None


def load_snippets_file(installed: InstalledExtension, snippet: SnippetContribution) -> Dict[str, VSCodeSnippet]:
    """
    Load a snippets JSON file from an installed extension.

    Args:
        installed: InstalledExtension metadata
        snippet: SnippetContribution to load

    Returns:
        Dict mapping snippet prefix to VSCodeSnippet
    """
    ext_root = Path(installed.install_path) / "extension"
    snippet_path = ext_root / snippet.path.lstrip("./")

    if not snippet_path.exists():
        logger.warning(f"Snippet file not found: {snippet_path}")
        return {}

    try:
        with open(snippet_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in snippets {snippet_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load snippets {snippet_path}: {e}")
        return {}

    snippets = {}
    for key, value in data.items():
        if isinstance(value, dict):
            snippets[key] = VSCodeSnippet.from_dict(key, value)
    return snippets


def load_grammar_file(installed: InstalledExtension, grammar: GrammarContribution) -> Optional[Dict[str, Any]]:
    """
    Load a grammar file (JSON or plist) from an installed extension.

    Note: Only JSON grammars are supported. Plist grammars are skipped with warning.

    Args:
        installed: InstalledExtension metadata
        grammar: GrammarContribution to load

    Returns:
        Parsed grammar dict or None if failed/unsupported
    """
    ext_root = Path(installed.install_path) / "extension"
    grammar_path = ext_root / grammar.path.lstrip("./")

    if not grammar_path.exists():
        logger.warning(f"Grammar file not found: {grammar_path}")
        return None

    # Only support JSON grammars
    if grammar_path.suffix.lower() != ".json":
        logger.warning(f"Grammar file format not supported (only JSON): {grammar_path}")
        return None

    try:
        with open(grammar_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in grammar {grammar_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load grammar {grammar_path}: {e}")
        return None


def load_all_themes(installed: InstalledExtension) -> List[tuple[str, VSCodeTheme]]:
    """
    Load all themes from an installed extension.

    Returns:
        List of (theme_label, VSCodeTheme) tuples
    """
    themes = []
    manifest = installed.manifest

    for theme_contrib in manifest.themes:
        theme = load_theme_file(installed, theme_contrib)
        if theme:
            themes.append((theme_contrib.label, theme))
            logger.info(f"Loaded theme: {theme_contrib.label}")
        else:
            logger.warning(f"Failed to load theme: {theme_contrib.label}")

    return themes


def load_all_snippets(installed: InstalledExtension) -> Dict[str, Dict[str, VSCodeSnippet]]:
    """
    Load all snippets from an installed extension, grouped by language.

    Returns:
        Dict mapping language -> Dict of snippet prefix -> VSCodeSnippet
    """
    all_snippets = {}
    manifest = installed.manifest

    for snippet_contrib in manifest.snippets:
        snippets = load_snippets_file(installed, snippet_contrib)
        if snippets:
            lang = snippet_contrib.language.lower()
            if lang not in all_snippets:
                all_snippets[lang] = {}
            all_snippets[lang].update(snippets)
            logger.info(f"Loaded {len(snippets)} snippets for language: {lang}")
        else:
            logger.warning(f"Failed to load snippets for language: {snippet_contrib.language}")

    return all_snippets


def load_all_grammars(installed: InstalledExtension) -> List[tuple[str, Dict[str, Any]]]:
    """
    Load all grammars from an installed extension.

    Returns:
        List of (scope_name, grammar_dict) tuples
    """
    grammars = []
    manifest = installed.manifest

    for grammar_contrib in manifest.grammars:
        grammar = load_grammar_file(installed, grammar_contrib)
        if grammar:
            grammars.append((grammar_contrib.scope_name, grammar))
            logger.info(f"Loaded grammar: {grammar_contrib.scope_name}")
        else:
            logger.warning(f"Failed to load grammar: {grammar_contrib.scope_name}")

    return grammars


def classify_extension(manifest: ExtensionManifest) -> ExtensionClassification:
    """Classify extension based on its contributions."""
    return manifest.classify()


def get_supported_contributions(manifest: ExtensionManifest) -> Dict[str, int]:
    """Get count of supported contributions by type."""
    return {
        "themes": len(manifest.themes),
        "snippets": len(manifest.snippets),
        "grammars": len(manifest.grammars),
    }


def get_all_available_themes() -> List[tuple[InstalledExtension, VSCodeTheme]]:
    """Get all themes from all enabled installed extensions."""
    from medha.extensions.installer import get_enabled_extensions

    all_themes = []
    for installed in get_enabled_extensions():
        for theme in load_all_themes(installed):
            all_themes.append((installed, theme))
    return all_themes


def get_all_available_snippets(language: str = None) -> Dict[str, Dict[str, VSCodeSnippet]]:
    """
    Get all snippets from all enabled installed extensions.

    Args:
        language: Optional filter by language

    Returns:
        Dict mapping language -> snippet_name -> VSCodeSnippet
    """
    from medha.extensions.installer import get_enabled_extensions

    all_snippets = {}
    for installed in get_enabled_extensions():
        snippets = load_all_snippets(installed)
        for lang, lang_snippets in snippets.items():
            if language and lang != language:
                continue
            if lang not in all_snippets:
                all_snippets[lang] = {}
            all_snippets[lang].update(lang_snippets)
    return all_snippets


# =============================================================================
# Theme Mapper - Maps VS Code theme colors to MEDHA editor palette
# =============================================================================

# Mapping of VS Code theme color keys to MEDHA palette keys
VSCODE_TO_MEDHA_COLOR_MAP = {
    # Editor colors
    "editor.background": "editor_bg",
    "editor.foreground": "editor_fg",
    "editor.lineHighlightBackground": "editor_line_highlight",
    "editor.selectionBackground": "editor_selection",
    "editor.inactiveSelectionBackground": "editor_selection_inactive",
    "editorCursor.foreground": "editor_cursor",
    "editorWhitespace.foreground": "editor_whitespace",
    "editorIndentGuide.background": "editor_indent_guide",
    "editorIndentGuide.activeBackground": "editor_indent_guide_active",
    "editorRuler.foreground": "editor_ruler",
    "editorCodeLens.foreground": "editor_codelens",
    "editorLightbulb.foreground": "editor_lightbulb",

    # Line numbers
    "editorLineNumber.foreground": "linenumber_fg",
    "editorLineNumber.activeForeground": "linenumber_active_fg",

    # Brackets
    "editorBracketMatch.background": "bracket_match_bg",
    "editorBracketMatch.border": "bracket_match_border",

    # Gutter
    "editorGutter.background": "gutter_bg",
    "editorGutter.modifiedBackground": "gutter_modified",
    "editorGutter.addedBackground": "gutter_added",
    "editorGutter.deletedBackground": "gutter_deleted",

    # Minimap
    "minimap.background": "minimap_bg",
    "minimapSlider.background": "minimap_slider",
    "minimapSlider.activeBackground": "minimap_slider_active",

    # Scrollbar
    "scrollbar.shadow": "scrollbar_shadow",
    "scrollbarSlider.background": "scrollbar_slider",
    "scrollbarSlider.hoverBackground": "scrollbar_slider_hover",
    "scrollbarSlider.activeBackground": "scrollbar_slider_active",

    # Side bar
    "sideBar.background": "sidebar_bg",
    "sideBar.foreground": "sidebar_fg",
    "sideBar.border": "sidebar_border",
    "sideBarTitle.foreground": "sidebar_title_fg",
    "sideBarSectionHeader.background": "sidebar_section_bg",
    "sideBarSectionHeader.foreground": "sidebar_section_fg",

    # Activity bar
    "activityBar.background": "activitybar_bg",
    "activityBar.foreground": "activitybar_fg",
    "activityBar.inactiveForeground": "activitybar_inactive_fg",
    "activityBar.border": "activitybar_border",
    "activityBarBadge.background": "activitybar_badge_bg",
    "activityBarBadge.foreground": "activitybar_badge_fg",

    # Status bar
    "statusBar.background": "statusbar_bg",
    "statusBar.foreground": "statusbar_fg",
    "statusBar.border": "statusbar_border",
    "statusBar.debuggingBackground": "statusbar_debug_bg",
    "statusBar.debuggingForeground": "statusbar_debug_fg",
    "statusBar.noFolderBackground": "statusbar_nofolder_bg",
    "statusBar.noFolderForeground": "statusbar_nofolder_fg",

    # Title bar
    "titleBar.activeBackground": "titlebar_active_bg",
    "titleBar.activeForeground": "titlebar_active_fg",
    "titleBar.inactiveBackground": "titlebar_inactive_bg",
    "titleBar.inactiveForeground": "titlebar_inactive_fg",
    "titleBar.border": "titlebar_border",

    # Panel
    "panel.background": "panel_bg",
    "panel.border": "panel_border",
    "panelTitle.activeBorder": "panel_title_active_border",
    "panelTitle.activeForeground": "panel_title_active_fg",
    "panelTitle.inactiveForeground": "panel_title_inactive_fg",

    # Tab
    "tab.activeBackground": "tab_active_bg",
    "tab.activeForeground": "tab_active_fg",
    "tab.inactiveBackground": "tab_inactive_bg",
    "tab.inactiveForeground": "tab_inactive_fg",
    "tab.border": "tab_border",
    "tab.activeBorder": "tab_active_border",
    "tab.unfocusedActiveBorder": "tab_unfocused_active_border",
    "tab.hoverBackground": "tab_hover_bg",
    "tab.hoverBorder": "tab_hover_border",

    # Terminal
    "terminal.background": "terminal_bg",
    "terminal.foreground": "terminal_fg",
    "terminal.ansiBlack": "terminal_ansi_black",
    "terminal.ansiRed": "terminal_ansi_red",
    "terminal.ansiGreen": "terminal_ansi_green",
    "terminal.ansiYellow": "terminal_ansi_yellow",
    "terminal.ansiBlue": "terminal_ansi_blue",
    "terminal.ansiMagenta": "terminal_ansi_magenta",
    "terminal.ansiCyan": "terminal_ansi_cyan",
    "terminal.ansiWhite": "terminal_ansi_white",
    "terminal.ansiBrightBlack": "terminal_ansi_bright_black",
    "terminal.ansiBrightRed": "terminal_ansi_bright_red",
    "terminal.ansiBrightGreen": "terminal_ansi_bright_green",
    "terminal.ansiBrightYellow": "terminal_ansi_bright_yellow",
    "terminal.ansiBrightBlue": "terminal_ansi_bright_blue",
    "terminal.ansiBrightMagenta": "terminal_ansi_bright_magenta",
    "terminal.ansiBrightCyan": "terminal_ansi_bright_cyan",
    "terminal.ansiBrightWhite": "terminal_ansi_bright_white",
    "terminal.selectionBackground": "terminal_selection",
    "terminalCursor.background": "terminal_cursor_bg",
    "terminalCursor.foreground": "terminal_cursor_fg",

    # Debug
    "debugToolBar.background": "debug_toolbar_bg",
    "debugToolBar.border": "debug_toolbar_border",

    # Editor widget
    "editorWidget.background": "editor_widget_bg",
    "editorWidget.border": "editor_widget_border",
    "editorWidget.resizeBorder": "editor_widget_resize_border",

    # Peek view
    "peekViewEditor.background": "peek_editor_bg",
    "peekViewEditor.matchHighlightBackground": "peek_match_highlight",
    "peekViewResult.background": "peek_result_bg",
    "peekViewResult.matchHighlightBackground": "peek_result_match_highlight",
    "peekViewResult.fileForeground": "peek_result_file_fg",
    "peekViewResult.lineForeground": "peek_result_line_fg",
    "peekViewResult.selectionBackground": "peek_result_selection",
    "peekViewResult.selectionForeground": "peek_result_selection_fg",
    "peekViewTitle.background": "peek_title_bg",
    "peekViewTitleLabel.foreground": "peek_title_label_fg",
    "peekViewTitleDescription.foreground": "peek_title_desc_fg",

    # Merge conflicts
    "merge.currentHeaderBackground": "merge_current_header_bg",
    "merge.currentContentBackground": "merge_current_content_bg",
    "merge.incomingHeaderBackground": "merge_incoming_header_bg",
    "merge.incomingContentBackground": "merge_incoming_content_bg",
    "merge.commonContentBackground": "merge_common_content_bg",
    "merge.border": "merge_border",

    # Notifications
    "notificationCenterHeader.foreground": "notification_header_fg",
    "notificationCenterHeader.background": "notification_header_bg",
    "notifications.foreground": "notification_fg",
    "notifications.background": "notification_bg",
    "notifications.border": "notification_border",
    "notificationToast.border": "notification_toast_border",

    # Progress
    "progressBar.background": "progressbar_bg",

    # List/tree
    "list.activeSelectionBackground": "list_active_selection_bg",
    "list.activeSelectionForeground": "list_active_selection_fg",
    "list.inactiveSelectionBackground": "list_inactive_selection_bg",
    "list.inactiveSelectionForeground": "list_inactive_selection_fg",
    "list.hoverBackground": "list_hover_bg",
    "list.hoverForeground": "list_hover_fg",
    "list.focusBackground": "list_focus_bg",
    "list.focusForeground": "list_focus_fg",
    "list.highlightForeground": "list_highlight_fg",
    "list.invalidItemForeground": "list_invalid_fg",
    "list.dropBackground": "list_drop_bg",

    # Input
    "input.background": "input_bg",
    "input.foreground": "input_fg",
    "input.border": "input_border",
    "input.placeholderForeground": "input_placeholder_fg",
    "inputOption.activeBorder": "input_option_active_border",
    "inputValidation.infoBackground": "input_validation_info_bg",
    "inputValidation.infoForeground": "input_validation_info_fg",
    "inputValidation.infoBorder": "input_validation_info_border",
    "inputValidation.warningBackground": "input_validation_warning_bg",
    "inputValidation.warningForeground": "input_validation_warning_fg",
    "inputValidation.warningBorder": "input_validation_warning_border",
    "inputValidation.errorBackground": "input_validation_error_bg",
    "inputValidation.errorForeground": "input_validation_error_fg",
    "inputValidation.errorBorder": "input_validation_error_border",

    # Button
    "button.background": "button_bg",
    "button.foreground": "button_fg",
    "button.hoverBackground": "button_hover_bg",
    "button.secondaryBackground": "button_secondary_bg",
    "button.secondaryForeground": "button_secondary_fg",
    "button.secondaryHoverBackground": "button_secondary_hover_bg",

    # Dropdown
    "dropdown.background": "dropdown_bg",
    "dropdown.foreground": "dropdown_fg",
    "dropdown.border": "dropdown_border",

    # Badge
    "badge.foreground": "badge_fg",
    "badge.background": "badge_bg",

    # Git
    "gitDecoration.addedResourceForeground": "git_added_fg",
    "gitDecoration.modifiedResourceForeground": "git_modified_fg",
    "gitDecoration.deletedResourceForeground": "git_deleted_fg",
    "gitDecoration.untrackedResourceForeground": "git_untracked_fg",
    "gitDecoration.ignoredResourceForeground": "git_ignored_fg",
    "gitDecoration.conflictingResourceForeground": "git_conflicting_fg",
    "gitDecoration.submoduleResourceForeground": "git_submodule_fg",

    # Diff editor
    "diffEditor.insertedTextBackground": "diff_inserted_bg",
    "diffEditor.removedTextBackground": "diff_removed_bg",
    "diffEditor.insertedTextBorder": "diff_inserted_border",
    "diffEditor.removedTextBorder": "diff_removed_border",
    "diffEditor.overviewRulerInsertedForeground": "diff_overview_inserted_fg",
    "diffEditor.overviewRulerRemovedForeground": "diff_overview_removed_fg",
    "diffEditor.overviewRulerCommonForeground": "diff_overview_common_fg",
}

# Token color scope mapping
TOKEN_SCOPE_MAP = {
    # Comments
    "comment": "comment",
    "comment.line": "comment",
    "comment.block": "comment",
    "comment.documentation": "comment",

    # Strings
    "string": "string",
    "string.quoted": "string",
    "string.quoted.single": "string",
    "string.quoted.double": "string",
    "string.template": "string",
    "string.regexp": "string_regex",

    # Keywords
    "keyword": "keyword",
    "keyword.control": "keyword",
    "keyword.operator": "keyword_operator",
    "keyword.other": "keyword",

    # Constants
    "constant": "constant",
    "constant.numeric": "number",
    "constant.character": "constant_char",
    "constant.language": "constant_lang",
    "constant.other": "constant",

    # Entities
    "entity": "entity",
    "entity.name": "entity_name",
    "entity.name.type": "type",
    "entity.name.class": "class_name",
    "entity.name.function": "function",
    "entity.name.method": "function",
    "entity.name.tag": "tag",
    "entity.other": "entity_other",
    "entity.other.inherited-class": "inherited_class",

    # Storage
    "storage": "storage",
    "storage.type": "type",
    "storage.modifier": "storage_modifier",

    # Variables
    "variable": "variable",
    "variable.language": "variable_lang",
    "variable.parameter": "parameter",
    "variable.other": "variable",

    # Functions
    "function": "function",
    "function.call": "function_call",

    # Support
    "support": "support",
    "support.function": "support_function",
    "support.class": "support_class",
    "support.type": "support_type",
    "support.constant": "support_constant",
    "support.variable": "support_variable",

    # Markup
    "markup": "markup",
    "markup.heading": "heading",
    "markup.bold": "bold",
    "markup.italic": "italic",
    "markup.underline": "underline",
    "markup.link": "link",
    "markup.quote": "quote",
    "markup.list": "list",

    # Meta
    "meta": "meta",
    "meta.brace": "meta_brace",
    "meta.tag": "meta_tag",

    # Invalid
    "invalid": "invalid",
    "invalid.illegal": "invalid",
    "invalid.deprecated": "deprecated",
}


def validate_color(color: str) -> str:
    """Validate and normalize a hex color string."""
    if not color:
        return ""
    color = color.strip()
    if not color.startswith("#"):
        color = "#" + color
    # Validate hex format
    import re
    if not re.match(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$", color):
        logger.warning(f"Invalid color format: {color}, ignoring")
        return ""
    return color.lower()


def map_vscode_theme_to_medha(theme: VSCodeTheme) -> Dict[str, Any]:
    """
    Map VS Code theme colors to MEDHA palette.

    Returns:
        Dict with keys:
        - palette: Dict of MEDHA color keys -> hex colors
        - token_colors: Dict of token scope -> format dict
        - raw_colors: Original VS Code colors dict (for reference)
    """
    palette = {}
    token_colors = {}

    # Map workbench colors
    for vscode_key, medha_key in VSCODE_TO_MEDHA_COLOR_MAP.items():
        if vscode_key in theme.colors:
            color = validate_color(theme.colors[vscode_key])
            if color:
                palette[medha_key] = color

    # Map token colors
    for token_color in theme.token_colors:
        scope = token_color.get("scope", "")
        settings = token_color.get("settings", {})

        # Scope can be a string or list of strings
        scopes = [scope] if isinstance(scope, str) else scope

        for s in scopes:
            # Find matching MEDHA token type
            medha_token = None
            for vscode_scope, medha_scope in TOKEN_SCOPE_MAP.items():
                if s.startswith(vscode_scope):
                    medha_token = medha_scope
                    break

            if medha_token:
                format_dict = {}
                if "foreground" in settings:
                    format_dict["foreground"] = validate_color(settings["foreground"])
                if "background" in settings:
                    format_dict["background"] = validate_color(settings["background"])
                if "fontStyle" in settings:
                    format_dict["fontStyle"] = settings["fontStyle"]
                if format_dict:
                    token_colors[medha_token] = format_dict

    return {
        "palette": palette,
        "token_colors": token_colors,
        "raw_colors": theme.colors,
    }


def apply_theme_to_editor(theme: VSCodeTheme, editor, highlighter) -> None:
    """
    Apply a VS Code theme to a MEDHA editor widget.

    This modifies the editor's palette and syntax highlighter formats.
    """
    mapped = map_vscode_theme_to_medha(theme)

    # Apply palette colors to editor
    # Note: This requires the editor to support dynamic palette updates
    # For now, we log the mapped colors
    logger.info(f"Applying theme '{theme.name}' with {len(mapped['palette'])} palette colors and {len(mapped['token_colors'])} token colors")

    # Apply to highlighter if supported
    if hasattr(highlighter, 'set_theme_formats'):
        highlighter.set_theme_formats(mapped["token_colors"])

    # Apply to editor palette if supported
    if hasattr(editor, 'set_palette_colors'):
        editor.set_palette_colors(mapped["palette"])

    return mapped


def load_extension_contributions(installed: InstalledExtension) -> Dict[str, Any]:
    """
    Load all declarative contributions from an installed extension.

    Returns:
        Dict with keys: themes, snippets, grammars
    """
    if installed.classification == ExtensionClassification.UNSUPPORTED:
        logger.info(f"Extension {installed.unique_id} is UNSUPPORTED (JS only)")
        return {"themes": [], "snippets": {}, "grammars": []}

    contributions = {
        "themes": load_all_themes(installed),
        "snippets": load_all_snippets(installed),
        "grammars": load_all_grammars(installed),
    }

    if installed.classification == ExtensionClassification.PARTIAL:
        logger.info(f"Extension {installed.unique_id} is PARTIAL (has JS code + declarative)")

    return contributions


def load_extension_contributions(installed: InstalledExtension) -> Dict[str, Any]:
    """
    Load all declarative contributions from an installed extension.

    Returns:
        Dict with keys: themes, snippets, grammars
    """
    if installed.classification == ExtensionClassification.UNSUPPORTED:
        logger.info(f"Extension {installed.unique_id} is UNSUPPORTED (JS only)")
        return {"themes": [], "snippets": {}, "grammars": []}

    contributions = {
        "themes": load_all_themes(installed),
        "snippets": load_all_snippets(installed),
        "grammars": load_all_grammars(installed),
    }

    if installed.classification == ExtensionClassification.PARTIAL:
        logger.info(f"Extension {installed.unique_id} is PARTIAL (has JS code + declarative)")

    return contributions