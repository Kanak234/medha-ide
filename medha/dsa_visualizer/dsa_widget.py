"""
MEDHĀ IDE — Universal Live DSA Visualizer Widget Panel
Provides interactive QGraphicsView canvas with Zoom, Pan, HUD time complexity overlay,
and dynamic layout rendering for Linear and Non-Linear Data Structures.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QLabel, QPushButton, QComboBox, QSlider
)
from PySide6.QtGui import QColor, QBrush, QFont, QPainter
from PySide6.QtCore import Qt, Signal
from medha.dsa_visualizer.tracers.dsa_tracer import DSASnapshot, UniversalDSATracer
from medha.dsa_visualizer.renderers.linear_renderer import LinearDSARenderer
from medha.dsa_visualizer.renderers.tree_renderer import TreeDSARenderer


class DSAVisualizerWidget(QWidget):
    """
    Main UI Dock Panel for Live DSA Graphical Debugging & Step Visualization.
    """

    def __init__(self, tracer: UniversalDSATracer = None, parent=None):
        super().__init__(parent)
        self.tracer = tracer or UniversalDSATracer(self)
        self.current_snapshot = None
        self.total_operations = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header Bar
        header_bar = QHBoxLayout()
        lbl_title = QLabel(" UNIVERSAL LIVE DSA VISUALIZER & DEBUGGER ENGINE")
        lbl_title.setStyleSheet("background-color: #161b22; color: #a371f7; font-weight: bold; font-size: 11px; padding: 6px;")
        header_bar.addWidget(lbl_title, 1)

        layout.addLayout(header_bar)

        # Graphics Canvas View & Scene
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#0d1117")))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("border: none;")
        layout.addWidget(self.view)

        # Control Bar & Time Complexity HUD Overlay
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setContentsMargins(6, 4, 6, 4)

        self.lbl_hud = QLabel("Ops: 0 | Estimated Complexity: O(1) | Step: 0")
        self.lbl_hud.setStyleSheet("color: #79c0ff; font-weight: bold; font-size: 11px;")
        ctrl_layout.addWidget(self.lbl_hud)

        ctrl_layout.addStretch()

        btn_zoom_in = QPushButton("🔍 +")
        btn_zoom_in.setFixedWidth(35)
        btn_zoom_in.clicked.connect(lambda: self.view.scale(1.2, 1.2))
        ctrl_layout.addWidget(btn_zoom_in)

        btn_zoom_out = QPushButton("🔍 -")
        btn_zoom_out.setFixedWidth(35)
        btn_zoom_out.clicked.connect(lambda: self.view.scale(0.8, 0.8))
        ctrl_layout.addWidget(btn_zoom_out)

        btn_reset_view = QPushButton("Fit View")
        btn_reset_view.clicked.connect(self.fit_canvas)
        ctrl_layout.addWidget(btn_reset_view)

        layout.addLayout(ctrl_layout)

        # Connect Tracer Signal
        self.tracer.snapshot_ready.connect(self.render_snapshot)

    def render_snapshot(self, snapshot: DSASnapshot):
        self.current_snapshot = snapshot
        self.total_operations += 1

        ds_type = snapshot.ds_type
        if ds_type == "array":
            LinearDSARenderer.render_array(self.scene, snapshot)
            n_val = len(snapshot.nodes)
            complexity = f"O(N) [N={n_val}]"
        elif ds_type in ["linked_list", "doubly_linked_list"]:
            is_double = (ds_type == "doubly_linked_list")
            LinearDSARenderer.render_linked_list(self.scene, snapshot, is_double=is_double)
            n_val = len(snapshot.nodes)
            complexity = f"O(N) [N={n_val}]"
        elif ds_type == "stack":
            LinearDSARenderer.render_stack(self.scene, snapshot)
            complexity = "O(1) Push/Pop"
        elif ds_type in ["binary_tree", "bst"]:
            TreeDSARenderer.render_tree(self.scene, snapshot)
            n_val = len(snapshot.nodes)
            complexity = f"O(log N) [Height ~ {n_val.bit_length()}]"
        else:
            LinearDSARenderer.render_array(self.scene, snapshot)
            complexity = "O(1)"

        self.lbl_hud.setText(f"Ops: {self.total_operations} | Time Complexity: {complexity} | Step: {self.tracer.step_count}")

    def fit_canvas(self):
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
