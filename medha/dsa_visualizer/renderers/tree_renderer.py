"""
MEDHĀ IDE — Non-Linear Tree & Graph DSA Renderer
Calculates automatic hierarchical tree levels and branch line coordinates for BST, AVL, and Red-Black Trees.
"""

from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF


class TreeDSARenderer:
    """Hierarchical Tree Layout Renderer (Binary Search Tree, AVL, Heaps)."""

    @staticmethod
    def render_tree(scene: QGraphicsScene, snapshot):
        scene.clear()

        title = scene.addText(f"🌲 Binary Search Tree: {snapshot.name}", QFont("Sans-Serif", 11, QFont.Bold))
        title.setDefaultTextColor(QColor("#388bfd"))
        title.setPos(20, 20)

        if not snapshot.nodes:
            empty_txt = scene.addText("Tree is empty.", QFont("Sans-Serif", 10))
            empty_txt.setDefaultTextColor(QColor("#8b949e"))
            empty_txt.setPos(50, 80)
            return

        # Build adjacency graph & locate root
        children_set = set()
        adj = {}
        for edge in snapshot.edges:
            src, dst = edge["from"], edge["to"]
            adj.setdefault(src, []).append((dst, edge.get("label", "")))
            children_set.add(dst)

        root_id = None
        for n in snapshot.nodes:
            if n["id"] not in children_set:
                root_id = n["id"]
                break

        if not root_id and snapshot.nodes:
            root_id = snapshot.nodes[0]["id"]

        nodes_map = {n["id"]: n for n in snapshot.nodes}
        positions = {}

        # Hierarchical coordinate calculation
        def calculate_positions(node_id, x, y, dx):
            positions[node_id] = (x, y)
            children = adj.get(node_id, [])

            left_child = None
            right_child = None
            for cid, lbl in children:
                if lbl == "L": left_child = cid
                elif lbl == "R": right_child = cid
                elif not left_child: left_child = cid
                else: right_child = cid

            if left_child:
                calculate_positions(left_child, x - dx, y + 60, dx / 1.8)
            if right_child:
                calculate_positions(right_child, x + dx, y + 60, dx / 1.8)

        calculate_positions(root_id, 300, 80, 120)

        # 1. Draw Branch Lines
        for edge in snapshot.edges:
            src, dst = edge["from"], edge["to"]
            if src in positions and dst in positions:
                sx, sy = positions[src]
                dx, dy = positions[dst]
                scene.addLine(sx + 20, sy + 20, dx + 20, dy + 20, QPen(QColor("#30363d"), 2))

        # 2. Draw Circular Nodes
        for nid, (x, y) in positions.items():
            node_data = nodes_map.get(nid, {})
            label = str(node_data.get("label", ""))
            hl = node_data.get("highlight", "normal")

            bg_color = QColor("#1f6feb") if hl == "active" else QColor("#161b22")
            border_color = QColor("#58a6ff") if hl == "active" else QColor("#30363d")

            # Circle Item
            ellipse = scene.addEllipse(x, y, 40, 40, QPen(border_color, 2), QBrush(bg_color))

            # Label Text
            txt = scene.addText(label, QFont("Monospace", 9, QFont.Bold))
            txt.setDefaultTextColor(QColor("#ffffff"))
            txt.setPos(x + 10, y + 8)
