# MEDHA IDE — Extensions System Plan (Open VSX Integration)

## 1. PRD — Product Requirements

### User Stories
1. **Search Extensions**: As a developer, I want to search the Open VSX registry from inside MEDHA so I can discover themes, snippets, and grammars.
2. **Install Extension**: As a developer, I want to install an extension with one click, securely (HTTPS, SHA-256 verified, zip-slip protected, 50 MB limit).
3. **Manage Installed**: As a developer, I want to see all installed extensions, enable/disable/uninstall them.
4. **Apply Themes Live**: As a developer, I want installed color themes to apply immediately without restarting MEDHA.
5. **Use Snippets**: As a developer, I want installed snippets to appear in code completion (prefix → body, $1/$0 placeholders).
6. **Offline Mode**: As a developer, if I have no internet, the panel shows "Offline — showing installed extensions" and everything already installed keeps working.
7. **Unsupported Visibility**: As a developer, I want to see extensions that are JS-only marked as UNSUPPORTED with a tooltip explaining why.

### Acceptance Criteria (per Gate)
- **Gate 1 (Registry Client)**: `tests/test_extensions_registry.py` passes (fake server + 1 real search for "dracula").
- **Gate 2 (Installer + Contribution Loader)**: zip-slip attack rejected, install/uninstall round-trip works, 3 fixture extensions classified correctly.
- **Gate 3 (Apply Contributions)**: fixture theme changes editor palette colors; fixture snippet expands in editor.
- **Gate 4 (UI + Integration)**: `.venv/bin/python -m medha` runs 10 s with no traceback, 0 "already running" warnings; `verify_medha.py` still 6/6.
- **Gate 5 (Handoff)**: `docs/HANDOFF-EXTENSIONS.md` with honest results.

---

## 2. TRD — Technical Reference Design

### Modules (new files under `medha/extensions/`)
| File | Responsibility |
|------|----------------|
| `registry.py` | Pure-Python Open VSX client: `search(query, offset)`, `detail(namespace, name)`, `download(url, sha256, dest_dir) -> path`. No Qt. |
| `installer.py` | `install(vsix_path) -> install_dir`, `uninstall(namespace, name, version)`, `list_installed() -> list[InstalledExt]`. Zip-slip safe, SHA-256 verify, 50 MB cap. |
| `contributions.py` | Parse `extension/package.json` → classify `SUPPORTED` / `PARTIAL` / `UNSUPPORTED`. Load themes (JSON), snippets (JSON), grammars (TextMate JSON/plist — subset only). |
| `models.py` | Dataclasses: `ExtensionInfo`, `InstalledExtension`, `ThemeContribution`, `SnippetContribution`, `GrammarContribution`, `ExtensionClassification`. |
| `manager.py` | High-level orchestrator: `search_and_install()`, `apply_theme(theme_id)`, `get_available_snippets(language)`, `refresh_installed()`. Emits Qt signals. |

### Threading & Network
- All network calls in `QThread` workers (subclass `QThread`, `run()` does blocking `requests` with 10 s timeout).
- `RegistryClient` is pure Python; UI layer wraps it in `RegistryWorker(QThread)`.
- Signals: `search_finished(list[ExtensionInfo])`, `detail_finished(ExtensionDetail)`, `download_finished(path)` / `error(str)`.

### Storage Layout
```
~/.medha/
  extensions/
    <namespace>.<name>-<version>/          # installed extension root
      extension/                            # unzipped VSIX contents
        package.json
        theme/*.json
        snippets/*.json
        syntaxes/*.json
      manifest.json                         # our metadata: classification, enabled, install_time
  extensions_index.json                     # cached search results (optional)
```

### Security Checklist (Installer)
1. Download over HTTPS only.
2. Verify SHA-256 against registry value (refuse on mismatch).
3. Unzip with zip-slip protection: reject any entry whose resolved path escapes target dir.
4. Max download size: 50 MB (stream with `response.iter_content`, abort if exceeded).
5. Never `exec`/`import`/`eval` any code from the extension. Treat .vsix as untrusted data.

---

## 3. UI Brief — Panel Layout (ASCII)

```
┌─────────────────────────────────────────────────────────────────┐
│ Activity Bar: [Explorer] [Search] [Source Control] [Extensions] │
│                                                                 │
│ Extensions Panel (dock, Ctrl+Shift+X)                           │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Search extensions in Open VSX Registry...     [Offline ⚠]   │
├─────────────────────────────────────────────────────────────────┤
│ Tabs: [Marketplace] [Installed]                                 │
│                                                                 │
│ Marketplace Tab:                                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🎨 Dracula Theme Official            [SUPPORTED]  Install   │ │
│ │    dracula-theme.theme-dracula v2.25.1  439k downloads      │ │
│ │    The official Dracula Theme...                             │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 🎨 Dracula Colorful                [SUPPORTED]  Install   │ │
│ │    nszihan.vscode-dracula-colorful v2.2.1  17k downloads    │ │
│ │    A vibrant variant of Dracula...                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Installed Tab:                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🎨 Dracula Theme Official            [SUPPORTED]  Disable  │ │
│ │    Theme: Dracula, Dracula Soft                              │ │
│ │    [Apply] [Uninstall]                                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Detail View (click extension):                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Dracula Theme Official                                       │ │
│ │ [SUPPORTED]  License: MIT  Repo: github.com/dracula/...     │ │
│ │                                                              │ │
│ │ Contributions:                                               │ │
│ │   • Themes: Dracula, Dracula Soft                            │ │
│ │                                                              │ │
│ │ [README content...]                                          │ │
│ │                                                              │ │
│ │ [Install] / [Uninstall] / [Disable]                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### States
- **Loading**: Spinner in list, "Searching..."
- **Empty**: "No extensions found. Try a different query."
- **Offline**: Yellow banner "Offline — showing installed extensions", search disabled.
- **Error**: Red banner "Registry unreachable: <error>", retry button.
- **Installed**: Green checkmark, "Installed" badge, Disable/Uninstall buttons.

---

## 4. Architecture Visualization (for GATE-21-EXTENSIONS.md)

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ UI Panel     │────▶│ RegistryClient   │────▶│ Open VSX API    │
│ (Extensions- │     │ (pure Python)    │     │ (HTTPS, 10s TO) │
│  Panel)      │     │ search/detail/   │     └─────────────────┘
│              │     │ download         │            │
└──────────────┘     └──────────────────┘            ▼
       │                      │              ┌─────────────────┐
       │                      ▼              │ Downloaded .vsix│
       │              ┌──────────────────┐   │ (stream, 50MB)  │
       │              │ Installer        │   └─────────────────┘
       │              │ (zip-slip safe,  │            │
       └─────────────▶│  SHA-256 verify) │            ▼
                      └──────────────────┘   ┌─────────────────┐
                             │              │ Unzip to        │
                             ▼              │ ~/.medha/ext/...│
                      ┌──────────────────┐  └─────────────────┘
                      │ Contributions    │            │
                      │ Loader           │            ▼
                      │ (parse pkg.json, │   ┌─────────────────┐
                      │  classify, load  │   │ Theme Mapper    │──▶ Editor Palette
                      │  themes/snippets/│   │ (VS Code → Qt)  │     QSyntaxHighlighter
                      │  grammars)       │   └─────────────────┘
                      └──────────────────┘            │
                             │                        ▼
                             ▼                 ┌─────────────────┐
                      ┌──────────────────┐     │ Snippet Provider│──▶ Completion
                      │ Classification   │     │ (prefix→body,   │     Model
                      │ SUPPORTED/       │     │  $1/$0)         │
                      │ PARTIAL/UNSUPP.  │     └─────────────────┘
                      └──────────────────┘
```

---

## 5. Worst-Case Scenarios (for GATE-21-EXTENSIONS.md)

| Scenario | Mitigation |
|----------|------------|
| No internet / registry down | Offline banner, show installed only, no crash/freeze |
| Registry API changed | Versioned client, graceful degradation, log raw response |
| Corrupt / malicious .vsix | SHA-256 mismatch → refuse; zip-slip → refuse; 50 MB → abort |
| Huge download (>50 MB) | Streaming download with size counter, abort early |
| Theme JSON with bad values | Validate keys, clamp colors to `#RRGGBB`, fallback to defaults |
| Extension with only JS code | Classify `UNSUPPORTED`, show badge + tooltip, never execute |
| TextMate grammar too complex | Implement documented subset only (basic regex rules); mark `NOT DONE` if full engine needed |

---

## 6. Victory Demo Script (for GATE-21-EXTENSIONS.md)

1. Launch MEDHA: `.venv/bin/python -m medha`
2. Open Extensions panel (Ctrl+Shift+X)
3. Search "dracula" → see results with [SUPPORTED] badges
4. Click "Dracula Theme Official" → detail view shows themes
5. Click Install → downloads, verifies SHA-256, unzips to `~/.medha/extensions/...`
6. Click "Apply" on "Dracula" theme → editor colors change live (no restart)
7. Type snippet prefix (from installed snippet ext) → completion shows, Tab expands with $1/$0
8. Click Uninstall → extension removed from disk, theme reverts
9. Disconnect network → panel shows "Offline", installed still works
10. Run `verify_medha.py` → 6/6 PASS

---

## 7. File Creation / Change Summary

### New Files
```
medha/extensions/__init__.py
medha/extensions/models.py
medha/extensions/registry.py
medha/extensions/installer.py
medha/extensions/contributions.py
medha/extensions/manager.py
medha/extensions/ui/panel.py
medha/extensions/ui/worker.py
tests/test_extensions_registry.py
tests/test_extensions_installer.py
tests/test_extensions_contributions.py
tests/test_extensions_apply.py
docs/GATE-21-EXTENSIONS.md
docs/HANDOFF-EXTENSIONS.md
```

### Modified Files
```
medha/app.py              # Add Extensions dock, activity button, Ctrl+Shift+X
medha/theme.py            # Add theme application API (palette + highlighter formats)
medha/highlighter.py      # Make highlighter configurable from theme data
medha/editor_widget.py    # Add snippet completion integration point
```

---

## 8. Implementation Order (Phases)

1. **Phase 0** — This document + `docs/GATE-21-EXTENSIONS.md` (architecture, worst-case, victory)
2. **Phase 1** — `registry.py` + `tests/test_extensions_registry.py` (GATE 1)
3. **Phase 2** — `installer.py`, `contributions.py`, `models.py` + tests (GATE 2)
4. **Phase 3** — Theme mapper, snippet provider, highlighter integration + tests (GATE 3)
5. **Phase 4** — UI panel, dock, activity button, wiring in `app.py` (GATE 4)
6. **Phase 5** — `docs/HANDOFF-EXTENSIONS.md` with real outputs