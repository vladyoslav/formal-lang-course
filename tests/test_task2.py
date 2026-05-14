import networkx as nx
import pytest
from networkx.drawing.nx_pydot import read_dot
from project.task1 import get_graph_by_name, make_labeled_two_cycles_graph
from project.task2 import graph_to_nfa
from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    State,
)


@pytest.fixture
def test_graph() -> nx.MultiDiGraph:
    return read_dot("./tests/graphs/task2/input.dot")


def correct_nfa_from_graph(graph: nx.MultiDiGraph):
    exp = NondeterministicFiniteAutomaton()
    for first, second, label in graph.edges(data="label"):
        exp.add_transition(first, label, second)

    return exp


def test_graph_to_nfa(test_graph: nx.MultiDiGraph):
    exp = correct_nfa_from_graph(test_graph)
    exp.add_start_state(State(0))
    exp.add_final_state(State(1))

    nfa = graph_to_nfa(test_graph, {0}, {1})

    assert nfa.is_equivalent_to(exp)


def test_nfa_from_graph_invalid_starts(test_graph: nx.MultiDiGraph):
    with pytest.raises(Exception) as ex:
        graph_to_nfa(test_graph, {1236}, {1})
    assert "Wrong start" in str(ex.value)


def test_nfa_from_graph_invalid_finals(test_graph: nx.MultiDiGraph):
    with pytest.raises(Exception) as ex:
        graph_to_nfa(test_graph, {0}, {1236})
    assert "Wrong final" in str(ex.value)


def test_nfa_from_graph_name():
    graph = get_graph_by_name("skos")

    exp = correct_nfa_from_graph(graph)
    exp.add_start_state(State(0))
    exp.add_final_state(State(1))

    nfa = graph_to_nfa(graph, {0}, {1})

    assert nfa.is_equivalent_to(exp)


def test_nfa_from_two_cycles_graph(tmp_path):
    path = tmp_path / "two_cycles.dot"

    make_labeled_two_cycles_graph(3, 5, ("a", "b"), str(path))

    graph = read_dot(str(path))
    exp = correct_nfa_from_graph(graph)
    exp.add_start_state(State(0))
    exp.add_final_state(State(1))
    nfa = graph_to_nfa(graph, {0}, {1})

    assert nfa.is_equivalent_to(exp)
