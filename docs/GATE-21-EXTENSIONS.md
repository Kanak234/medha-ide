# GATE-21-EXTENSIONS — Architecture, Worst Cases, Victory Criteria

## VISUALIZE — ASCII Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MEDHA IDE EXTENSIONS PIPELINE                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌────────────────────┐      ┌─────────────────────┐
  │  UI Layer    │      │  Registry Client   │      │   Open VSX API      │
  │  (Qt Widgets)│      │  (Pure Python)     │      │   (HTTPS, REST)     │
  │              │      │                    │      │                     │
  │ Extensions   │─────▶│  search(query)     │─────▶│ GET /api/-/search   │
  │ Panel        │      │  detail(ns,name)   │      │ GET /api/ns/name    │
  │              │      │  download(url,     │      │ GET /api/.../file/  │
  │  Signals:    │      │   sha256) -> Path  │      │    *.vsix           │
  │  search_req  │      │                    │      │                     │
  │  install_req │      │  10 s timeout      │      │  Rate limits:       │
  │  uninstall   │      │  Streaming DL      │      │  reasonable         │
  │  apply_theme │      │  50 MB max         │      └─────────────────────┘
  │  list_inst   │      └────────┬───────────┘
  └──────────────┘               │
         ▲                        ▼
         │               ┌────────────────────┐
         │               │   Installer        │
         │               │  (Security First)  │
         │               │                    │
         │               │  install(vsix)     │
         │               │  uninstall(id)     │
         │               │  list_installed()  │
         │               │                    │
         │               │  • HTTPS only      │
         │               │  • SHA-256 verify  │
         │               │  • Zip-slip guard  │
         │               │  • 50 MB limit     │
         │               │  • No code exec    │
         │               └────────┬───────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────┐
         │               │  Contributions     │
         │               │  Loader            │
         │               │                    │
         │               │  parse package.json│
         │               │  classify:         │
         │               │    SUPPORTED       │
         │               │    PARTIAL         │
         │               │    UNSUPPORTED     │
         │               │                    │
         │               │  load themes[]     │
         │               │  load snippets[]   │
         │               │  load grammars[]   │
         │               │  (subset only)     │
         │               └────────┬───────────┘
         │                        │
         ▼                        ▼
  ┌──────────────┐      ┌────────────────────┐
  │ Theme Mapper │      │ Snippet Provider   │
  │              │      │                    │
  │ VS Code JSON │      │ prefix -> body     │
  │   colors     │      │ $1/$0 placeholders │
  │ tokenColors  │      │ per language       │
  │   scopes     │      │                    │
  │   ──▶ Qt     │      │ integrates with    │
  │   palette    │      │ QCompleter /       │
  │ QSyntaxHigh- │      │ custom completion  │
  │ lighter fmt  │      │                    │
  └──────────────┘      └────────────────────┘
         │                        │
         └──────────┬─────────────┘
                    ▼
         ┌────────────────────┐
         │   Editor Widget    │
         │ (AdvancedCodeEditor│
         │  Widget)           │
         │                    │
         │ setPalette(colors) │
         │ setHighlighter(fmt)│
         │ addSnippets(list)  │
         └────────────────────┘


DATA FLOW SUMMARY:
1. User types query → RegistryWorker(QThread) → Open VSX → ExtensionInfo list → UI list
2. User clicks Install → DownloadWorker → .vsix file → Installer → ~/.medha/extensions/...
3. Installer emits installed → ContributionsLoader parses package.json → classifies
4. If SUPPORTED: themes → ThemeMapper → Editor palette + Highlighter formats
5. If SUPPORTED: snippets → SnippetProvider → Editor completion model
6. If PARTIAL: declarative parts only, JS ignored with warning badge
7. If UNSUPPORTED: badge only, no contribution loaded
```

---

## WORST CASE — Threat Model & Mitigations

| # | Scenario | Impact | Mitigation (Implemented) |
|---|----------|--------|--------------------------|
| 1 | **No internet / registry down** | User cannot search/install | Offline banner, cached installed list works, no crash/freeze. Network in QThread with 10s timeout. |
| 2 | **Registry API changed** | Search/detail parse fails | Defensive JSON parsing (`.get()`), log raw response, fallback to cached index. |
| 3 | **Corrupt .vsix (bad ZIP)** | Crash on unzip | `zipfile.ZipFile` in try/except, corrupt → delete partial, show error. |
| 4 | **Malicious .vsix (zip-slip)** | Path traversal write | `extractall` with per-member path validation: `os.path.relpath(target, dest).startswith('..')` → refuse. |
| 5 | **Malicious .vsix (SHA-256 mismatch)** | Supply chain attack | Download stream → hashlib.sha256 incrementally → compare to registry value → mismatch = delete + refuse. |
| 6 | **Huge download (>50 MB)** | DoS / disk fill | Stream with `iter_content(8192)`, running total, abort + delete if > 50*1024*1024. |
| 7 | **Theme JSON with bad values** | UI corruption / crash | Validate each color: regex `^#[0-9a-fA-F]{6}$`, clamp, fallback to default. `tokenColors` scopes: ignore unknown, log warning. |
| 8 | **Extension with only JS code** | False expectation | Classify `UNSUPPORTED`, badge + tooltip "Needs VS Code runtime — not supported in MEDHA", never import/exec. |
| 9 | **Extension with JS + themes** | Partial works, JS ignored | Classify `PARTIAL`, load themes/snippets/grammars, show badge "JS code not supported". |
| 10 | **TextMate grammar too complex** | Incomplete highlighting | Implement documented subset: `patterns` with `match`/`name` regex only. No `include`, `begin/end`, `repository`. Mark `NOT DONE` in handoff if full engine needed. |
| 11 | **Concurrent install/uninstall** | Race condition | Serialize via queue in Manager; one operation at a time. |
| 12 | **Corrupt ~/.medha/extensions/** | App misbehavior | `list_installed()` validates manifest.json, skips broken dirs, logs warning. |

---

## VICTORY — Demo Script (Manual Verification)

> Run each step, observe expected behavior. All steps must pass for Gate 4.

### Prerequisites
```bash
cd /home/kanak07/chromium-shift/medha-ide
.venv/bin/python -m medha &
# Wait for window to appear
```

### Step-by-Step

| Step | Action | Expected |
|------|--------|----------|
| 1 | Press `Ctrl+Shift+X` or click Extensions icon in activity bar | Extensions panel opens as right dock |
| 2 | Panel shows "Marketplace" and "Installed" tabs | Two tabs visible |
| 3 | Type `dracula` in search box, press Enter | Spinner → 5+ results with [SUPPORTED] badges |
| 4 | Click "Dracula Theme Official" | Detail view opens: README, license MIT, repo link, themes list |
| 5 | Click **Install** on detail view | Progress → "Installed" badge, Disable/Uninstall buttons appear |
| 6 | Switch to **Installed** tab | Dracula Theme Official listed with themes: Dracula, Dracula Soft |
| 7 | Click **Apply** next to "Dracula" theme | Editor background/foreground/selection colors change **immediately** (no restart) |
| 8 | Open a `.c` file, type `mai` → Tab | If snippet extension installed: `main()` snippet expands with cursor at `$1` |
| 9 | Click **Uninstall** on Dracula theme | Extension removed from `~/.medha/extensions/`, theme reverts to default |
| 10 | Disconnect WiFi / unplug ethernet | Panel shows yellow banner "Offline — showing installed extensions" |
| 11 | Search box disabled, Installed tab still works | No crash, no freeze |
| 12 | Reconnect network, search "dracula" again | Works normally |
| 13 | Close MEDHA, run `verify_medha.py` | **6/6 PASS** (same as before) |

### Automated Gate Checks

| Gate | Command | Must Show |
|------|---------|-----------|
| 1 | `cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python -m pytest tests/test_extensions_registry.py -v` | All tests PASS + real "dracula" search prints names |
| 2 | `cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python -m pytest tests/test_extensions_installer.py tests/test_extensions_contributions.py -v` | Zip-slip rejected, round-trip PASS, 3 fixtures classified |
| 3 | `cd /home/kanak07/chromium-shift/medha-ide && .venv/bin/python -m pytest tests/test_extensions_apply.py -v` | Theme changes palette, snippet expands |
| 4 | `timeout --foreground 10 .venv/bin/python -m medha` (then `verify_medha.py`) | No traceback, 0 "already running", verify_medha 6/6 |

---

## NOT DONE / DEFERRED (Honest)

- **Full TextMate Grammar Engine**: Only a regex `match`/`name` subset implemented. Complex grammars (nested `begin`/`end`, `include`, `repository`) marked `NOT DONE`.
- **Extension Auto-Update**: Not in scope. Manual reinstall required.
- **Extension Dependencies**: Not resolved (VS Code `extensionDependencies` ignored).
- **Icon Download/Display**: Placeholder icons used; real icon fetch deferred.
- **README/Changelog Rendering**: Plain text only, no Markdown rendering.
- **Workspace-Level Extensions**: Only user-global `~/.medha/extensions/` supported.
- **Extension Settings/Configuration**: `contributes.configuration` ignored (no settings UI).

---

## Open Questions

1. Should `~/.medha/extensions/` be configurable via env var?
2. Do we need a background indexer for faster search (local cache of registry)?
3. How to handle theme `semanticHighlighting: true` — integrate with LSP semantic tokens?
4. Snippet tab stops beyond `$1`/`$0` — implement full VS Code snippet grammar?
5. Grammar injection: extend existing highlighter vs replace? Current plan: extend.