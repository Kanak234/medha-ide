import sys
import os
from PySide6.QtWidgets import QApplication
from medha.app import MedhaMainWindow

def main():
    # Native platform default with conditional fallback to xcb for Wayland/X11 window visibility
    if not os.environ.get("QT_QPA_PLATFORM") and (os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY")):
        os.environ["QT_QPA_PLATFORM"] = "xcb"

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
