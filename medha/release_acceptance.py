"""Real Windows source-app acceptance with bundled compilers; never publishes.

This complements the frozen GUI/selftest in build_msix.ps1. It does not claim
MSIX installation or manual desktop acceptance. Evidence is saved in dist/.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

from medha.platform_info import app_root
ROOT = app_root()


def main():
    assert sys.platform == 'win32', 'Run on Windows to validate ConPTY'
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from medha import settings
    from medha.app import MedhaMainWindow

    output = Path(os.environ.get('MEDHA_ACCEPTANCE_DIR', str(Path.cwd() / 'dist' / 'acceptance')))
    output.mkdir(parents=True, exist_ok=True)
    report = {'scope': 'Frozen Windows GUI' if getattr(sys, 'frozen', False) else 'Windows source GUI', 'passed': [],
              'pending': ['MSIX install/uninstall', 'installed-package interactive acceptance',
                          'extension install/uninstall', 'manual Windows desktop review']}
    app = QApplication([])

    def wait(predicate, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            app.processEvents()
            if predicate():
                return
            QTest.qWait(30)
        raise AssertionError('Acceptance check timed out')

    # Temporary settings and source files avoid changing user work or Store assets.
    with tempfile.TemporaryDirectory(prefix='medha-acceptance-') as folder:
        project = Path(folder)
        settings.settings_path = lambda: str(project / 'settings.json')
        window = MedhaMainWindow(str(project))
        window.resize(1920, 1080)
        window.show()
        try:
            terminal = window.terminal
            assert type(terminal._pty).__name__ == '_WindowsConPtyProcess'
            wait(lambda: terminal._pty._shell_started)
            # Clearing before each command distinguishes output from old results.
            terminal.clear()
            terminal.execute_command('dir')
            wait(lambda: 'Directory of' in terminal.output_edit.toPlainText())
            report['passed'].append('ConPTY prompt and dir')
            terminal.clear()
            terminal.execute_command('ping -t 127.0.0.1')
            wait(lambda: 'TTL=' in terminal.output_edit.toPlainText())
            QTest.keyClick(terminal.input_line, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
            wait(lambda: 'Ping statistics' in terminal.output_edit.toPlainText())
            terminal.clear()
            terminal.execute_command('dir')
            wait(lambda: 'Directory of' in terminal.output_edit.toPlainText())
            report['passed'].append('ping Ctrl+C and shell survives')

            source = project / 'scanf.c'
            source.write_text('#include <stdio.h>\nint main(void){int n; if(scanf("%d",&n)!=1)return 2; printf("ANSWER=%d\\n",n*2); return 0;}\n')
            window.open_file_path(str(source))
            captured = []
            codes = []
            window.runner.output.connect(captured.append)
            window.runner.finished.connect(lambda code, diagnostics: codes.append(code))
            window.runner.run_file(str(source))
            wait(lambda: window.runner.stage == 'run')
            terminal.input_line.setText('21')
            terminal.send_input()
            wait(lambda: bool(codes))
            assert codes[-1] == 0 and 'ANSWER=42' in ''.join(captured)
            report['passed'].append('C build/run and scanf through terminal input')

            turbo = project / 'shapes.c'
            shutil.copyfile(ROOT / 'examples/turboc/02_lines_and_shapes.c', turbo)
            window.open_file_path(str(turbo))
            window.runner.run_file(str(turbo))
            wait(lambda: window.runner._decoder is not None and window.runner._decoder.frames > 0)
            window.dock_turbo.show()
            QTest.qWait(300)
            assert window.grab().save(str(output / 'turbo-windows.png'))
            window.runner.write_stdin('\n')
            wait(lambda: window.runner.stage == 'idle')
            assert codes[-1] == 0
            report['passed'].append('Turbo C graphics produced a decoded framebuffer')
            report['status'] = 'PASS'
        except Exception:
            import traceback
            report['status'] = 'FAIL'
            report['error'] = traceback.format_exc()
            raise
        finally:
            (output / 'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            window.close()
            app.processEvents()
    return 0


if __name__ == '__main__':
    sys.exit(main())
