# Archive

Old experiments kept for history. Not part of MEDHA. Do not use.

## Contents

- `legacy/` — React/Vite/Monaco web prototype (fake build with hardcoded outputs)
- `medha_demo/` — Demo binaries and scripts
- `medha_studio/` — Separate experimental app
- `offline_sdk_bundle/` — Documentation library (once padded with 656 MB filler)
- `main`, `main.c`, `main.s`, `main.py` — Build leftovers
- `run1.txt`, `run2.txt` — Build logs
- `package.json`, `package-lock.json`, `tsconfig.json` — Web tooling config (unused by MEDHA)
- `medha-ide.spec`, `medha_v01.py` — Old PyInstaller spec and prototype
- `ABOUT.md`, `ARCHITECTURE.md`, `MEDHA_100_FEATURES.md`, `MEDHA_101_FEATURES.md`, `MEDHA_CHECKPOINT_LOOP.md`, `PROJECT_HISTORY.md`, `RELEASE_NOTES.md`, `SYSTEM_REQUIREMENTS.md`, `TEST_REPORT.md`, `TROUBLESHOOTING.md` — Documentation describing the fake web build

## The Real MEDHA

The only real application is the `medha/` package (PySide6 native desktop IDE).
Run it with: `python -m medha`