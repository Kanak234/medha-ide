"""Reproducible Qt screenshots: python tools/capture_v2.py --phase after."""
import argparse
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from medha.app import MedhaMainWindow
from medha import settings

parser = argparse.ArgumentParser()
parser.add_argument('--phase', default='after')
parser.add_argument('--welcome', action='store_true')
args = parser.parse_args()
app = QApplication([])
output = Path(__file__).resolve().parents[1] / 'docs/screenshots/v2'
output.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='medha-capture-') as directory:
    root = Path(directory)
    os.environ['XDG_DATA_HOME'] = str(root / 'data')
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(root))
    settings.settings_path = lambda: str(root / 'settings.json')
    project = root / 'hello-c'
    project.mkdir()
    source = project / 'hello.c'
    source.write_text('''// MEDHĀ · learn by building\n#include <stdio.h>\n\nint main(void) {\n    const char *name = "world";\n    int numbers[] = {8, 3, 5, 1, 9};\n\n    printf("Hello, %s!\\n", name);\n    for (int i = 0; i < 5; ++i) {\n        printf("numbers[%d] = %d\\n", i, numbers[i]);\n    }\n\n    return 0;\n}\n''')
    window = MedhaMainWindow(str(project))
    if not args.welcome:
        window.open_file_path(str(source))
    for theme in (['dark', 'light'] if hasattr(window, 'apply_theme') else ['dark']):
        if hasattr(window, 'apply_theme'):
            window.apply_theme(theme)
        for width, height in [(1366, 768), (1920, 1080)]:
            window.resize(width, height)
            window.show()
            QTest.qWait(200)
            assert window.size().width() == width and window.size().height() == height
            path = output / f'{args.phase}-{theme}-{width}x{height}.png'
            assert window.grab().save(str(path))
            print(path.name, 'editor:', window.tab_widget.width(), flush=True)
    window.close()
