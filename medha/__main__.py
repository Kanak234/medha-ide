import sys
import os

def health_check():
    import json
    import shutil
    import PySide6
    status = {
        "status": "ok",
        "app": "medha-ide",
        "version": "1.0.0",
        "python": sys.version.split()[0],
        "pyside6": PySide6.__version__,
        "toolchains": {
            "gcc": shutil.which("gcc") is not None,
            "g++": shutil.which("g++") is not None,
            "gdb": shutil.which("gdb") is not None,
            "git": shutil.which("git") is not None,
            "cmake": shutil.which("cmake") is not None,
            "make": shutil.which("make") is not None,
        }
    }
    print(json.dumps(status, indent=2))
    return 0

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("health", "--health"):
        sys.exit(health_check())

    # Native platform default with conditional fallback to xcb for Wayland/X11 window visibility
    if not os.environ.get("QT_QPA_PLATFORM") and (os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY")):
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    from PySide6.QtWidgets import QApplication
    from medha.app import MedhaMainWindow

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
