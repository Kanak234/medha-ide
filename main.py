"""
================================================================================
MEDHĀ IDE — Unified Production Main Entry Point
Initializes Anti-Gravity Core, PySide6 Application, and MedhaMainWindow.
================================================================================
"""

import sys
import os

# Set platform fallback for Linux X11 / Wayland
if not os.environ.get("QT_QPA_PLATFORM") and (os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY")):
    os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtWidgets import QApplication
from medha.app import MedhaMainWindow


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    workspace_path = os.getcwd()
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        workspace_path = sys.argv[1]

    window = MedhaMainWindow(workspace_path=workspace_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
