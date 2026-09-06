"""
MEDHĀ IDE — Universal Multi-Language DSA Runtime Tracer
Extracts live Data Structure state (Arrays, Linked Lists, Trees, Graphs)
from GDB (C/C++), sys.settrace (Python), and JDWP (Java).
"""

import sys
import re
import os
from PySide6.QtCore import QObject, Signal


class DSASnapshot:
    """Represents a unified data structure graph snapshot at a step."""
    def __init__(self, ds_type="array", name="var", nodes=None, edges=None):
        self.ds_type = ds_type  # "array" | "linked_list" | "doubly_linked_list" | "binary_tree" | "stack" | "queue"
        self.name = name
        self.nodes = nodes or []  # list of dicts: {"id": "1", "label": "42", "highlight": "active"|"normal"|"deleted"}
        self.edges = edges or []  # list of dicts: {"from": "1", "to": "2", "label": "next"}


class UniversalDSATracer(QObject):
    """Thread-safe non-blocking DSA Tracer emitting state snapshots on step."""

    snapshot_ready = Signal(DSASnapshot)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_language = "cpp"
        self.step_count = 0

    def parse_python_frame(self, frame):
        """Analyzes Python stack frame for Data Structures (lists, dicts, LinkedList/TreeNode classes)."""
        self.step_count += 1
        locals_dict = frame.f_locals

        for var_name, obj in locals_dict.items():
            if var_name.startswith("__") or callable(obj):
                continue

            # 1. Detect Dynamic Lists / Arrays
            if isinstance(obj, list):
                nodes = [{"id": str(i), "label": str(val), "highlight": "active" if i == len(obj)-1 else "normal"} for i, val in enumerate(obj)]
                snap = DSASnapshot(ds_type="array", name=var_name, nodes=nodes)
                self.snapshot_ready.emit(snap)
                return snap

            # 2. Detect Linked List or Binary Tree Node objects
            if hasattr(obj, '__dict__'):
                attrs = obj.__dict__
                # Binary Tree: left / right
                if 'left' in attrs or 'right' in attrs:
                    nodes, edges = self._traverse_tree(obj)
                    snap = DSASnapshot(ds_type="binary_tree", name=var_name, nodes=nodes, edges=edges)
                    self.snapshot_ready.emit(snap)
                    return snap
                # Linked List: next / prev
                elif 'next' in attrs:
                    ds_kind = "doubly_linked_list" if 'prev' in attrs else "linked_list"
                    nodes, edges = self._traverse_linked_list(obj, is_double=('prev' in attrs))
                    snap = DSASnapshot(ds_type=ds_kind, name=var_name, nodes=nodes, edges=edges)
                    self.snapshot_ready.emit(snap)
                    return snap

        return None

    def _traverse_linked_list(self, head, is_double=False):
        nodes = []
        edges = []
        curr = head
        idx = 0
        visited = set()

        while curr and id(curr) not in visited and idx < 50:
            visited.add(id(curr))
            val = getattr(curr, 'val', getattr(curr, 'data', str(idx)))
            node_id = str(id(curr))
            nodes.append({"id": node_id, "label": str(val), "highlight": "normal"})

            nxt = getattr(curr, 'next', None)
            if nxt:
                edges.append({"from": node_id, "to": str(id(nxt)), "label": "next"})
            curr = nxt
            idx += 1

        return nodes, edges

    def _traverse_tree(self, root):
        nodes = []
        edges = []
        visited = set()

        def dfs(node):
            if not node or id(node) in visited:
                return
            visited.add(id(node))
            val = getattr(node, 'val', getattr(node, 'data', 'Node'))
            nid = str(id(node))
            nodes.append({"id": nid, "label": str(val), "highlight": "normal"})

            left = getattr(node, 'left', None)
            if left:
                edges.append({"from": nid, "to": str(id(left)), "label": "L"})
                dfs(left)

            right = getattr(node, 'right', None)
            if right:
                edges.append({"from": nid, "to": str(id(right)), "label": "R"})
                dfs(right)

        dfs(root)
        return nodes, edges

    def parse_gdb_variables(self, variables_list):
        """Parses GDB variables output into a DSASnapshot for C/C++."""
        self.step_count += 1
        arr_elements = []

        for name, val in variables_list:
            # Check for GDB Array representation: {1, 2, 3, 4}
            if val.startswith('{') and val.endswith('}'):
                raw_items = [s.strip() for s in val.strip('{}').split(',') if s.strip()]
                nodes = [{"id": str(i), "label": v, "highlight": "normal"} for i, v in enumerate(raw_items)]
                snap = DSASnapshot(ds_type="array", name=name, nodes=nodes)
                self.snapshot_ready.emit(snap)
                return snap

        return None
