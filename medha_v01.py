#!/usr/bin/env python3
"""
MEDHĀ IDE v0.1 — Standalone Crash-Proof PySide6 Core Main Window
Features:
 1. Real Folder Explorer (QFileSystemModel + QTreeView)
 2. Real Code Editor tab with line numbers & file handling
 3. Real QProcess Terminal & Compiler Runner (gcc & python3 support without segfaults)
 4. Global exception hook & process cleanup to prevent silent exits
"""

import sys
import os
import shutil
import traceback
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTreeView, QFileSystemModel, QTextEdit, QPlainTextEdit,
    QLineEdit, QPushButton, QSplitter, QLabel, QStatusBar, QMessageBox,
    QFileDialog
)
from PySide6.QtGui import QFont, QTextCursor, QColor, QPainter, QTextFormat
from PySide6.QtCore import Qt, QProcess, Signal, QRect, QSize, QDir

# --- 1. Global Exception Hook to prevent Silent Crash ---
def global_exception_hook(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    sys.stderr.write(f"[MEDHĀ CRASH PREVENTED] Unhandled Exception:\n{err_msg}\n")
    # Show GUI dialog if QApplication instance exists
    app = QApplication.instance()
    if app and app.startingUp() is False:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("MEDHĀ IDE — Exception Caught")
        msg.setText("An unhandled exception occurred in the application.")
        msg.setDetailedText(err_msg)
        msg.exec()

sys.excepthook = global_exception_hook


# --- 2. Code Editor with Line Numbers ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class SimpleCodeEditor(QPlainTextEdit):
    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.line_number_area = LineNumberArea(self)

        font = QFont("Monospace", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                selection-background-color: #1f6feb;
                selection-color: #ffffff;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)

    def line_number_area_width(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#161b22"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#8b949e"))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1


# --- 3. Robust QProcess Terminal Widget ---
class CrashProofTerminalWidget(QWidget):
    def __init__(self, workspace_path=None, parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path or QDir.currentPath()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setFont(QFont("Monospace", 9))
        self.output_edit.setStyleSheet("""
            QTextEdit {
                background-color: #090d16;
                color: #58a6ff;
                border: 1px solid #21262d;
            }
        """)
        layout.addWidget(self.output_edit)

        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter terminal command (e.g. gcc main.c -o main && ./main)...")
        self.input_line.setFont(QFont("Monospace", 9))
        self.input_line.setStyleSheet("background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; padding: 4px;")
        self.input_line.returnPressed.connect(self.send_input)
        input_layout.addWidget(self.input_line)

        btn_run = QPushButton("Execute")
        btn_run.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 4px 10px;")
        btn_run.clicked.connect(self.send_input)
        input_layout.addWidget(btn_run)

        layout.addLayout(input_layout)

        # QProcess shell setup with explicit parent anchoring
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.workspace_path)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.on_finished)

        self.start_shell()

    def start_shell(self):
        if self.process.state() == QProcess.ProcessState.NotRunning:
            shell = os.environ.get("SHELL", "/bin/bash")
            self.process.start(shell, ["-i"])
            self.append_output(f"[MEDHĀ Shell Started: {shell}]\n", color="#3fb950")

    def read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.append_output(data)

    def read_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.append_output(data, color="#f85149")

    def append_output(self, text, color=None):
        cursor = self.output_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if color:
            fmt = cursor.charFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()

    def send_input(self):
        cmd = self.input_line.text().strip()
        if not cmd:
            return
        self.input_line.clear()
        self.execute_command(cmd)

    def execute_command(self, cmd_string):
        if self.process.state() != QProcess.ProcessState.Running:
            self.start_shell()
        self.append_output(f"$ {cmd_string}\n", color="#79c0ff")
        self.process.write((cmd_string + "\n").encode("utf-8"))

    def on_finished(self, exit_code, status):
        self.append_output(f"\n[Process Finished (Exit Code: {exit_code})]\n", color="#8b949e")

    def safe_terminate(self):
        if hasattr(self, 'process') and self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()

    def closeEvent(self, event):
        self.safe_terminate()
        super().closeEvent(event)


# --- 4. Main Window ---
class MedhaMainWindow(QMainWindow):
    def __init__(self, workspace_path=None):
        super().__init__()
        self.workspace_path = workspace_path or os.getcwd()
        self.setWindowTitle("MEDHĀ IDE — v0.1 Crash-Proof Core")
        self.resize(1200, 700)

        # Central Splitter Layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        # --- Left Panel: Real Folder Explorer ---
        explorer_widget = QWidget()
        exp_layout = QVBoxLayout(explorer_widget)
        exp_layout.setContentsMargins(2, 2, 2, 2)
        lbl_exp = QLabel(" PROJECT EXPLORER")
        lbl_exp.setStyleSheet("background-color: #161b22; color: #8b949e; font-weight: bold; padding: 4px;")
        exp_layout.addWidget(lbl_exp)

        self.model = QFileSystemModel()
        self.model.setRootPath(self.workspace_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.workspace_path))
        self.tree.hideColumn(1)  # Hide Size
        self.tree.hideColumn(2)  # Hide Type
        self.tree.hideColumn(3)  # Hide Date
        self.tree.header().setVisible(False)
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #21262d;
            }
            QTreeView::item:hover { background-color: #161b22; }
            QTreeView::item:selected { background-color: #1f6feb; color: white; }
        """)
        self.tree.doubleClicked.connect(self.on_file_double_clicked)
        exp_layout.addWidget(self.tree)
        main_splitter.addWidget(explorer_widget)

        # --- Right Panel: Editor + Terminal Splitter ---
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Editor Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: #0d1117; }
            QTabBar::tab { background-color: #161b22; color: #8b949e; padding: 6px 12px; }
            QTabBar::tab:selected { background-color: #0d1117; color: #58a6ff; border-top: 2px solid #1f6feb; }
        """)
        right_splitter.addWidget(self.tab_widget)

        # Bottom Panel: Terminal + Controls
        bottom_widget = QWidget()
        bot_layout = QVBoxLayout(bottom_widget)
        bot_layout.setContentsMargins(0, 0, 0, 0)

        # Control Bar for Quick Run (gcc / python3)
        ctrl_bar = QHBoxLayout()
        btn_run_c = QPushButton("⚡ Build & Run C (gcc)")
        btn_run_c.setStyleSheet("background-color: #1f6feb; color: white; font-weight: bold; padding: 4px 8px;")
        btn_run_c.clicked.connect(self.run_active_c_file)
        ctrl_bar.addWidget(btn_run_c)

        btn_run_py = QPushButton("▶ Run Python (python3)")
        btn_run_py.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 4px 8px;")
        btn_run_py.clicked.connect(self.run_active_python_file)
        ctrl_bar.addWidget(btn_run_py)
        ctrl_bar.addStretch()

        bot_layout.addLayout(ctrl_bar)

        self.terminal = CrashProofTerminalWidget(workspace_path=self.workspace_path, parent=self)
        bot_layout.addWidget(self.terminal)
        right_splitter.addWidget(bottom_widget)

        main_splitter.addWidget(right_splitter)

        # Set Splitter Sizes
        main_splitter.setSizes([260, 940])
        right_splitter.setSizes([450, 250])

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(f"MEDHĀ v0.1 Ready | Workspace: {self.workspace_path}")

        # Open initial sample main.c or untitled tab
        default_file = os.path.join(self.workspace_path, "main.c")
        if os.path.exists(default_file):
            self.open_file(default_file)
        else:
            self.create_untitled_tab("main.c", "// MEDHĀ IDE C Demo\n#include <stdio.h>\n\nint main() {\n    printf(\"Hello, MEDHĀ IDE!\\n\");\n    return 0;\n}\n")

    def create_untitled_tab(self, filename="untitled.c", content=""):
        editor = SimpleCodeEditor(file_path=None, parent=self)
        editor.setPlainText(content)
        idx = self.tab_widget.addTab(editor, filename)
        self.tab_widget.setCurrentIndex(idx)

    def open_file(self, file_path):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return

        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, SimpleCodeEditor) and editor.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            editor = SimpleCodeEditor(file_path=file_path, parent=self)
            editor.setPlainText(content)
            idx = self.tab_widget.addTab(editor, os.path.basename(file_path))
            self.tab_widget.setCurrentIndex(idx)
            self.statusBar().showMessage(f"Opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error Opening File", str(e))

    def on_file_double_clicked(self, index):
        path = self.model.filePath(index)
        if not self.model.isDir(index):
            self.open_file(path)

    def get_current_editor(self) -> SimpleCodeEditor:
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, SimpleCodeEditor):
            return widget
        return None

    def save_current_file(self):
        editor = self.get_current_editor()
        if not editor:
            return None
        if not editor.file_path:
            path, _ = QFileDialog.getSaveFileName(self, "Save File", self.workspace_path)
            if not path:
                return None
            editor.file_path = path
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(path))

        try:
            with open(editor.file_path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
            self.statusBar().showMessage(f"Saved: {editor.file_path}")
            return editor.file_path
        except Exception as e:
            QMessageBox.critical(self, "Error Saving File", str(e))
            return None

    def run_active_c_file(self):
        file_path = self.save_current_file()
        if not file_path:
            return
        dir_name = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        out_bin = os.path.join(dir_name, base_name)
        cmd = f'gcc -g "{file_path}" -o "{out_bin}" && "{out_bin}"'
        self.terminal.execute_command(cmd)

    def run_active_python_file(self):
        file_path = self.save_current_file()
        if not file_path:
            return
        cmd = f'python3 "{file_path}"'
        self.terminal.execute_command(cmd)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.create_untitled_tab()
            self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        if hasattr(self, 'terminal'):
            self.terminal.safe_terminate()
        super().closeEvent(event)


# --- 5. Application Launcher ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MedhaMainWindow()
    window.show()
    sys.exit(app.exec())
