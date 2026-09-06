"""
MEDHĀ IDE — Live Memory & Pointer Visualizer (QGraphicsView / QGraphicsScene)
Renders interactive graphical maps of:
 1. Stack Memory Frames & Local Variables
 2. Heap Memory Allocations (malloc / free)
 3. Pointer Arrows linking pointers to target memory addresses
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QLabel, QPushButton
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter
from PySide6.QtCore import Qt, QPointF


class MemoryVisualizerWidget(QWidget):
    """
    Graphical Memory & Pointer Inspector side-panel.
    Visually depicts Stack vs Heap memory layout during GDB debugging steps.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel(" LIVE MEMORY & POINTER INSPECTOR (STACK vs HEAP)")
        header.setStyleSheet("background-color: #161b22; color: #3fb950; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        # Graphics Scene & View
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#0d1117")))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setStyleSheet("border: none;")
        layout.addWidget(self.view)

        # Control Bar
        ctrl_bar = QHBoxLayout()
        btn_clear = QPushButton("Reset Layout")
        btn_clear.setStyleSheet("background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px;")
        btn_clear.clicked.connect(self.reset_visualization)
        ctrl_bar.addWidget(btn_clear)

        btn_sample = QPushButton("Render Demo Memory Map")
        btn_sample.setStyleSheet("background-color: #1f6feb; color: white; padding: 4px;")
        btn_sample.clicked.connect(self.render_sample_memory)
        ctrl_bar.addWidget(btn_sample)

        layout.addLayout(ctrl_bar)
        self.render_sample_memory()

    def reset_visualization(self):
        self.scene.clear()

    def update_memory_map(self, stack_vars, heap_allocations):
        """
        stack_vars: list of (var_name, var_val, address)
        heap_allocations: list of (ptr_name, address, size)
        """
        self.scene.clear()

        # 1. Draw Stack Region Box (Left)
        stack_title = self.scene.addText("🔷 STACK FRAME (Locals)", QFont("Sans-Serif", 10, QFont.Bold))
        stack_title.setDefaultTextColor(QColor("#58a6ff"))
        stack_title.setPos(20, 10)

        y_offset = 40
        stack_boxes = {}
        for name, val, addr in stack_vars:
            rect = self.scene.addRect(20, y_offset, 220, 40, QPen(QColor("#1f6feb"), 1.5), QBrush(QColor("#161b22")))
            txt = self.scene.addText(f"{name}: {val}\nAddr: {addr}", QFont("Monospace", 8))
            txt.setDefaultTextColor(QColor("#c9d1d9"))
            txt.setPos(25, y_offset + 2)
            stack_boxes[name] = (240, y_offset + 20)
            y_offset += 50

        # 2. Draw Heap Region Box (Right)
        heap_title = self.scene.addText("🟩 HEAP ALLOCATIONS (malloc)", QFont("Sans-Serif", 10, QFont.Bold))
        heap_title.setDefaultTextColor(QColor("#3fb950"))
        heap_title.setPos(320, 10)

        hy_offset = 40
        for ptr_name, heap_addr, size in heap_allocations:
            rect = self.scene.addRect(320, hy_offset, 220, 45, QPen(QColor("#238636"), 1.5), QBrush(QColor("#091d14")))
            txt = self.scene.addText(f"Heap Chunk @ {heap_addr}\nSize: {size} bytes (via {ptr_name})", QFont("Monospace", 8))
            txt.setDefaultTextColor(QColor("#7ee787"))
            txt.setPos(325, hy_offset + 2)

            # Draw Pointer Arrow connecting Stack Pointer to Heap Chunk
            if ptr_name in stack_boxes:
                sx, sy = stack_boxes[ptr_name]
                line = self.scene.addLine(sx, sy, 320, hy_offset + 22, QPen(QColor("#f2cc60"), 2, Qt.DashLine))
            hy_offset += 55

    def render_sample_memory(self):
        sample_stack = [
            ("int a", "42", "0x7fffffffe400"),
            ("int *ptr", "0x5555555592a0", "0x7fffffffe408"),
            ("char *buffer", "0x555555559300", "0x7fffffffe410")
        ]
        sample_heap = [
            ("int *ptr", "0x5555555592a0", "64"),
            ("char *buffer", "0x555555559300", "128")
        ]
        self.update_memory_map(sample_stack, sample_heap)
