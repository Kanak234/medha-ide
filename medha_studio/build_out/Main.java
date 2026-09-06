"""
================================================================================
MEDHĀ STUDIO — Unified Single-Window IDE & Real-Time DSA Canvas
Features:
  - Left View: Multi-Language Editor & Real-Time Asynchronous Terminal
  - Right View: Dynamic QGraphicsView / QGraphicsScene DSA Canvas
  - Live Event Bridge: Intercepts __DSA__:{"type":...} stdout payloads to update canvas
================================================================================
"""

import sys
import os
import json
import shutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QPlainTextEdit, QGraphicsView, QGraphicsScene, QLabel,
    QPushButton, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPolygonF
from PySide6.QtCore import Qt, QProcess, QPointF

# X11 / Wayland platform fallback
if not os.environ.get("QT_QPA_PLATFORM") and (os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY")):
    os.environ["QT_QPA_PLATFORM"] = "xcb"


# --- Dynamic DSA Graphical Canvas ---
class DynamicDSACanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#0d1117")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(" 🎨 REAL-TIME DSA GRAPHICAL CANVAS")
        header.setStyleSheet("background-color: #161b22; color: #a371f7; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("border: none;")
        layout.addWidget(self.view)

        # Default Message
        self.show_placeholder("Run a code file or select a demo to render live DSA graphs.")

    def show_placeholder(self, text):
        self.scene.clear()
        t = self.scene.addText(text, QFont("Sans-Serif", 10))
        t.setDefaultTextColor(QColor("#8b949e"))
        t.setPos(20, 40)

    def render_payload(self, data):
        """Processes __DSA__ JSON dictionary payload and renders visual data structures."""
        try:
            self.scene.clear()
            ds_type = data.get("type", "array").lower()
            name = data.get("name", "DS")

            if ds_type in ["linked_list", "doubly_linked_list"]:
                self._render_linked_list(name, data.get("nodes", []), is_double=(ds_type == "doubly_linked_list"))
            elif ds_type in ["binary_tree", "bst"]:
                self._render_tree(name, data.get("nodes", []), data.get("edges", []))
            elif ds_type in ["stack", "queue"]:
                self._render_stack_queue(name, ds_type, data.get("nodes", []))
            else:
                self._render_array(name, data.get("nodes", []))

            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        except Exception as e:
            self.show_placeholder(f"Render Error: {e}")

    def _render_array(self, name, nodes):
        title = self.scene.addText(f"📊 Array / Vector: {name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#58a6ff"))
        title.setPos(20, 20)

        x = 30
        y = 80
        for i, val in enumerate(nodes):
            idx_t = self.scene.addText(f"[{i}]", QFont("Monospace", 8))
            idx_t.setDefaultTextColor(QColor("#8b949e"))
            idx_t.setPos(x + 15, y - 25)

            self.scene.addRect(x, y, 60, 50, QPen(QColor("#30363d"), 2), QBrush(QColor("#161b22")))
            txt = self.scene.addText(str(val), QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#ffffff"))
            txt.setPos(x + 18, y + 12)
            x += 75

    def _render_linked_list(self, name, nodes, is_double=False):
        title_text = f"🔗 Doubly Linked List: {name}" if is_double else f"🔗 Singly Linked List: {name}"
        title = self.scene.addText(title_text, QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#3fb950"))
        title.setPos(20, 20)

        x = 40
        y = 90
        positions = []
        for val in nodes:
            self.scene.addRect(x, y, 90, 50, QPen(QColor("#238636"), 2), QBrush(QColor("#0d1117")))
            txt = self.scene.addText(str(val), QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#7ee787"))
            txt.setPos(x + 20, y + 12)
            self.scene.addLine(x + 60, y, x + 60, y + 50, QPen(QColor("#30363d"), 1.5))
            positions.append((x + 75, y + 25, x, y + 25))
            x += 140

        for i in range(len(positions) - 1):
            sx, sy, _, _ = positions[i]
            _, _, dx, dy = positions[i + 1]
            self.scene.addLine(sx, sy - 5, dx, dy - 5, QPen(QColor("#58a6ff"), 2))
            if is_double:
                self.scene.addLine(dx, dy + 10, sx, sy + 10, QPen(QColor("#d29922"), 1.5, Qt.DashLine))

    def _render_tree(self, name, nodes, edges):
        title = self.scene.addText(f"🌲 Binary Search Tree: {name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#a371f7"))
        title.setPos(20, 20)

        tree_pos = {}
        if nodes:
            tree_pos[str(nodes[0])] = (260, 70)
        if len(nodes) > 1: tree_pos[str(nodes[1])] = (160, 140)
        if len(nodes) > 2: tree_pos[str(nodes[2])] = (360, 140)
        if len(nodes) > 3: tree_pos[str(nodes[3])] = (110, 210)
        if len(nodes) > 4: tree_pos[str(nodes[4])] = (210, 210)

        for e in edges:
            u, v = str(e.get("from")), str(e.get("to"))
            if u in tree_pos and v in tree_pos:
                ux, uy = tree_pos[u]
                vx, vy = tree_pos[v]
                self.scene.addLine(ux + 20, uy + 20, vx + 20, vy + 20, QPen(QColor("#30363d"), 2))

        for val, (px, py) in tree_pos.items():
            color = QColor("#1f6feb") if val == str(nodes[0]) else QColor("#161b22")
            self.scene.addEllipse(px, py, 40, 40, QPen(QColor("#8957e5"), 2), QBrush(color))
            t = self.scene.addText(str(val), QFont("Monospace", 9, QFont.Bold))
            t.setDefaultTextColor(QColor("#ffffff"))
            t.setPos(px + 10, py + 8)

    def _render_stack_queue(self, name, kind, nodes):
        title = self.scene.addText(f"🥞 Stack (LIFO): {name}" if kind == "stack" else f"🚶 Queue (FIFO): {name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#e3b341"))
        title.setPos(20, 20)

        x = 50
        y = 100
        for i, val in enumerate(nodes):
            self.scene.addRect(x, y, 70, 40, QPen(QColor("#d29922"), 2), QBrush(QColor("#161b22")))
            txt = self.scene.addText(str(val), QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#f2cc60"))
            txt.setPos(x + 20, y + 8)
            x += 80


# --- Master Studio Main Window ---
class MedhaStudioWindow(QMainWindow):
    def __init__(self, demo_dir=""):
        super().__init__()
        self.setWindowTitle("MEDHĀ STUDIO — Unified Multi-Language IDE & Live DSA Canvas")
        self.resize(1400, 820)
        self.demo_dir = demo_dir or os.path.dirname(os.path.abspath(__file__))

        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # Left Section (Editor & Terminal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)

        # Toolbar
        bar = QHBoxLayout()
        btn_open = QPushButton("📂 Open File...")
        btn_open.clicked.connect(self.action_open_file)
        bar.addWidget(btn_open)

        self.combo_demo = QComboBox()
        self.combo_demo.addItems([
            "Select Pre-Built Demo...",
            "C: Doubly Linked List (demo_linked_list.c)",
            "Python: BST Tree (demo_bst_tree.py)",
            "Java: Stack & Queue (demo_stack_queue.java)"
        ])
        self.combo_demo.currentIndexChanged.connect(self.action_select_demo)
        bar.addWidget(self.combo_demo)

        btn_run = QPushButton("⚡ RUN CODE")
        btn_run.setStyleSheet("background-color: #1f6feb; color: white; font-weight: bold; padding: 6px 16px;")
        btn_run.clicked.connect(self.action_run_code)
        bar.addWidget(btn_run)

        left_layout.addLayout(bar)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setStyleSheet("background-color: #0d1117; color: #e6edf3; border: 1px solid #30363d;")
        left_layout.addWidget(self.editor, 2)

        term_hdr = QLabel(" 🖥️ NON-BLOCKING REAL-TIME TERMINAL OUTPUT")
        term_hdr.setStyleSheet("background-color: #161b22; color: #79c0ff; font-weight: bold; font-size: 11px; padding: 4px;")
        left_layout.addWidget(term_hdr)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Monospace", 9))
        self.terminal.setStyleSheet("background-color: #090d16; color: #7ee787; border: 1px solid #30363d;")
        left_layout.addWidget(self.terminal, 1)

        main_splitter.addWidget(left_widget)

        # Right Section (DSA Graphical Canvas)
        self.canvas = DynamicDSACanvas()
        main_splitter.addWidget(self.canvas)
        main_splitter.setSizes([780, 620])

        # Asynchronous Process Runner
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)

        self.current_file = ""
        self.active_bin = None

    def action_open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Code File", self.demo_dir, "All Files (*)")
        if path:
            self.load_file(path)

    def action_select_demo(self, index):
        demos = {
            1: os.path.join(self.demo_dir, "demos", "demo_linked_list.c"),
            2: os.path.join(self.demo_dir, "demos", "demo_bst_tree.py"),
            3: os.path.join(self.demo_dir, "demos", "demo_stack_queue.java")
        }
        if index in demos and os.path.exists(demos[index]):
            self.load_file(demos[index])

    def load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self.current_file = path
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", str(e))

    def action_run_code(self):
        content = self.editor.toPlainText()
        if not content.strip():
            return

        work_dir = os.path.join(self.demo_dir, "build_out")
        os.makedirs(work_dir, exist_ok=True)
        self.process.setWorkingDirectory(work_dir)
        self.terminal.clear()

        ext = ".c"
        if "public class" in content or "import java" in content:
            ext = ".java"
        elif "def " in content or "import " in content or "print(" in content:
            ext = ".py"

        if ext == ".c":
            src = os.path.join(work_dir, "temp.c")
            out_bin = os.path.join(work_dir, "temp_c")
            with open(src, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] gcc -g {src} -o {out_bin}\n")
            self.active_bin = out_bin
            self.process.start(shutil.which("gcc") or "gcc", ["-g", src, "-o", out_bin])

        elif ext == ".py":
            src = os.path.join(work_dir, "temp.py")
            with open(src, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] python3 -u {src}\n")
            self.active_bin = None
            self.process.start(shutil.which("python3") or "python3", ["-u", src])

        elif ext == ".java":
            src = os.path.join(work_dir, "Main.java")
            with open(src, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] javac {src}\n")
            self.active_bin = "java_run"
            self.process.start(shutil.which("javac") or "javac", [src])

    def on_stdout(self):
        raw = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.terminal.append(raw)

        # Code-to-Canvas Event Bridge: Intercept __DSA__: payloads
        for line in raw.splitlines():
            if "__DSA__:" in line:
                payload_str = line.split("__DSA__:", 1)[1].strip()
                try:
                    payload = json.loads(payload_str)
                    self.canvas.render_payload(payload)
                except Exception as e:
                    pass

    def on_stderr(self):
        raw = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.terminal.append(f"[ERR] {raw}")

    def on_finished(self, exit_code, status):
        if exit_code == 0 and getattr(self, "active_bin", None):
            bin_path = self.active_bin
            self.active_bin = None
            if bin_path == "java_run":
                self.terminal.append("[MEDHĀ] Running compiled Java class...\n")
                self.process.start(shutil.which("java") or "java", ["-cp", os.path.join(self.demo_dir, "build_out"), "Main"])
            elif os.path.exists(bin_path):
                self.terminal.append(f"[MEDHĀ] Running binary: {bin_path}\n")
                self.process.start(bin_path, [])
        else:
            self.terminal.append(f"\n[MEDHĀ Engine] Process finished with exit code {exit_code}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MedhaStudioWindow()
    window.show()
    sys.exit(app.exec())
