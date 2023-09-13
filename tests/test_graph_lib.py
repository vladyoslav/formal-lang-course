import filecmp

import project.graph_lib as gl


def test_load_graph_from_name():
    graph = gl.get_graph_by_name("skos")
    assert graph.number_of_nodes() == 144
    assert graph.size() == 252


def test_get_graph_info():
    graph = gl.get_graph_by_name("skos")
    nodes, edges, labels = gl.get_graph_info(graph)

    assert nodes == graph.number_of_nodes()
    assert edges == graph.size()
    assert labels[0] == "subPropertyOf"
    assert len(labels) == 252


def test_make_labeled_two_cycles_graph():
    path = "./tests/graphs/task1.dot"
    expected = "./tests/graphs/expected_task1.dot"

    gl.make_labeled_two_cycles_graph(3, 5, ("a", "b"), path)

    assert filecmp.cmp(path, expected, shallow=False)
