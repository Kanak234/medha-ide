from medha.dsa_engine import DSANodeData, DSAEdgeData, DSAGraphSnapshot

def test_dsa_data_structures():
    node = DSANodeData(1, "42", "active")
    assert node.id == "1"
    assert node.label == "42"
    assert node.highlight == "active"

    edge = DSAEdgeData(1, 2, "points_to")
    assert edge.src == "1"
    assert edge.dst == "2"
    assert edge.label == "points_to"

    snapshot = DSAGraphSnapshot("binary_tree", "bst_root", [node], [edge])
    assert snapshot.ds_type == "binary_tree"
    assert snapshot.name == "bst_root"
    assert len(snapshot.nodes) == 1
    assert len(snapshot.edges) == 1
