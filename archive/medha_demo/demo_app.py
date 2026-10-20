"""
================================================================================
MEDHĀ IDE — Standalone Unified Interactive Demo Application
Self-contained single-file PySide6 application demonstrating:
  1. Multi-language Code Editor (C, C++, Python, Java) with syntax templates.
  2. Asynchronous QProcess compiler & runner.
  3. Interactive Dynamic DSA Graphical Canvas (Arrays, Linked Lists, BST, Graphs).
================================================================================
"""

import sys
import os
import shutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QPlainTextEdit, QGraphicsView, QGraphicsScene, QLabel,
    QPushButton, QComboBox, QTabWidget, QMessageBox
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPolygonF
from PySide6.QtCore import Qt, QProcess, QPointF, QTimer

# Defensive X11 / Wayland platform fallback
if not os.environ.get("QT_QPA_PLATFORM") and (os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY")):
    os.environ["QT_QPA_PLATFORM"] = "xcb"

# --- Pre-loaded DSA Code Templates ---
DEMO_TEMPLATES = {
    "C (Linked List)": """// MEDHĀ IDE — C Doubly Linked List Demo
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
    struct Node* prev;
} Node;

Node* create_node(int data) {
    Node* n = (Node*)malloc(sizeof(Node));
    n->data = data;
    n->next = NULL;
    n->prev = NULL;
    return n;
}

int main() {
    Node* head = create_node(10);
    head->next = create_node(20);
    head->next->prev = head;
    head->next->next = create_node(30);
    head->next->next->prev = head->next;

    printf("MEDHĀ IDE C Demo: Doubly Linked List [10 <-> 20 <-> 30]\\n");
    return 0;
}
""",
    "C++ (BST Tree)": """// MEDHĀ IDE — C++ Binary Search Tree Demo
#include <iostream>

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}
};

int main() {
    TreeNode* root = new TreeNode(50);
    root->left = new TreeNode(30);
    root->right = new TreeNode(70);
    root->left->left = new TreeNode(20);
    root->left->right = new TreeNode(40);

    std::cout << "MEDHĀ IDE C++ Demo: BST Created with Root (50)\\n";
    return 0;
}
""",
    "Python (Graph)": """# MEDHĀ IDE — Python Graph Adjacency List Demo
class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v):
        self.adj.setdefault(u, []).append(v)
        self.adj.setdefault(v, []).append(u)

g = Graph()
g.add_edge("A", "B")
g.add_edge("B", "C")
g.add_edge("C", "D")
g.add_edge("A", "D")

print("MEDHĀ IDE Python Demo: Graph connected nodes:", g.adj)
""",
    "Java (Array Vector)": """// MEDHĀ IDE — Java Dynamic Array Demo
public class Main {
    public static void main(String[] args) {
        int[] arr = {10, 20, 30, 40, 50};
        System.out.print("MEDHĀ IDE Java Demo Array Elements: ");
        for (int x : arr) {
            System.out.print(x + " ");
        }
        System.out.println();
    }
}
"""
}


# --- Interactive DSA Graphics Canvas ---
class DSAGraphicsCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#0d1117")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Canvas Header
        header = QLabel(" 🎨 INTERACTIVE DYNAMIC DSA GRAPHICAL CANVAS")
        header.setStyleSheet("background-color: #161b22; color: #a371f7; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        # QGraphicsView Canvas
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("border: none;")
        layout.addWidget(self.view)

        # 1-Click Interactive Mode Buttons Bar
        btn_bar = QHBoxLayout()
        btn_bar.setContentsMargins(4, 4, 4, 4)

        btn_arr = QPushButton("📊 Array")
        btn_arr.setStyleSheet("background-color: #1f6feb; color: white; font-weight: bold;")
        btn_arr.clicked.connect(self.draw_array_demo)
        btn_bar.addWidget(btn_arr)

        btn_list = QPushButton("🔗 Linked List")
        btn_list.setStyleSheet("background-color: #238636; color: white; font-weight: bold;")
        btn_list.clicked.connect(self.draw_linked_list_demo)
        btn_bar.addWidget(btn_list)

        btn_tree = QPushButton("🌲 BST Tree")
        btn_tree.setStyleSheet("background-color: #8957e5; color: white; font-weight: bold;")
        btn_tree.clicked.connect(self.draw_bst_tree_demo)
        btn_bar.addWidget(btn_tree)

        btn_graph = QPushButton("🕸️ Graph Network")
        btn_graph.setStyleSheet("background-color: #da3633; color: white; font-weight: bold;")
        btn_graph.clicked.connect(self.draw_graph_demo)
        btn_bar.addWidget(btn_graph)

        layout.addLayout(btn_bar)

        # Initial Render
        self.draw_linked_list_demo()

    def draw_array_demo(self):
        self.scene.clear()
        title = self.scene.addText("📊 Dynamic Array / Vector [Indices & Cells]", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#58a6ff"))
        title.setPos(20, 20)

        elements = [10, 25, 42, 99, 120]
        x = 30
        y = 90
        for i, val in enumerate(elements):
            # Index label
            idx_t = self.scene.addText(f"[{i}]", QFont("Monospace", 8))
            idx_t.setDefaultTextColor(QColor("#8b949e"))
            idx_t.setPos(x + 15, y - 25)

            # Cell box
            hl_color = QColor("#1f6feb") if i == 2 else QColor("#161b22")
            border = QColor("#58a6ff") if i == 2 else QColor("#30363d")
            self.scene.addRect(x, y, 60, 50, QPen(border, 2), QBrush(hl_color))

            val_t = self.scene.addText(str(val), QFont("Monospace", 10, QFont.Bold))
            val_t.setDefaultTextColor(QColor("#ffffff"))
            val_t.setPos(x + 18, y + 12)
            x += 75

    def draw_linked_list_demo(self):
        self.scene.clear()
        title = self.scene.addText("🔗 Doubly Linked List [Nodes & Bi-directional Arrows]", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#3fb950"))
        title.setPos(20, 20)

        nodes = ["10", "20", "30"]
        x = 40
        y = 90
        positions = []

        for val in nodes:
            self.scene.addRect(x, y, 90, 50, QPen(QColor("#238636"), 2), QBrush(QColor("#0d1117")))
            txt = self.scene.addText(val, QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#7ee787"))
            txt.setPos(x + 20, y + 12)
            self.scene.addLine(x + 60, y, x + 60, y + 50, QPen(QColor("#30363d"), 1.5))
            positions.append((x + 75, y + 25, x, y + 25))
            x += 140

        # Draw Next & Prev Arrows
        for i in range(len(positions) - 1):
            sx, sy, _, _ = positions[i]
            _, _, dx, dy = positions[i + 1]
            self.scene.addLine(sx, sy - 5, dx, dy - 5, QPen(QColor("#58a6ff"), 2))
            self.scene.addLine(dx, dy + 10, sx, sy + 10, QPen(QColor("#d29922"), 1.5, Qt.DashLine))

    def draw_bst_tree_demo(self):
        self.scene.clear()
        title = self.scene.addText("🌲 Binary Search Tree (BST) [Hierarchical Coordinates]", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#a371f7"))
        title.setPos(20, 20)

        tree_nodes = {
            "50": (260, 70),
            "30": (160, 140),
            "70": (360, 140),
            "20": (110, 210),
            "40": (210, 210)
        }
        edges = [("50", "30"), ("50", "70"), ("30", "20"), ("30", "40")]

        for src, dst in edges:
            sx, sy = tree_nodes[src]
            dx, dy = tree_nodes[dst]
            self.scene.addLine(sx + 20, sy + 20, dx + 20, dy + 20, QPen(QColor("#30363d"), 2))

        for val, (px, py) in tree_nodes.items():
            color = QColor("#1f6feb") if val == "50" else QColor("#161b22")
            self.scene.addEllipse(px, py, 40, 40, QPen(QColor("#8957e5"), 2), QBrush(color))
            t = self.scene.addText(val, QFont("Monospace", 9, QFont.Bold))
            t.setDefaultTextColor(QColor("#ffffff"))
            t.setPos(px + 10, py + 8)

    def draw_graph_demo(self):
        self.scene.clear()
        title = self.scene.addText("🕸️ Graph Network [Connected Nodes & Edges]", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#f85149"))
        title.setPos(20, 20)

        graph_nodes = {
            "A": (120, 90),
            "B": (280, 90),
            "C": (360, 190),
            "D": (200, 220)
        }
        edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("B", "D")]

        for u, v in edges:
            ux, uy = graph_nodes[u]
            vx, vy = graph_nodes[v]
            self.scene.addLine(ux + 20, uy + 20, vx + 20, vy + 20, QPen(QColor("#f85149"), 2))

        for name, (gx, gy) in graph_nodes.items():
            self.scene.addEllipse(gx, gy, 40, 40, QPen(QColor("#f85149"), 2), QBrush(QColor("#21262d")))
            t = self.scene.addText(name, QFont("Monospace", 10, QFont.Bold))
            t.setDefaultTextColor(QColor("#ffffff"))
            t.setPos(gx + 13, gy + 8)


# --- Master Demo Window ---
class MedhaDemoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MEDHĀ IDE — Native PySide6 Unified Interactive Demo")
        self.resize(1350, 800)

        # Central Splitter (Left: Editor & Terminal | Right: Visualizer)
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # Left Section Widget
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)

        # Language Selector Toolbar
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Select Template:"))
        self.combo_tpl = QComboBox()
        self.combo_tpl.addItems(list(DEMO_TEMPLATES.keys()))
        self.combo_tpl.currentTextChanged.connect(self.load_template)
        top_bar.addWidget(self.combo_tpl)

        btn_run = QPushButton("⚡ RUN CODE")
        btn_run.setStyleSheet("background-color: #1f6feb; color: white; font-weight: bold; padding: 6px 16px;")
        btn_run.clicked.connect(self.run_active_code)
        top_bar.addWidget(btn_run)
        left_layout.addLayout(top_bar)

        # Code Editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setStyleSheet("background-color: #0d1117; color: #e6edf3; border: 1px solid #30363d;")
        left_layout.addWidget(self.editor, 2)

        # Terminal Output View
        term_header = QLabel(" 🖥️ NON-BLOCKING REAL-TIME TERMINAL OUTPUT")
        term_header.setStyleSheet("background-color: #161b22; color: #79c0ff; font-weight: bold; font-size: 11px; padding: 4px;")
        left_layout.addWidget(term_header)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Monospace", 9))
        self.terminal.setStyleSheet("background-color: #090d16; color: #7ee787; border: 1px solid #30363d;")
        left_layout.addWidget(self.terminal, 1)

        main_splitter.addWidget(left_widget)

        # Right Section (DSA Visualizer Canvas)
        self.canvas = DSAGraphicsCanvas()
        main_splitter.addWidget(self.canvas)
        main_splitter.setSizes([750, 600])

        # QProcess Compiler & Execution Runner
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)

        # Load initial C template
        self.load_template("C (Linked List)")

    def load_template(self, tpl_key):
        if tpl_key in DEMO_TEMPLATES:
            self.editor.setPlainText(DEMO_TEMPLATES[tpl_key])
            if "C (Linked" in tpl_key:
                self.canvas.draw_linked_list_demo()
            elif "BST" in tpl_key:
                self.canvas.draw_bst_tree_demo()
            elif "Graph" in tpl_key:
                self.canvas.draw_graph_demo()
            elif "Array" in tpl_key:
                self.canvas.draw_array_demo()

    def run_active_code(self):
        tpl_key = self.combo_tpl.currentText()
        content = self.editor.toPlainText()
        work_dir = os.path.expanduser("~/Desktop/ide/medha_demo")
        os.makedirs(work_dir, exist_ok=True)
        self.process.setWorkingDirectory(work_dir)
        self.terminal.clear()

        if "C (" in tpl_key:
            src_path = os.path.join(work_dir, "demo.c")
            bin_path = os.path.join(work_dir, "demo_c")
            with open(src_path, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] gcc -g {src_path} -o {bin_path}\n")
            self.active_bin = bin_path
            self.process.start(shutil.which("gcc") or "gcc", ["-g", src_path, "-o", bin_path])

        elif "C++ (" in tpl_key:
            src_path = os.path.join(work_dir, "demo.cpp")
            bin_path = os.path.join(work_dir, "demo_cpp")
            with open(src_path, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] g++ -g {src_path} -o {bin_path}\n")
            self.active_bin = bin_path
            self.process.start(shutil.which("g++") or "g++", ["-g", src_path, "-o", bin_path])

        elif "Python (" in tpl_key:
            src_path = os.path.join(work_dir, "demo.py")
            with open(src_path, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] python3 -u {src_path}\n")
            self.active_bin = None
            self.process.start(shutil.which("python3") or "python3", ["-u", src_path])

        elif "Java (" in tpl_key:
            src_path = os.path.join(work_dir, "Main.java")
            with open(src_path, "w") as f: f.write(content)
            self.terminal.append(f"[MEDHĀ] javac {src_path}\n")
            self.active_bin = "java_run"
            self.process.start(shutil.which("javac") or "javac", [src_path])

    def on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.terminal.append(data)

    def on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.terminal.append(f"[ERR] {data}")

    def on_finished(self, exit_code, status):
        if exit_code == 0 and getattr(self, "active_bin", None):
            bin_path = self.active_bin
            self.active_bin = None
            if bin_path == "java_run":
                self.terminal.append("[MEDHĀ] Running compiled Java class...\n")
                self.process.start(shutil.which("java") or "java", ["-cp", os.path.expanduser("~/Desktop/ide/medha_demo"), "Main"])
            elif os.path.exists(bin_path):
                self.terminal.append(f"[MEDHĀ] Running binary {bin_path}...\n")
                self.process.start(bin_path, [])
        else:
            self.terminal.append(f"\n[MEDHĀ Engine] Process finished with exit code {exit_code}\n")


# --- Main Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MedhaDemoMainWindow()
    window.show()
    sys.exit(app.exec())
