# MEDHĀ STUDIO — Python Binary Search Tree (BST) Demo
import json

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

print("[MEDHĀ Python Demo] Building Binary Search Tree (BST)...")

root = TreeNode(50)
root.left = TreeNode(30)
root.right = TreeNode(70)
root.left.left = TreeNode(20)
root.left.right = TreeNode(40)

def inorder(node):
    if not node:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)

print(f"BST In-Order Traversal: {inorder(root)}")

# Emit live __DSA__ JSON Payload for Real-Time Graphical Canvas
payload = {
    "type": "bst",
    "name": "root_node",
    "nodes": [50, 30, 70, 20, 40],
    "edges": [
        {"from": 50, "to": 30},
        {"from": 50, "to": 70},
        {"from": 30, "to": 20},
        {"from": 30, "to": 40}
    ]
}
print(f"__DSA__:{json.dumps(payload)}")
