import filecmp

from project.task1 import (
    get_graph_by_name,
    get_graph_info,
    make_labeled_two_cycles_graph,
)


def test_load_graph_from_name():
    graph = get_graph_by_name("skos")
    assert graph.number_of_nodes() == 144
    assert graph.size() == 252


def test_get_graph_info():
    graph = get_graph_by_name("skos")
    nodes, edges, labels = get_graph_info(graph)

    assert nodes == graph.number_of_nodes()
    assert edges == graph.size()
    assert labels[0] == "type"
    assert len(labels) == 21


def test_make_labeled_two_cycles_graph():
    path = "./tests/graphs/task1/actual.dot"
    expected = "./tests/graphs/task1/expected.dot"

    make_labeled_two_cycles_graph(3, 5, ("a", "b"), path)

    assert filecmp.cmp(path, expected, shallow=False)
