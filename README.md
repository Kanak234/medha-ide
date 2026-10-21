<p align="center">
  <img src="docs/assets/logo-mark.svg" width="80" alt="MEDHĀ logo">
</p>

# MEDHĀ IDE

**Native PySide6 offline IDE for C/C++/Python — editor, real compiler runs, terminal, problems panel, LSP (clangd/pylsp), GDB/debugpy debugger, Git, CMake build, local Ollama AI panel, Open VSX extensions (themes/snippets/grammar subset).**

---

## What MEDHA Is

MEDHĀ is a **native desktop IDE** written in Python with PySide6 (Qt 6). It is offline-first: everything works without internet except searching/downloading extensions from Open VSX. No Electron, no web views, no bundled browsers. It integrates your system toolchain (gcc, g++, gdb, python3, clangd, pylsp, cmake, git, ollama) into a single window with dockable panels.

**Not a web app.** The `legacy/` folder (archived) was a React/Vite/Monaco prototype — it is not MEDHA.

---

## Real Features (Implemented in `medha/`)

| Feature | Module | Status |
|---------|--------|--------|
| Multi-tab code editor with syntax highlighting | `medha/editor.py`, `editor_widget.py` | ✅ |
| Real compilation & execution (gcc/g++/python3) | `medha/runner.py` | ✅ |
| Integrated terminal (real shell via QProcess) | `medha/terminal.py` | ✅ |
| Problems panel (parses compiler stderr) | `medha/problems.py` | ✅ |
| LSP client — clangd (C/C++), pylsp (Python) | `medha/lsp.py` | ✅ (needs clangd / python-lsp-server installed) |
| GDB debugger (C/C++) + debugpy (Python) | `medha/debugger.py`, `debugger_engine.py` | ✅ GDB verified; debugpy needs `pip install debugpy` |
| Git status, stage, commit, log, diff | `medha/git_backend.py` | ✅ |
| CMake configure & build (multi-target Debug/Release) | `medha/build.py`, `build_system.py` | ✅ |
| Live disassembly (gcc -S) | `medha/compiler/disassembly.py` | ✅ |
| Project explorer | `medha/explorer.py` | ✅ |
| Local Ollama AI chat panel | `medha/ai.py`, `ai_panel.py` | ✅ |
| Open VSX extensions: themes, snippets, grammar subset | `medha/extensions/` | ✅ |
| Memory visualizer & pointer inspector | `medha/visualizers/memory_view.py` | ✅ |
| DSA visualizer (arrays, trees, graphs) | `medha/dsa_visualizer/` | ✅ |
| Symbol outline | `medha/editor_widget.py` | ✅ |
| Static safety linter (cppcheck integration) | `medha/analyzers/linter.py` | ✅ |

---

## Install

```bash
# 1. Clone and enter
git clone <this-repo> medha-ide
cd medha-ide

# 2. Create venv and install deps
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# Requirements: PySide6>=6.12, psutil>=7.2, requests>=2.34

# 3. Run
.venv/bin/python -m medha
```

**System dependencies** (install via your package manager):
- `gcc` `g++` `gdb` — C/C++ compilation & debugging
- `python3` — Python execution & debugpy
- `clangd` — C/C++ LSP (optional but recommended)
- `pylsp` / `python-lsp-server` — Python LSP (optional)
- `cmake` `make` — CMake build system
- `git` — Git integration
- `ollama` — Local AI (optional)
- `cppcheck` — Static safety linting (optional)

---

## Run Tests & Validators

```bash
# Unit tests
.venv/bin/python -m pytest tests -q

# Adversarial validator (Phases 1-2): window, runner, terminal, diagnostics
.venv/bin/python verify_medha.py

# Adversarial validator (Phases 3-6): LSP, debugger, git, build, hygiene
.venv/bin/python verify_medha_p3_p6.py

# DSA visualizer verification
.venv/bin/python verify_dsa_visualizer.py
```

**Validators use runtime-generated values** — hardcoded/mocked output cannot pass.

---

## Limitations (Honest)

- **No VS Code JavaScript extensions** — only Open VSX extensions that are pure data (themes, snippets, TextMate grammars). Node.js-based extensions (language servers, debuggers, formatters) cannot run.
- **LSP requires external binaries** — `clangd` for C/C++, `pylsp` for Python. Install them separately; MEDHA will auto-detect if on PATH.
- **Debugpy for Python** — install via `pip install debugpy` (or `--break-system-packages`).
- **No bundled compilers/runtimes** — uses your system `gcc`, `g++`, `python3`, `cmake`, `git`.
- **Linux-first** — Wayland/X11 via Qt. Windows/macOS untested.
- **No web browser, no Monaco, no LibreOffice, no VLC, no game engine** — those were in the archived `legacy/` prototype.

---

## Logo

The logo mark (`medha/assets/logo-mark.svg`) is shown above. If you don't see it, the file may be at `video-editor/logo-mark.svg` in the parent workspace.

---

## License

MEDHĀ IDE is licensed under **GPL-3.0-or-later**. See [LICENSE](LICENSE) for the full license text.
Third-party components are listed in [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).