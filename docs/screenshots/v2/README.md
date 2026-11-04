# Track A visual verification

Captured from the real PySide6 window on Linux with `QT_QPA_PLATFORM=offscreen`.
Images are native 1366×768 and 1920×1080 pixels, without rescaling.

| State | 1366×768 | 1920×1080 |
|---|---|---|
| Before (original dark theme) | [Before](before-dark-1366x768.png) | [Before](before-dark-1920x1080.png) |
| After, Medhā Dark | [Dark](after-dark-1366x768.png) | [Dark](after-dark-1920x1080.png) |
| After, Medhā Light | [Light](after-light-1366x768.png) | [Light](after-light-1920x1080.png) |
| Welcome, dark | [Welcome](after-welcome-dark-1366x768.png) | [Welcome](after-welcome-dark-1920x1080.png) |
| Welcome, light | [Welcome](after-welcome-light-1366x768.png) | [Welcome](after-welcome-light-1920x1080.png) |

The original application has no light-theme switch, so a genuine before-light
capture is unavailable. No synthetic before-light image is supplied.
`step-1` through `step-5` retain intermediate layout/navigation/theme/welcome/status evidence.

The editor tab region increased from **127 → 1044 px** at 1366×768 and
**301 → 1598 px** at 1920×1080. Automated assertions also check the actual text
viewport (excluding the gutter and minimap) remains at least 60% of window width
in both themes at both resolutions.

The red terminal job-control warning is existing **B3**, assigned to Track B.
It remains visible in these unedited screenshots; this PR does not implement a PTY.

Reproduce from the repository root in an environment with the dependencies installed:

```sh
QT_QPA_PLATFORM=offscreen python tools/capture_v2.py --phase after
QT_QPA_PLATFORM=offscreen python tools/capture_v2.py --phase after-welcome --welcome
```

The capture tool uses a temporary project and isolated settings, then shuts down
its processes. It does not change the user's workspace or preferences.
