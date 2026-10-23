"""Open the real GUI, process events, save evidence, then shut down cleanly."""
import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from medha.app import MedhaMainWindow


def run():
    app = QApplication(sys.argv)
    window = MedhaMainWindow(workspace_path=os.getcwd())
    window.show()
    result = Path(os.environ["MEDHA_SMOKE_RESULT"])

    def verify():
        try:
            assert window.isVisible(), "Main window is not visible"
            assert window.tab_widget.count() > 0, "Welcome editor did not open"
            assert Path(window.workspace_path, "main.c").is_file(), "Scratchpad missing"
            assert window.grab().save(str(result.with_suffix(".png"))), "Screenshot failed"
            result.write_text(json.dumps({"status": "PASS", "workspace": window.workspace_path,
                                          "title": window.windowTitle()}), encoding="utf-8")
            window.close()
            app.exit(0)
        except Exception:
            import traceback
            result.write_text(traceback.format_exc(), encoding="utf-8")
            app.exit(1)

    QTimer.singleShot(5000, verify)
    return app.exec()
