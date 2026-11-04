# Track A verification — 2026-11-05

Branch: `v2-ui`. Base: `92e278b`.

## Implemented

- B1: 48 px activity bar, scrollable sidebar views, editor-first splitters, bottom panel; Ctrl+B/Ctrl+J and QSettings size/visibility persistence.
- B2: escaped literal ampersands in docks, debugger tabs, and dynamically named editor tabs.
- Command centre, command palette, incremental Quick Open, workspace text search, Git view, and File/Edit/Selection/View/Go/Run/Terminal/Help menus.
- Existing menu actions preserved as the same QAction objects; original action names captured in `tests/fixtures/v1_actions.json` and checked after relocation.
- Medhā Dark/Light with shared QSS and central color tokens, readable activity icons, grey close buttons, editor gutter and clickable minimap. Windows PyInstaller spec includes the QSS resource.
- Welcome page with new C file, open folder/file, current Recent list, Turbo examples, and DSA entry points.
- Real local branch, document/language/encoding, compiler availability and build diagnostics; optional CPU/RAM sampling.
- B4, B6, B7: prerequisite duplicate-loader, offline-test and lint cleanup in separate commits.
- Newly documented B8/B9: orderly process shutdown and Save/Discard/Cancel protection for edited tabs/windows.

## Checks by step

All counts below are offline. The real registry test is explicitly skipped unless
`MEDHA_NETWORK_TESTS=1`; local fake registry-server tests still run.

| Step | Full pytest | UI smoke |
|---|---|---|
| Baseline | 85 passed, real-network test deselected | baseline screenshots |
| B6 | 86 passed, 1 skipped | window opens |
| B4/B7 | 87 passed, 1 skipped | 1 passed |
| B2/B8 | 88 passed, 1 skipped | 2 passed |
| Workbench/B1 | 91 passed, 1 skipped | 5 passed |
| Navigation | 93 passed, 1 skipped | 7 passed |
| Themes/minimap | 94 passed, 1 skipped | 8 passed |
| Welcome/close guard | 96 passed, 1 skipped | 10 passed |
| Status/actions | 98 passed, 1 skipped | 12 passed |
| Final regression checks | **106 passed, 1 skipped** | **20 passed** |

Pyflakes is clean after B7 and at every subsequent completed step.

```sh
QT_QPA_PLATFORM=offscreen python -m pytest -q
python -m pyflakes medha
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_ui_smoke.py -q
```

UI tests check tool routing, both screen sizes/themes, actual text viewport width,
keyboard toggles, settings restoration into a second window, palette action
preservation, Quick Open, Search, Recent, minimap navigation, real status updates,
unsaved-close cancellation and cancelled Save As. Requests are blocked during UI
startup, and Qt callback exceptions are collected as failures.

The all-action smoke test triggers every menu action from the legitimate Welcome
(no active document) state. Dialogs are cancelled and external CMake build calls
are stubbed. It verifies UI wiring and survival, not every compiler/debugger backend.
Focused tests exercise document operations separately.

## Review limits

- Screenshots and tests ran on Linux/PySide6 6.12. Windows install/launch/uninstall and the full cross-platform release checklist are still required before release.
- B3 (PTY/ConPTY) and B5 (remaining broad exception handlers) remain Track B work.
- Original UI supported only dark; before-light images cannot be captured authentically. Both new themes have full after evidence in `screenshots/v2/`.
- No Store submission, release version change, or merge is included.
