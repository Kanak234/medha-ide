"""Store scenes rendered by the real application, using local sample programs.

Called only by capture_v2.py --store. Temporary settings/projects are supplied by
that script; no publishing API is called and no user workspace is modified.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from medha.command_palette import CommandPalette, collect_actions


def wait_until(predicate, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        QApplication.processEvents()
        if predicate():
            return
        QTest.qWait(30)
    raise RuntimeError('Timed out waiting for the sample program')


def capture_store(window, project, source, output):
    output.mkdir(parents=True, exist_ok=True)
    window.resize(1920, 1080)
    window.show()
    window.apply_theme('dark')
    window.bottom_tabs.hide()
    evidence = {'size': [1920, 1080], 'platform': sys.platform, 'scenes': []}

    def save(name, detail):
        QTest.qWait(200)
        assert window.width() == 1920 and window.height() == 1080
        assert window.grab().save(str(output / name))
        evidence['scenes'].append({'file': name, 'evidence': detail})
        print(name, flush=True)
        # The saved pixels come from window.grab(), including all visible tool widgets.

    save('01-welcome.png', 'Actual Welcome page; no document opened.')
    window.open_file_path(str(source))
    save('02-editor-minimap.png', 'Editable hello.c sample with syntax highlighting and minimap.')

    palette = CommandPalette(collect_actions(window.menuBar()), window)
    palette.setWindowFlags(Qt.WindowType.Widget)
    palette.setParent(window)
    palette.move((window.width() - palette.width()) // 2, 70)
    palette.show()
    palette.raise_()
    save('03-command-centre.png', 'Real CommandPalette embedded for offscreen capture; commands are not mocked.')
    palette.hide()
    palette.deleteLater()
    # Offscreen platforms cannot capture a separate native popup in window.grab().
    # Reparenting the actual palette preserves its contents and Qt rendering.

    visual_source = project / 'array_demo.py'
    visual_source.write_text('''# Inspect a live Python list with the DSA visualizer\nnumbers = [8, 3, 5, 1, 9]\ntotal = sum(numbers)\nprint("Sum:", total)\n''')
    window.open_file_path(str(visual_source))
    def trace(frame, event, arg):
        if frame.f_code.co_filename == str(visual_source) and event == 'line' and frame.f_lineno == 3:
            window.dsa_tracer.parse_python_frame(frame)
        return trace
    previous_trace = sys.gettrace()
    try:
        sys.settrace(trace)
        exec(compile(visual_source.read_text(), str(visual_source), 'exec'), {})
    finally:
        sys.settrace(previous_trace)
    assert window.dsa_widget.current_snapshot is not None
    window.workbench.sidebar_width = 650
    window.dock_dsa.show()
    QTest.qWait(100)
    window.dsa_widget.fit_canvas()
    save('04-dsa-visualizer.png', 'UniversalDSATracer parsed a real Python frame containing numbers=[8,3,5,1,9].')

    window.open_file_path(str(source))
    binary = project / 'hello-debug'
    subprocess.run(['gcc', '-g', '-O0', str(source), '-o', str(binary)], check=True, capture_output=True, timeout=30)
    window.gdb_engine.toggle_breakpoint(str(source), 8)
    window.real_gdb_panel.refresh_breakpoints()
    window.gdb_engine.start_debug(str(binary))
    window.gdb_engine.poll_stop_status()
    assert window.gdb_engine.session.stopped, 'GDB did not stop at the sample breakpoint'
    window.real_gdb_panel.tabs.setCurrentIndex(2)
    window.dock_gdb.show()
    window.workbench.debug_input.setText('numbers[0]')
    window.workbench.evaluate()
    assert window.gdb_engine.evaluate_expression('numbers[0]') == '8'
    window.bottom_tabs.show()
    index = next(i for i in range(window.bottom_tabs.count()) if window.bottom_tabs.tabText(i) == 'Debug Console')
    window.bottom_tabs.setCurrentIndex(index)
    window.workbench.restore_sizes()
    save('05-debugger.png', 'Real gcc -g build paused in GDB at hello.c:8; numbers[0] evaluates to 8.')
    window.gdb_engine.stop_debug()
    window.get_current_editor().clear_execution_line()

    turbo = project / 'shapes.c'
    shutil.copyfile(Path(__file__).resolve().parents[1] / 'examples/turboc/02_lines_and_shapes.c', turbo)
    window.open_file_path(str(turbo))
    window.workbench.activate(0)
    window.workbench.sidebar_width = 270
    window.workbench.panel_height = 540
    window.runner.run_file(str(turbo))
    wait_until(lambda: window.runner._decoder is not None and window.runner._decoder.frames > 0)
    window.dock_turbo.show()
    window.workbench.restore_sizes()
    save('06-turbo-c-screen.png', 'Bundled shapes.c compiled and ran through ProcessRunner; screen is the real PRABHA framebuffer.')
    window.runner.write_stdin('\n')
    wait_until(lambda: window.runner.stage == 'idle')

    window.open_file_path(str(source))
    window.bottom_tabs.hide()
    window.apply_theme('light')
    save('07-light-theme.png', 'Same source document with the built-in Medhā Light theme.')
    (output / 'capture-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
