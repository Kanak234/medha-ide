"""
MEDHĀ IDE — entry point (`python -m medha`, MEDHA.exe, the snap launcher).

WHAT:  Picks the right Qt platform plugin on Linux, then opens the main window.
       Extra command-line modes (used by CI, the MSIX smoke test and lab admins):
         --version    print the version and exit
         --selftest   headless: find the toolchains, compile + run a tiny C program
                      with the real runner, print the result, exit 0/1
WHY:   v1 forced QT_QPA_PLATFORM even where it does not apply; on Windows and macOS
       Qt must choose its own native plugin. --selftest lets the Windows build be
       verified on GitHub's windows-latest machine without a screen.
FLOW:  main() → (selftest | version) or QApplication → MedhaMainWindow.show()
"""
import os
import sys


def _choose_linux_platform():
    # Respect an explicit choice; otherwise Wayland session → wayland, X11 → xcb.
    if os.environ.get("QT_QPA_PLATFORM"):
        return
    if os.environ.get("WAYLAND_DISPLAY"):
        os.environ["QT_QPA_PLATFORM"] = "wayland"
    elif os.environ.get("DISPLAY"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"


def selftest() -> int:
    """Compile and run a C program through the real ProcessRunner; print evidence."""
    import tempfile
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication
    from medha import __version__, toolchains
    from medha.runner import ProcessRunner

    app = QApplication.instance() or QApplication(sys.argv)
    print(f"MEDHA IDE {__version__} self-test")
    for name, tool in toolchains.report():
        print(f"  {name:9} {tool.source or '-':14} {tool.path or 'NOT FOUND'}  {tool.version}")
    folder = tempfile.mkdtemp(prefix="medha-selftest-")
    src = os.path.join(folder, "selftest.c")
    with open(src, "w") as f:
        f.write('#include <stdio.h>\nint main(void){int s=0;for(int i=1;i<=100;i++)s+=i;printf("SUM=%d\\n",s);return 0;}\n')
    runner = ProcessRunner()
    out, result = [], {}
    runner.output.connect(out.append)
    loop = QEventLoop()
    runner.finished.connect(lambda code, diags: (result.update(code=code), loop.quit()))
    QTimer.singleShot(120000, loop.quit)
    runner.run_file(src)
    loop.exec()
    text = "".join(out)
    print(text)
    ok = result.get("code") == 0 and "SUM=5050" in text
    print("SELFTEST", "PASS" if ok else "FAIL")
    del app
    return 0 if ok else 1


def main():
    if "--version" in sys.argv:
        from medha import __version__
        print(__version__)
        return 0
    if "--selftest" in sys.argv:
        return selftest()
    if sys.platform.startswith("linux"):
        _choose_linux_platform()

    from PySide6.QtWidgets import QApplication
    from medha.app import MedhaMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("MEDHĀ IDE")
    app.setDesktopFileName("io.github.Kanak234.Medha")
    app.setOrganizationName("MEDHA")
    window = MedhaMainWindow(workspace_path=os.getcwd())
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
