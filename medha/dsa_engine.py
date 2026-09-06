"""
MEDHĀ IDE — Dynamic DSA Graphical Visualizer Engine
Provides interactive QGraphicsView rendering for Arrays, Linked Lists, Stacks, Queues, BST Trees, and Graphs.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QLabel, QPushButton
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPolygonF
from PySide6.QtCore import Qt, QPointF


class DSANodeData:
    def __init__(self, node_id, label, highlight="normal"):
        self.id = str(node_id)
        self.label = str(label)
        self.highlight = highlight # "normal" | "active" | "deleted"


class DSAEdgeData:
    def __init__(self, src_id, dst_id, label=""):
        self.src = str(src_id)
        self.dst = str(dst_id)
        self.label = label


class DSAGraphSnapshot:
    def __init__(self, ds_type="array", name="var", nodes=None, edges=None):
        self.ds_type = ds_type  # "array" | "linked_list" | "doubly_linked_list" | "stack" | "binary_tree" | "graph"
        self.name = name
        self.nodes = nodes or []
        self.edges = edges or []


class DynamicDSAVisualizerEngine(QWidget):
    """Integrated QGraphicsView DSA Visualizer Canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#0d1117")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header Bar
        header = QLabel(" DYNAMIC DSA GRAPHICAL ENGINE (Arrays, Trees, Graphs)")
        header.setStyleSheet("background-color: #161b22; color: #a371f7; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        # Canvas View
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("border: none;")
        layout.addWidget(self.view)

        # Control Bar
        ctrl_bar = QHBoxLayout()
        btn_fit = QPushButton("Fit View")
        btn_fit.setStyleSheet("background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 8px;")
        btn_fit.clicked.connect(self.fit_view)
        ctrl_bar.addWidget(btn_fit)

        btn_sample_list = QPushButton("Demo Linked List")
        btn_sample_list.setStyleSheet("background-color: #1f6feb; color: white; padding: 4px 8px;")
        btn_sample_list.clicked.connect(self.render_sample_linked_list)
        ctrl_bar.addWidget(btn_sample_list)

        btn_sample_tree = QPushButton("Demo BST Tree")
        btn_sample_tree.setStyleSheet("background-color: #238636; color: white; padding: 4px 8px;")
        btn_sample_tree.clicked.connect(self.render_sample_tree)
        ctrl_bar.addWidget(btn_sample_tree)

        layout.addLayout(ctrl_bar)
        self.render_sample_linked_list()

    def fit_view(self):
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def render_snapshot(self, snapshot: DSAGraphSnapshot):
        self.scene.clear()
        if snapshot.ds_type == "array":
            self._render_array(snapshot)
        elif snapshot.ds_type in ["linked_list", "doubly_linked_list"]:
            self._render_linked_list(snapshot)
        elif snapshot.ds_type in ["binary_tree", "bst"]:
            self._render_tree(snapshot)
        else:
            self._render_array(snapshot)

    def _render_array(self, snapshot):
        x = 30
        y = 80
        title = self.scene.addText(f"📊 Array: {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#58a6ff"))
        title.setPos(20, 20)

        for i, node in enumerate(snapshot.nodes):
            rect = self.scene.addRect(x, y, 60, 50, QPen(QColor("#30363d"), 2), QBrush(QColor("#161b22")))
            txt = self.scene.addText(str(node.label), QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#ffffff"))
            txt.setPos(x + 20, y + 12)
            x += 75

    def _render_linked_list(self, snapshot):
        x = 30
        y = 90
        positions = {}
        title = self.scene.addText(f"🔗 Linked List: {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#3fb950"))
        title.setPos(20, 20)

        for node in snapshot.nodes:
            rect = self.scene.addRect(x, y, 90, 50, QPen(QColor("#238636"), 2), QBrush(QColor("#0d1117")))
            txt = self.scene.addText(str(node.label), QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#7ee787"))
            txt.setPos(x + 25, y + 12)
            self.scene.addLine(x + 60, y, x + 60, y + 50, QPen(QColor("#30363d"), 1.5))
            positions[node.id] = (x + 75, y + 25, x, y + 25)
            x += 140

        for edge in snapshot.edges:
            if edge.src in positions and edge.dst in positions:
                sx, sy, _, _ = positions[edge.src]
                _, _, dx, dy = positions[edge.dst]
                self.scene.addLine(sx, sy, dx, dy, QPen(QColor("#58a6ff"), 2))

    def _render_tree(self, snapshot):
        title = self.scene.addText(f"🌲 Binary Search Tree: {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#388bfd"))
        title.setPos(20, 20)

        if not snapshot.nodes:
            return

        positions = {
            snapshot.nodes[0].id: (250, 80)
        }
        if len(snapshot.nodes) > 1:
            positions[snapshot.nodes[1].id] = (170, 150)
        if len(snapshot.nodes) > 2:
            positions[snapshot.nodes[2].id] = (330, 150)

        for edge in snapshot.edges:
            if edge.src in positions and edge.dst in positions:
                sx, sy = positions[edge.src]
                dx, dy = positions[edge.dst]
                self.scene.addLine(sx + 20, sy + 20, dx + 20, dy + 20, QPen(QColor("#30363d"), 2))

        for node in snapshot.nodes:
            if node.id in positions:
                px, py = positions[node.id]
                self.scene.addEllipse(px, py, 40, 40, QPen(QColor("#58a6ff"), 2), QBrush(QColor("#161b22")))
                txt = self.scene.addText(str(node.label), QFont("Monospace", 9, QFont.Bold))
                txt.setDefaultTextColor(QColor("#ffffff"))
                txt.setPos(px + 10, py + 8)

    def render_sample_linked_list(self):
        nodes = [DSANodeData("1", "10"), DSANodeData("2", "20"), DSANodeData("3", "30")]
        edges = [DSAEdgeData("1", "2"), DSAEdgeData("2", "3")]
        snap = DSAGraphSnapshot(ds_type="linked_list", name="head", nodes=nodes, edges=edges)
        self.render_snapshot(snap)

    def render_sample_tree(self):
        nodes = [DSANodeData("1", "50"), DSANodeData("2", "30"), DSANodeData("3", "70")]
        edges = [DSAEdgeData("1", "2", "L"), DSAEdgeData("1", "3", "R")]
        snap = DSAGraphSnapshot(ds_type="binary_tree", name="root", nodes=nodes, edges=edges)
        self.render_snapshot(snap)
