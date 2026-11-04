# Instructions for AI coding agents (ChatGPT/Codex, OpenCode/Nemotron, Claude)

Read `docs/MEDHA-v2-PLAN.md` first — it is the source of truth for the current work (bugs table, UI target, release rules).

## Ground rules
- Work on a branch: `v2-ui` (Track A, ChatGPT) or `v2-bugs` (Track B, Nemotron). Never commit straight to `main`; open a PR.
- Commit author must be **Kanak Prabhakar <kanakprabhakar72@gmail.com>**. No AI attribution lines (no "Co-Authored-By", no "Generated with …") in commits or PRs.
- Small commits, one bug or one UI step each, message starts with the bug id when there is one (e.g. `B2: escape & in dock titles`).
- Every change must keep these green before you push:
  `python -m pytest -q` (offline) · `python -m pyflakes medha` · offscreen smoke: `QT_QPA_PLATFORM=offscreen python -m pytest tests/test_ui_smoke.py -q`
- Do not remove features; move them. Do not add network calls at startup. Keep it working fully offline.
- Code style: heavy inline comments after each block — WHY it exists, WHAT it does, WHERE it flows next — so the owner can explain the code himself.
- When you find a new bug, add a row to the bugs table in `docs/MEDHA-v2-PLAN.md` (id, severity, bug, where, fix) in the same PR.
- Never touch: `LICENSE`, `THIRD_PARTY_*`, `store/privacy-policy.md`, signing/certificate files.
