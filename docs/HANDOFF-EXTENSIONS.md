## Summary

Implemented a complete Extensions system for MEDHA IDE using the Open VSX registry (https://open-vsx.org). The system provides:

1. **Registry Client** — Search, fetch details, and download extensions with 10s timeout, SHA-256 verification, 50 MB limit
2. **Secure Installer** — Zip-slip protected extraction, SHA-256 validation, install/uninstall/list with manifest metadata
3. **Contribution Loader** — Parses `package.json` declarative contributions: themes (VS Code color theme JSON), snippets (VS Code snippet JSON), grammars (TextMate JSON subset). Classifies extensions as SUPPORTED / PARTIAL / UNSUPPORTED
4. **Theme Mapper** — Maps VS Code theme colors (`editor.background`, `editor.foreground`, etc.) and tokenColors scopes to MEDHA editor palette and QSyntaxHighlighter formats
5. **UI Panel** — Marketplace/Installed tabs, search box, detail view with README/license/repo, badges with tooltips, Install/Uninstall/Enable/Disable/Apply Theme buttons, offline banner

All network operations run in QThread workers off the UI thread. No JavaScript extension code is ever executed — only declarative contributions are used.

---

## Files created / changed

| File | Purpose |
|------|---------|
| `docs/EXTENSIONS-PLAN.md` | Complete plan with PRD, TRD, UI brief, architecture, worst cases, victory criteria |
| `docs/GATE-21-EXTENSIONS.md` | Architecture diagram, threat model, demo script |
| `medha/extensions/__init__.py` | Package exports |
| `medha/extensions/models.py` | Dataclasses: ExtensionInfo, ExtensionDetail, InstalledExtension, ThemeContribution, SnippetContribution, GrammarContribution, VSCodeTheme, VSCodeSnippet, ExtensionClassification |
| `medha/extensions/registry.py` | OpenVSXRegistryClient: search(), detail(), download_vsix() with streaming, size limit, SHA-256 verification |
| `medha/extensions/installer.py` | install_vsix(), uninstall_extension(), list_installed_extensions(), get_enabled_extensions(), zip-slip safe extraction, 50 MB limit |
| `medha/extensions/contributions.py` | load_all_themes(), load_all_snippets(), load_all_grammars(), map_vscode_theme_to_medha(), apply_theme_to_editor(), classification |
| `medha/extensions/ui/worker.py` | QThread workers: SearchWorker, DetailWorker, DownloadWorker, InstallWorker, UninstallWorker, ListInstalledWorker, ToggleEnabledWorker, ApplyThemeWorker |
| `medha/extensions/ui/panel.py` | ExtensionsPanel widget with Marketplace/Installed tabs, search, detail view, buttons |
| `medha/extensions/ui/__init__.py` | UI package exports |
| `tests/test_extensions_registry.py` | Fake HTTP server tests + 1 real "dracula" search |
| `tests/test_extensions_installer.py` | Zip-slip attack test, install/uninstall round-trip, 3 fixture extensions (theme-only, snippets-only, JS-only) classification |
| `medha/app.py` | Added ExtensionsPanel dock, View menu entry, Ctrl+Shift+X shortcut, theme apply handler |

---

## Gate results

### Gate 1: Registry Client
```
cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python -m pytest tests/test_extensions_registry.py -v
```
```
============================= test session starts ==============================
tests/test_extensions_registry.py::TestRegistrySearch::test_search_parses_results PASSED
tests/test_extensions_registry.py::TestRegistrySearch::test_search_with_offset PASSED
tests/test_extensions_registry.py::TestRegistrySearch::test_search_empty_query PASSED
tests/test_extensions_registry.py::TestRegistryDetail::test_detail_parses_full_metadata PASSED
tests/test_extensions_registry.py::TestRegistryDetail::test_detail_not_found_raises PASSED
tests/test_extensions_registry.py::TestRegistryDownload::test_download_sha256_match PASSED
tests/test_extensions_registry.py::TestRegistryDownload::test_download_sha256_mismatch_refused PASSED
tests/test_extensions_registry.py::TestRegistryDownload::test_download_oversize_refused PASSED
tests/test_extensions_registry.py::TestRegistryDownload::test_download_network_error_handled PASSED
tests/test_extensions_registry.py::TestRegistryRealCall::test_real_search_dracula PASSED
=============================== 10 passed, 1 warning in 0.78s =====================
```

**Real search output:**
```
=== Real Open VSX Search Results for 'dracula' ===
Total results: 53
  - nszihan.vscode-dracula-colorful v2.2.1: Dracula Colorful (17889 downloads)
  - Mopsgamer.dracula-highlighting v0.3.0: Dracula Highlighting (4966 downloads)
  - dracula-theme.theme-dracula v2.25.1: Dracula Theme Official (439954 downloads)
  - Shuzzy.dracula-shuzzyos v1.2.1: Dracula ShuzzyOS (3384 downloads)
  - realeinar.theme-dracula-midnight v1.0.0: Dracula Midnight (9342 downloads)
```

### Gate 2: Installer + Contribution Loader
```
cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python -m pytest tests/test_extensions_installer.py -v
```
```
============================= test session starts ==============================
tests/test_extensions_installer.py::TestSafeExtractZip::test_safe_extract_normal PASSED
tests/test_extensions_installer.py::TestSafeExtractZip::test_zip_slip_attack_rejected PASSED
tests/test_extensions_installer.py::TestSafeExtractZip::test_corrupt_zip_rejected PASSED
tests/test_extensions_installer.py::TestVerifySHA256::test_sha256_match PASSED
tests/test_extensions_installer.py::TestVerifySHA256::test_sha256_mismatch PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_install_theme_only PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_install_snippet_only PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_install_js_only_classified_unsupported PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_install_partial_classified_partial PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_sha256_mismatch_refused PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_oversize_vsix_refused PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_uninstall_removes_extension PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_uninstall_nonexistent_returns_false PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_list_installed_extensions PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_get_enabled_extensions PASSED
tests/test_extensions_installer.py::TestInstallerRoundTrip::test_get_installed_extension PASSED
tests/test_extensions_installer.py::TestParseExtensionManifest::test_parse_valid_manifest PASSED
tests/test_extensions_installer.py::TestParseExtensionManifest::test_parse_missing_package_json_raises PASSED
tests/test_extensions_installer.py::TestParseExtensionManifest::test_parse_invalid_json_raises PASSED
=============================== 19 passed in 0.18s =====================
```

**Fixtures tested:**
- Theme-only → SUPPORTED
- Snippets-only → SUPPORTED
- JS-only → UNSUPPORTED
- Mixed (themes + JS) → PARTIAL

### Gate 3: Apply Contributions
- Theme mapper implemented and connected via `_on_theme_apply_requested` in app.py
- Snippet infrastructure ready (get_all_available_snippets, VSCodeSnippet model with $1/$0 placeholders)
- Grammar loading implemented as subset (JSON only, no plist, no begin/end/include)

### Gate 4: UI + Integration
```
cd /home/kanak07/chromium-shift/medha-ide && timeout --foreground 10 .venv/bin/python -m medha
```
→ App launches successfully, no traceback, 0 "already running" warnings

```
cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python verify_medha.py
```
```
==============================================================
RESULT: 6/6 checkpoints passed
==============================================================
```

---

## Manual test script for Kanak

1. Launch MEDHA: `.venv/bin/python -m medha`
2. Press `Ctrl+Shift+X` → Extensions panel opens on right
3. Type `dracula` in search box, press Enter
4. Observe results with [SUPPORTED] badges (green)
5. Click "Dracula Theme Official" → detail view shows README, MIT license, repo link
6. Click **Install** → downloads, verifies SHA-256, installs to `~/.medha/extensions/...`
7. Switch to **Installed** tab → extension listed with themes: "Dracula", "Dracula Soft"
8. Click **Apply** on "Dracula" theme → editor colors change immediately (no restart)
9. Open a `.c` file, type `for` → if snippet extension installed, snippet expands with $1 placeholder
10. Click **Uninstall** → extension removed, theme reverts
11. Disconnect network → panel shows "⚠ Offline — showing installed extensions"
11. Reconnect, search "dracula" again → works normally
12. Run `verify_medha.py` → **6/6 PASS**

---

## NOT VERIFIED / NOT DONE

- **Full TextMate Grammar Engine** — Only JSON `patterns` with `match`/`name` supported. No `begin`/`end`, `include`, `repository`, or plist grammars. Marked NOT DONE.
- **Extension Auto-Update** — Not implemented. Manual reinstall required.
- **Extension Dependencies** — `extensionDependencies` ignored.
- **Icon Download/Display** — Placeholder only; real icons not fetched.
- **README/Markdown Rendering** — Plain text only; no Markdown rendering.
- **Workspace-Level Extensions** — Only user-global `~/.medha/extensions/` supported.
- **Extension Settings/Configuration** — `contributes.configuration` ignored.
- **Snippet Tab Stops** — Only `$1` and `$0` handled; full VS Code snippet grammar (choices, transforms, etc.) NOT DONE.
- **Theme Semantic Highlighting** — `semanticHighlighting: true` not integrated with LSP semantic tokens.

---

## Open questions

1. Should `~/.medha/extensions/` be configurable via `MEDHA_EXTENSIONS_DIR` env var?
2. Background indexer for local registry cache?
3. Integrate `semanticHighlighting: true` with LSP semantic tokens?
4. Implement full VS Code snippet grammar (choices `${1|opt1,opt2|}`, transforms)?
5. Grammar injection: extend existing highlighter vs replace? Current plan: extend.

---

## Follow-up 1 (2026-10-20)

### 1. Import Hygiene ✅
Removed Qt UI imports from `medha/extensions/__init__.py`. `app.py` imports `ExtensionsPanel` directly from `medha.extensions.ui.panel`.

**Verification:**
```bash
.venv/bin/python -c "import sys; import medha.extensions.registry, medha.extensions.installer, medha.extensions.contributions; print('PySide6' in sys.modules)"
```
**Output:** `False`

### 2. Dependencies ✅
Created `requirements.txt` listing all third-party packages imported by `medha/`:

```bash
# MEDHA IDE — Third-party dependencies
# Generated by scanning medha/ imports

# Qt 6 GUI framework (core dependency)
PySide6>=6.12.0

# System/process monitoring (used in app.py, core/orchestrator.py)
psutil>=7.2.0

# HTTP client for Open VSX Registry API (used in extensions/registry.py)
requests>=2.34.0
```

**Import scan command used:**
```bash
grep -r "^import \|^from " medha/ --include="*.py" | grep -v "^\s*#" | grep -v "medha\." | grep -v "^\s*from \." | grep -v "import os\|import sys\|import json\|import re\|import logging\|import time\|import hashlib\|import shutil\|import subprocess\|import tempfile\|import zipfile\|import urllib\|import socket\|import pathlib\|from pathlib\|from typing\|from dataclasses\|from enum\|from urllib\|from __future__\|import GDB" | sort -u
```

Updated `build_packages.py` with proper `.deb` Depends line:
```
Depends: gcc, g++, gdb, git, cmake, make, python3 (>= 3.10), python3-pyside6, python3-psutil, python3-requests
```

### 3. Missing Phase-3 Tests ✅
Created `tests/test_extensions_contributions.py` with 10 tests:

| Test | Purpose |
|------|---------|
| `test_map_fixture_theme_colors` | Fixture theme (editor.background #112233, editor.foreground #ddeeff, tokenColors comment #556677) → assert exact color mapping |
| `test_load_theme_file_from_installed` | Load theme from installed extension fixture |
| `test_apply_theme_to_editor_background` | `QT_QPA_PLATFORM=offscreen` create real editor, apply theme, assert palette/background is #112233 |
| `test_map_vscode_theme_returns_palette_with_editor_bg` | Unit test for palette mapping |
| `test_load_snippets_file` | Load snippet file from installed extension |
| `test_snippet_body_parsing_multiline` | Multi-line snippet body parsing |
| `test_snippet_body_parsing_single_line` | Single-line snippet body parsing |
| `test_editor_snippet_expansion_tabstops` | Real editor widget + snippet expansion, verify $1/$0 tabstop handling |
| `test_snippet_token_color_mapping` | Token colors from theme apply to snippet-relevant scopes |
| `test_multiple_snippet_files_merged` | Snippets from multiple files merged by language |

Registered `network` pytest mark in `pytest.ini`:
```ini
[pytest]
markers =
    network: marks tests that require network access (real Open VSX API calls)
    integration: marks integration tests that require full application setup
    slow: marks tests that are slow to run
```

**Test run:**
```bash
cd /home/kanak07/chromium-shift/medha-ide && QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_extensions_contributions.py -v
```
**Output:** 10 passed in 0.18s

**Full test suite:**
```bash
cd /home/kanak07/chromium-shift/medha-ide && QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -v
```
**Output:** 39 passed in 0.85s

### 4. Verify ✅

**pytest:**
```bash
cd /home/kanak07/chromium-shift/medha-ide && QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests -q
```
**Output:** 39 passed in 0.84s

**verify_medha.py:**
```bash
cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python verify_medha.py
```
**Output:**
```
==============================================================
MEDHĀ ADVERSARIAL VALIDATOR
validator sha256 : 4b8635bdb80a70b5062356771e8b81ae
run seed         : 6546231   (different every run — cannot be pre-baked)
==============================================================

[PASS] C0 — Real graphical session, not headless
[PASS] C1 — No fabricated values in source
[PASS] C2 — Native window appears on screen
[PASS] C3 — Run button invokes a real compiler and real binary
       n=631 (generated this run)
       expected=940353
       got=940353
[PASS] C4 — Compiler errors parsed with correct line numbers
       error deliberately placed at line 10 (chosen this run)
       lines reported by MEDHĀ: [10]
       diagnostic count: 1
[PASS] C5 — Terminal executes a real shell
       token generated this run: 23027d43be44091a
       found in terminal buffer: True

==============================================================
RESULT: 6/6 checkpoints passed
==============================================================
```

**App launch (no traceback):**
```bash
cd /home/kanak07/chromium-shift/medha-ide && timeout --foreground 10 .venv/bin/python -m medha
```
**Output:** App launches successfully, no traceback, only Qt Wayland informational messages.

**Import hygiene re-verified:**
```bash
.venv/bin/python -c "import sys; import medha.extensions.registry, medha.extensions.installer, medha.extensions.contributions; print('PySide6' in sys.modules)"
```
**Output:** `False`

**Git restore:**
```bash
git checkout -- main.s
```
Restored successfully.