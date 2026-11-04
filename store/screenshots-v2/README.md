# Store screenshots — 2.0.0 preparation

Seven native 1920×1080 PNG captures. No upload or publication has been performed.

| File | Scene |
|---|---|
| [01-welcome.png](01-welcome.png) | Welcome: New C file, Open folder, examples and DSA |
| [02-editor-minimap.png](02-editor-minimap.png) | Dark editor and document minimap |
| [03-command-centre.png](03-command-centre.png) | Real searchable command palette |
| [04-dsa-visualizer.png](04-dsa-visualizer.png) | Live Python list parsed by the DSA tracer |
| [05-debugger.png](05-debugger.png) | Real GDB breakpoint, locals and expression evaluation |
| [06-turbo-c-screen.png](06-turbo-c-screen.png) | Real compiled graphics.h sample and PRABHA framebuffer |
| [07-light-theme.png](07-light-theme.png) | Medhā Light editor |

Reproduce from the repository root with Python dependencies, gcc and gdb installed:

```sh
QT_QPA_PLATFORM=offscreen python tools/capture_v2.py --store
```

`capture-evidence.json` records how each scene was produced. The capture script
uses temporary files/preferences and executes only its own sample programs.
The command palette is the actual CommandPalette widget, reparented into the main
window so Qt's offscreen window capture includes it. No values or framebuffer
pixels are fabricated; UI state is selected through the existing widgets.

These are Linux source-build captures, not proof of Windows/MSIX acceptance.
The terminal panel is collapsed or another panel selected; B3 is still pending.
Before a Store submission, verify the corresponding packaged Windows UI and
complete the manual checklist. The strict Snap does not support GDB debugging.
