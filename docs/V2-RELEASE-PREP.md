# 2.0.0 release preparation — 2026-11-05

Prepared on `v2-release` from main `94824a6` (merged Track A, PR #7).
This is preparation only: no package upload, Store submission, tag, release,
Snap promotion or publishing workflow was performed.

## Prepared assets

- App/About, AppStream, Windows manifest/EXE version metadata and Linux package
  builders use 2.0.0 (MSIX: 2.0.0.0). Snap derives the app version via adopt-info.
- [Changelog](../CHANGELOG.md) includes B1/B2/B4/B6/B7/B8/B9 and the requested
  B3 “coming in this release” placeholder.
- [Partner Center copy](../store/listing.md) contains 633 characters between
  WHATS_NEW markers, including newlines; paste those bullets verbatim.
- [Seven screenshots](../store/screenshots-v2/README.md) are native 1920×1080,
  generated with `QT_QPA_PLATFORM=offscreen python tools/capture_v2.py --store`.
  Scene evidence accompanies the images. README uses the new UI and official
  [Microsoft Store](https://apps.microsoft.com/detail/9ndcdm1mmh5t) and
  [Snap](https://snapcraft.io/medha-ide) links.

## Offline validation

Linux source checkout, Python virtual environment, Qt offscreen platform,
isolated XDG settings/data directories and default network opt-out:

| Command | Result |
|---|---|
| `python -m pytest -q` | 110 passed, 1 skipped (explicit network opt-in) |
| `python -m pyflakes medha` | Passed, no diagnostics |
| `QT_QPA_PLATFORM=offscreen python -m pytest tests/test_ui_smoke.py -q` | 20 passed |
| `python -m pyflakes tools/capture_v2.py tools/store_scenes.py build_packages.py tests/test_release_metadata.py` | Passed, no diagnostics |
| `git diff --check` | Passed |

New release tests verify package-version agreement, About version, Store-copy
length and screenshot dimensions. Capture validation exercised real GDB, Python
DSA tracing and a compiled Turbo C graphics example; every screenshot was
visually inspected. These checks do not establish Windows package acceptance.

## Remaining release gates

- Resolve version ordering before submission: the base app and public Snap
  listing already reported 2.0.1. This branch follows the requested 2.0.0 target;
  compatibility with previously uploaded Windows versions is not established.
- Merge and validate B3 from `v2-bugs`, then replace its changelog placeholder.
  B5 remains separately tracked in the plan.
- Build the MSIX on Windows using the existing packaging script, and verify
  install, launch, uninstall and the plan's Windows/Ubuntu manual checklist.
  Build and validate the strict Snap, including its documented debugger limits.
- Verify screenshots against the Windows package before Store submission.
- Publishing requires a separate instruction. The existing Windows workflow
  can create a GitHub Release even when manually dispatched, so it was not run.

`medha/terminal.py`, `tests/conftest.py`, runner/project-manager/toolchain/debugger/
Turbo tests, licenses, privacy policy and signing/certificate files are unchanged.
