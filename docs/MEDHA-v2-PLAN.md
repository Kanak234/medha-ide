# MEDHĀ IDE v2.0 — "Bug-free + VS Code-style UI" plan (Nov 2026)

Owner: Kanak Prabhakar · Goal: fix what is live on the Microsoft Store (v1.1.0) instead of building new apps.
Who does what:
- **ChatGPT (Codex, GitHub-connected)** — Track A: the new UI. Also the Microsoft Store submission in Partner Center (it is logged in there).
- **Nemotron 3 Ultra (OpenCode on the laptop)** — Track B: bug hunting + tests. Works on its own branch.
- **Claude** — reviews every PR against this file, runs the tests/smoke, reports what is still broken.
Release rule: fix and push all month, publish to the Store **once** at the end (or at once for a crash/data-loss bug).

## 0. Verified state (checked 2026-11-05 on a clean clone, Python 3 + PySide6, offscreen)
- 83 unit tests pass, 2 skipped; 1 test needs internet (`TestRegistryRealCall`) → must be marked `@pytest.mark.network` and skipped offline.
- The window opens with **0 Python exceptions**; menus: File Edit View Run Analyze Debug LSP Git Build Tools Help.
- pyflakes: 16 dead variables, 1 duplicate function (`load_extension_contributions` defined twice in `extensions/contributions.py`).

## 1. Bugs found so far (fix in this order)
| # | Severity | Bug | Where | Fix |
|---|---|---|---|---|
| B1 | **High (UX)** | The code editor is squeezed to ~130 px: 8 tool docks are tabified on the RIGHT and take ~80 % of the width on first launch. | `medha/app.py` 206–269 | New layout (Track A). Until then: `resizeDocks` so the editor gets ≥ 60 %, right docks start hidden. |
| B2 | Medium | `&` in tab/dock titles is read as a keyboard mnemonic → shows "Compiler Output _Issues", "Live Memory _Pointers", dock "CONSOLE SAFETY DIAGNOSTICS". | `app.py` 174, 196, 210 + all `addTab`/`QDockWidget` titles | Escape as `&&` (or drop "&"). Add a test that no visible title contains a single `&`. |
| B3 | **High** | The terminal is a `QProcess` with no pseudo-terminal: bash prints "cannot set terminal process group / no job control"; interactive programs (vim, top, colours, Ctrl+C) do not work. | `medha/terminal.py` | Linux/macOS: `pty.openpty()` + `QSocketNotifier`; Windows (the Store build!): ConPTY via `pywinpty`. Keep the QProcess path as fallback. |
| B4 | Medium | `load_extension_contributions` defined twice — the second silently replaces the first. | `extensions/contributions.py` 675/698 | Keep one, add a test. |
| B5 | Low | 8 `except Exception: pass` hide real errors. | `grep -rn "except Exception" medha` | Log with `logging.exception` and show a status-bar message. |
| B6 | Low | Test suite fails offline (real network call). | `tests/test_extensions_registry.py` | `@pytest.mark.network`, skipped unless `MEDHA_NETWORK_TESTS=1`. |
| B7 | Low | 16 unused variables (pyflakes). | dsa_engine, panel.py, renderers | Remove. CI runs `pyflakes medha` and must be clean. |
| B8 | Medium | Closing a window with active disassembly can call a deleted QTextEdit. | `app.py` closeEvent | Stop child QProcesses before widget teardown. |
| B9 | High | Closing an edited tab discarded unsaved work without confirmation. | `app.py` close_tab/closeEvent | Save/Discard/Cancel guard, including cancelled Save As. |
More bugs come from Track B (section 3) — append them to this table with the same columns.

## 2. Track A — New UI like VS Code / Antigravity (ChatGPT)
Target layout (one screen, nothing hidden that a beginner needs):
```
┌ title bar (Medhā · file · project) ─────────────────────── command centre (Ctrl+Shift+P) ┐
│A│ SIDE BAR (Explorer / Search / Run & Debug / Git / Extensions / DSA / AI) │ EDITOR TABS  │
│C│                                                                          │  editor      │
│T│                                                                          │  + minimap   │
│ │                                                                          ├──────────────┤
│B│                                                                          │ PANEL: Terminal · Output · Problems · Debug Console · Turbo C screen │
└ status bar: branch · errors/warnings · Ln/Col · language · encoding · compiler · theme ──┘
```
Rules:
1. **Activity bar** (48 px icons, left) switches the **side bar** view — replaces the 8 right-hand docks. DSA Visualizer, Memory, Disassembly, GDB, Outline, AI and Extensions become side-bar views or panel tabs.
2. **Editor gets ≥ 60 % width** at 1366×768 and up. Side bar and panel are collapsible (Ctrl+B, Ctrl+J) and remember their size (QSettings).
3. **Command palette** (Ctrl+Shift+P) lists every action; **Quick Open** (Ctrl+P) opens files. Keep the existing `command_palette.py`, make it the main way to find things.
4. **Menus**: File Edit Selection View Go Run Terminal Help (VS Code order). Analyze/LSP/Git/Build/Debug items move under these.
5. **Theme**: one dark theme ("Medhā Dark", VS Code Dark Modern-like palette) + one light theme. Single QSS file, colour tokens in one place (`theme.py`). Font: JetBrains Mono / Cascadia Code fallback. Tab close button = small grey ✕ (not a red box).
6. **Welcome tab** on first launch: New C file · Open folder · Recent · Turbo C examples · "Learn DSA visually".
7. Status bar shows real data only (no fake "Live OS" text); CPU/RAM goes behind a toggle.
8. No feature is removed — only moved. Every old menu action must still be reachable (test: list of action names before == after).
Acceptance: screenshots at 1366×768 and 1920×1080 in light + dark, before/after, committed to `docs/screenshots/v2/`.

## 3. Track B — Bug hunt until "bug-free" (Nemotron via OpenCode)
Definition of bug-free for v2.0: all tests green offline, pyflakes clean, smoke test opens + exercises every menu action without an exception, and the manual checklist below passes on Windows and Ubuntu.
Steps:
1. Fix B4–B7 (small, safe) first; one commit each.
2. Write `tests/test_ui_smoke.py` (offscreen): open the main window, trigger **every** QAction in every menu one by one (with dialogs auto-closed), assert no exception and the window is still alive. Every failure = a new row in section 1.
3. Unit tests for the parts without any today: `runner.py`, `project_manager.py`, `toolchains.py`, `debugger.py`, `turbo/` (target: every public function has at least one test).
4. Run `pyflakes`, `python -m compileall`, and `ruff check --select E9,F` and fix everything.
5. Fix B3 (pty terminal) last — it touches Windows code; test both paths.
Manual checklist (both OSes): new C file → build → run → program reads `scanf` input from the terminal → debug with a breakpoint → Turbo C graphics program draws → DSA visualizer steps → save, close, reopen project → install one extension from Open VSX → uninstall it.

## 4. Release (ChatGPT, end of month)
1. Version 2.0.0 everywhere (`packaging/*.metainfo.xml`, Windows package manifest, `store/listing.md`).
2. Build the Windows package with the existing script in `packaging/windows`, test on Windows (install, launch, uninstall).
3. Partner Center: new submission → Packages (upload) → Store listings (What's new + new screenshots from `docs/screenshots/v2/`) → Submit. Snap: build + `snapcraft upload --release=candidate`, promote to stable after one day.

## 5. After v2 — v3 "Polyglot": many languages in one IDE (owner idea, 2026-11-05)
Owner's wish: MEDHĀ alone should cover what the JetBrains family covers (IntelliJ, PyCharm, CLion, WebStorm, GoLand, Rider, DataGrip…).
Honest scope: JetBrains' code and plugins are proprietary — nothing of theirs can be copied or bundled. The open way to get there
is the same one VS Code uses: **language servers (LSP) + debug adapters (DAP)**. MEDHĀ already has `medha/lsp.py`.
Start only after v2.0 is live and bug-free. One language per release, each one fully working (completion, go-to-definition,
diagnostics, rename, format, run, debug) before the next:
| Step | Language (JetBrains equivalent) | Language server | Debugger |
|---|---|---|---|
| 3.1 | C/C++ (CLion) — make the current support complete | clangd | gdb/lldb via DAP |
| 3.2 | Python (PyCharm) | pyright / python-lsp-server | debugpy |
| 3.3 | Java (IntelliJ) | Eclipse JDT LS | java-debug |
| 3.4 | JavaScript/TypeScript (WebStorm) | typescript-language-server | js-debug |
| 3.5 | Go (GoLand), Rust (RustRover) | gopls, rust-analyzer | delve, codelldb |
| 3.6 | SQL (DataGrip) | sqls + a simple DB browser (SQLite first) | — |
Each server is downloaded on first use (not bundled) to keep the Store package small; everything still works offline after that.

## Track A implementation evidence (2026-11-05)

Implemented on `v2-ui`: Track A steps 1–8, B1 and B2. Required offline/lint
prerequisites B4/B6/B7 are included as separate commits. B8/B9 were discovered
while exercising the UI and are fixed in this branch. B3/B5 remain Track B work.
See [verification details](V2-UI-VERIFICATION.md) and
[before/after screenshots](screenshots/v2/README.md). Linux checks: 106 passed,
1 explicit network skip; pyflakes clean; 20 UI smoke tests passed. Windows/manual
release acceptance remains pending.
