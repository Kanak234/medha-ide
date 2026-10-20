import sys
import os
from PySide6.QtWidgets import QApplication
from medha.app import MedhaMainWindow

def main():
    # Platform selection:
    # - On Wayland (WAYLAND_DISPLAY set), prefer native "wayland" plugin.
    # - On pure X11 (DISPLAY set, no WAYLAND_DISPLAY), use "xcb" plugin.
    # - If user already set QT_QPA_PLATFORM, respect it.
    # - xcb requires libxcb-cursor0 which may be missing; don't force it on Wayland.
    if not os.environ.get("QT_QPA_PLATFORM"):
        if os.environ.get("WAYLAND_DISPLAY"):
            # Wayland session: use native wayland plugin (works out of the box)
            os.environ["QT_QPA_PLATFORM"] = "wayland"
        elif os.environ.get("DISPLAY"):
            # Pure X11 session: use xcb plugin
            os.environ["QT_QPA_PLATFORM"] = "xcb"
        # If neither is set (headless), let Qt pick (may fail, but that's expected)

    app = QApplication(sys.argv)
    app.setApplicationName("MEDHĀ IDE")
    app.setDesktopFileName("medha-ide")
    app.setOrganizationName("MEDHĀ")

    workspace = os.getcwd()
    window = MedhaMainWindow(workspace_path=workspace)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
