# Changelog

## 2.0.0 — release preparation (unreleased)

### Added and improved

- VS Code-style workbench with activity bar, collapsible sidebar and bottom panel; layout sizes are remembered.
- Medhā Dark and Medhā Light themes, readable tab controls and a clickable editor minimap.
- Command centre and searchable command palette (Ctrl+Shift+P).
- Quick Open (Ctrl+P), workspace search and reorganized menus preserving existing commands.
- Welcome tab with New C file, Open folder, Recent files, Turbo C examples and Learn DSA visually.
- Real document, Git and compiler status; optional CPU/RAM display.

### Fixed

- **B1:** Right-side tools no longer squeeze the editor; code gets at least 60% width at the target resolutions.
- **B2:** Literal ampersands display correctly in tool titles and file tabs.
- **B4:** Removed the duplicate extension-contribution loader.
- **B6:** Real registry tests require an explicit network opt-in; offline tests remain enabled.
- **B7:** Removed unused bindings while preserving graphics calls and public exports; pyflakes is clean.
- **B8:** Child processes stop before widgets are destroyed, preventing late disassembly callbacks.
- **B9:** Unsaved documents have Save/Discard/Cancel protection, including cancelled Save As.

### Coming in this release

- **B3 — real terminal.** The terminal panel now runs your shell in a real pseudo-terminal (Linux/macOS: pty; Windows: ConPTY via pywinpty, QProcess fallback). The "no job control" error is gone; colours, interactive programs and Ctrl+C (interrupts the running program) work. Verified on Linux; Windows ConPTY to be checked on the Store build.

### Release gates

- This branch prepares assets only. Nothing has been published or submitted.
- Main and the public Snap listing reported 2.0.1 before this preparation. The requested 2.0.0 target needs version-order review against existing Store packages before submission.
- Windows package build/install/launch/uninstall, strict Snap runtime verification and the cross-platform manual checklist remain pending.
- B5 remains tracked separately in `docs/MEDHA-v2-PLAN.md`.
