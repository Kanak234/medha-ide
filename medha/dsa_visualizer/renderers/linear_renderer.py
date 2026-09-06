"""
MEDHĀ IDE — Linear DSA Visual Renderer
Renders Arrays, Vectors, Linked Lists, Doubly Linked Lists, Stacks, and Queues using QGraphicsScene.
"""

from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsItemGroup
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPolygonF
from PySide6.QtCore import Qt, QPointF


class LinearDSARenderer:
    """Graphics layout engine for Arrays, Linked Lists, Stacks, and Queues."""

    @staticmethod
    def render_array(scene: QGraphicsScene, snapshot):
        scene.clear()
        x_offset = 30
        y_pos = 80

        title = scene.addText(f"📊 Array / Vector: {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#58a6ff"))
        title.setPos(20, 20)

        for i, node in enumerate(snapshot.nodes):
            val = node.get("label", "")
            hl = node.get("highlight", "normal")

            bg_color = QColor("#1f6feb") if hl == "active" else (QColor("#da3633") if hl == "deleted" else QColor("#161b22"))
            border_color = QColor("#58a6ff") if hl == "active" else QColor("#30363d")

            # Index label above box
            idx_txt = scene.addText(f"[{i}]", QFont("Monospace", 8))
            idx_txt.setDefaultTextColor(QColor("#8b949e"))
            idx_txt.setPos(x_offset + 15, y_pos - 25)

            # Element Box
            rect = scene.addRect(x_offset, y_pos, 60, 50, QPen(border_color, 2), QBrush(bg_color))

            # Value label inside box
            val_txt = scene.addText(str(val), QFont("Monospace", 10, QFont.Bold))
            val_txt.setDefaultTextColor(QColor("#ffffff"))
            val_txt.setPos(x_offset + 18, y_pos + 12)

            x_offset += 75

    @staticmethod
    def render_linked_list(scene: QGraphicsScene, snapshot, is_double=False):
        scene.clear()
        x_offset = 40
        y_pos = 90
        node_positions = {}

        kind_name = "Doubly Linked List" if is_double else "Singly Linked List"
        title = scene.addText(f"🔗 {kind_name}: {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#3fb950"))
        title.setPos(20, 20)

        for i, node in enumerate(snapshot.nodes):
            nid = node["id"]
            val = node.get("label", "")

            # Node Box (Data | Next)
            rect = scene.addRect(x_offset, y_pos, 90, 50, QPen(QColor("#238636"), 2), QBrush(QColor("#0d1117")))
            txt = scene.addText(f"{val}", QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#7ee787"))
            txt.setPos(x_offset + 25, y_pos + 12)

            # Node Pointer Divider Line
            scene.addLine(x_offset + 60, y_pos, x_offset + 60, y_pos + 50, QPen(QColor("#30363d"), 1.5))

            node_positions[nid] = (x_offset + 75, y_pos + 25, x_offset, y_pos + 25)
            x_offset += 140

        # Draw Directed Arrow Lines between Linked List Nodes
        for edge in snapshot.edges:
            src = edge["from"]
            dst = edge["to"]
            label = edge.get("label", "next")

            if src in node_positions and dst in node_positions:
                sx, sy, _, _ = node_positions[src]
                _, _, dx, dy = node_positions[dst]

                if label == "next":
                    line = scene.addLine(sx, sy, dx, dy, QPen(QColor("#58a6ff"), 2))
                    # Draw Arrow Head
                    arrow = scene.addPolygon(QPolygonF([QPointF(dx, dy), QPointF(dx - 8, dy - 5), QPointF(dx - 8, dy + 5)]))
                    arrow.setBrush(QBrush(QColor("#58a6ff")))
                    arrow.setPen(Qt.NoPen)
                elif label == "prev":
                    line = scene.addLine(dx, dy + 15, sx, sy + 15, QPen(QColor("#d29922"), 1.5, Qt.DashLine))

        # NULL Terminator
        null_txt = scene.addText("NULL", QFont("Monospace", 9, QFont.Bold))
        null_txt.setDefaultTextColor(QColor("#da3633"))
        null_txt.setPos(x_offset, y_pos + 15)

    @staticmethod
    def render_stack(scene: QGraphicsScene, snapshot):
        scene.clear()
        x_pos = 120
        y_offset = 240

        title = scene.addText(f"🥞 Stack (LIFO): {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#a371f7"))
        title.setPos(20, 20)

        # Draw Stack Container Frame
        scene.addLine(x_pos - 10, 60, x_pos - 10, 260, QPen(QColor("#8957e5"), 3))
        scene.addLine(x_pos + 110, 60, x_pos + 110, 260, QPen(QColor("#8957e5"), 3))
        scene.addLine(x_pos - 10, 260, x_pos + 110, 260, QPen(QColor("#8957e5"), 3))

        for i, node in enumerate(snapshot.nodes):
            val = node.get("label", "")
            rect = scene.addRect(x_pos, y_offset, 100, 35, QPen(QColor("#8957e5"), 1.5), QBrush(QColor("#161b22")))
            txt = scene.addText(str(val), QFont("Monospace", 10, QFont.Bold))
            txt.setDefaultTextColor(QColor("#d2a8ff"))
            txt.setPos(x_pos + 35, y_offset + 5)

            if i == len(snapshot.nodes) - 1:
                top_lbl = scene.addText("◄ TOP", QFont("Sans-Serif", 9, QFont.Bold))
                top_lbl.setDefaultTextColor(QColor("#f85149"))
                top_lbl.setPos(x_pos + 120, y_offset + 5)

            y_offset -= 40
