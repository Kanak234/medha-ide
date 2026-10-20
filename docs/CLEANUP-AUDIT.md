# MEDHA-IDE Cleanup Audit

**Generated**: 2026-10-21  
**Branch**: repo-cleanup  
**Auditor**: OpenCode cleanup agent

## Decision Criteria
- **KEEP**: Part of the real `medha/` PySide6 package, or essential project infrastructure
- **ARCHIVE**: Old experiments, fake builds, build leftovers, web leftovers not used by `medha/`
- **KANAK DECIDES**: Ambiguous files where intent is unclear

---

## Top-Level Audit Table

| Path | Decision | Evidence |
|------|----------|----------|
| `.git/` | KEEP | Git history |
| `.github/` | KEEP | GitHub workflows (if any) |
| `.pytest_cache/` | ARCHIVE | Build cache, regenerated |
| `.venv/` | ARCHIVE | Local venv, not tracked (in .gitignore) |
| `docs/` | KEEP | Documentation folder (contents audited separately) |
| `legacy/` | **ARCHIVE** | React/Vite web build with hardcoded fake outputs; `tsconfig.json` paths point here; nothing in `medha/` imports it |
| `medha_demo/` | **ARCHIVE** | Demo binaries (`demo`, `demo_c`, `demo_cpp`) and scripts; no imports from `medha/` |
| `medha_studio/` | **ARCHIVE** | Separate app (`app.py`, `run.sh`, `build_out/`, `demos/`); no imports from `medha/` |
| `medha/` | **KEEP** | **The ONLY real app** — PySide6 native IDE; entry point `medha/__main__.py` |
| `offline_sdk_bundle/` | **ARCHIVE** | Documentation library only (markdown files); padded with 656 MB filler historically; `medha/` does not import it |
| `tests/` | **KEEP** | Test suite for `medha/` package |
| `.gitignore` | **KEEP** | Will be updated |
| `ABOUT.md` | **ARCHIVE** | Describes fake web build (Monaco, browser, LibreOffice, VLC, game engine); not in `medha/` |
| `ARCHITECTURE.md` | **ARCHIVE** | Describes fake subsystem architecture (SARASVATĪ/KĀLĪ/MAHĀLAKṢMĪ/VAISHNAVĪ) and Monaco/web features; `medha/` has none of this |
| `build_packages.py` | **KEEP** | Packaging script for `medha/` (PyInstaller, .deb, AppImage) |
| `LICENSE` | **KEEP** | License file |
| `main` | **ARCHIVE** | Build leftover binary (ELF) |
| `main.c` | **ARCHIVE** | Build leftover C source |
| `main.py` | **ARCHIVE** | Old entry point (not `medha/__main__.py`); imports nothing from `medha/` |
| `main.s` | **ARCHIVE** | Build leftover assembly |
| `MEDHA_100_FEATURES.md` | **ARCHIVE** | Lists 100 fake features (Monaco, browser, LibreOffice, VLC, game engine, databases, etc.); `medha/` has none |
| `MEDHA_101_FEATURES.md` | **ARCHIVE** | Same as above + 1 fake feature |
| `MEDHA_CHECKPOINT_LOOP.md` | **ARCHIVE** | Process doc for fake build |
| `medha_v01.py` | **ARCHIVE** | Old prototype script |
| `medha-ide.spec` | **ARCHIVE** | PyInstaller spec for old build |
| `package-lock.json` | **ARCHIVE** | Web leftover; `build_packages.py` and `medha/` do not use npm |
| `package.json` | **ARCHIVE** | Web leftover; defines React/Vite/Monaco deps; `medha/` is pure Python/PySide6 |
| `PROJECT_HISTORY.md` | **ARCHIVE** | History of fake web build |
| `pytest.ini` | **KEEP** | Pytest config for `medha/` tests |
| `README.md` | **KEEP** | Will be rewritten truthfully |
| `RELEASE_NOTES.md` | **ARCHIVE** | Release notes for fake web build |
| `requirements.txt` | **KEEP** | Real dependencies for `medha/` (PySide6, psutil, requests) |
| `run1.txt` | **ARCHIVE** | Build leftover log |
| `run2.txt` | **ARCHIVE** | Build leftover log |
| `start-medha.sh` | **KEEP** | Will be fixed (portable, no hardcoded paths) |
| `SYSTEM_REQUIREMENTS.md` | **ARCHIVE** | Requirements for fake web build (Android, Web, editions) |
| `TEST_REPORT.md` | **ARCHIVE** | Vitest report for fake web build (TypeScript, Vite, Monaco) |
| `THIRD_PARTY_NOTICES` | **KEEP** | License attributions |
| `TROUBLESHOOTING.md` | **ARCHIVE** | Troubleshooting for fake web build (browser, SQLite WASM, dev server) |
| `tsconfig.json` | **ARCHIVE** | Web leftover; `include: ["legacy/src"]`; `medha/` and `build_packages.py` don't use it |
| `verify_dsa_visualizer.py` | **KEEP** | Verification script for DSA visualizer in `medha/` |
| `verify_medha_p3_p6.py` | **KEEP** | Adversarial validator for Phases 3-6 (LSP, debugger, git, build) |
| `verify_medha.py` | **KEEP** | Adversarial validator for Phases 1-2 (window, runner, terminal, diagnostics) |

---

## `docs/` Folder Audit

| File | Decision | Evidence |
|------|----------|----------|
| `AUDIT-2026-10.md` | **KEEP** | Previous audit record |
| `EXTENSIONS-PLAN.md` | **KEEP** | Extensions plan for real `medha/` |
| `GATE-21-EXTENSIONS.md` | **KEEP** | Gate doc for extensions |
| `HANDOFF-EXTENSIONS.md` | **KEEP** | Handoff for extensions work |
| `HANDOFF.md` | **KEEP** | Previous handoff |

---

## `medha/` Package — All KEPT (Real App)

All files under `medha/` are part of the real PySide6 application. No deletions.

Key modules verified:
- `medha/__main__.py` — Entry point (`python -m medha`)
- `medha/app.py` — MainWindow with editor, terminal, problems, LSP, GDB, git, CMake, AI, extensions
- `medha/editor.py`, `editor_widget.py` — Code editor with syntax highlighting
- `medha/terminal.py` — Integrated terminal (real shell)
- `medha/runner.py` — Process runner (real gcc/g++/python3)
- `medha/problems.py` — Problems panel (parses gcc stderr)
- `medha/lsp.py` — LSP client (clangd, pylsp)
- `medha/debugger.py`, `debugger_engine.py` — GDB/debugpy debugger
- `medha/git_backend.py` — Git operations
- `medha/build.py`, `build_system.py` — CMake/Make build system
- `medha/ai.py`, `ai_panel.py` — Local Ollama AI panel
- `medha/extensions/` — Open VSX extensions (themes, snippets, grammar subset)
- `medha/explorer.py` — Project explorer
- `medha/visualizers/` — Memory view, DSA visualizer
- `medha/compiler/disassembly.py` — Live disassembly (gcc -S)

---

## Summary Counts

| Category | Count |
|----------|-------|
| KEEP (top-level) | 11 |
| ARCHIVE (top-level) | 26 |
| KANAK DECIDES | 0 |
| KEEP (docs/) | 5 |
| KEEP (medha/) | 31 files |

---

## Verification Commands (to run after cleanup)

```bash
# 1. Git status
git status --short

# 2. Pytest
.venv/bin/python -m pytest tests -q

# 3. Validator C0-C5
.venv/bin/python verify_medha.py | grep RESULT

# 4. Validator C6-C12
.venv/bin/python verify_medha_p3_p6.py | grep RESULT

# 5. Smoke test (10s)
timeout --foreground 10 .venv/bin/python -m medha > /tmp/m.log 2>&1
grep -c Traceback /tmp/m.log  # must be 0
```