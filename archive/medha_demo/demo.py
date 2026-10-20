# MEDHĀ IDE — Python Graph Adjacency List Demo
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
