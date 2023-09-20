import networkx as nx
import project.automata_lib as al
import project.graph_lib as gl
import pytest
from networkx.drawing.nx_pydot import read_dot
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)


def test_min_dfa_from_regex():
    mdfa = al.min_dfa_from_regex("a+b+$+(a+b+$)(a+b)*(a+b+$)")

    assert mdfa.is_deterministic()

    exp = DeterministicFiniteAutomaton()

    exp.add_transition(0, "a", 0)
    exp.add_transition(0, "b", 0)
    exp.add_transition(1, "a", 2)
    exp.add_transition(1, "b", 2)
    exp.add_transition(2, "a", 0)
    exp.add_transition(2, "b", 2)

    exp.add_start_state(0)
    exp.add_final_state(1)
    exp.add_final_state(0)

    assert exp.is_equivalent_to(mdfa)

    mmdfa = mdfa.minimize()

    assert mdfa.states == mmdfa.states
    assert mdfa.start_states == mmdfa.start_states
    assert mdfa.final_states == mmdfa.final_states


def load_test_graph(path: str = "./tests/graphs/input_task2.dot"):
    graph = read_dot(path)
    graph.remove_node("\\n")  # removing \n node

    return graph


def correct_nfa_from_graph(graph: nx.MultiDiGraph):
    exp = NondeterministicFiniteAutomaton()
    for first, second, label in graph.edges(data="label"):
        exp.add_transition(first, label, second)

    return exp


def test_nfa_from_graph():
    graph = load_test_graph()

    exp = correct_nfa_from_graph(graph)
    exp.add_start_state(0)
    exp.add_final_state(1)

    nfa = al.nfa_from_graph(graph, [0], [1])

    assert nfa.is_equivalent_to(exp)

    exp.add_start_state(1)
    exp.add_final_state(0)

    nfa2 = al.nfa_from_graph(graph)

    assert nfa2.is_equivalent_to(exp)


def test_nfa_from_graph_invalid_starts():
    graph = load_test_graph()

    with pytest.raises(Exception) as ex:
        al.nfa_from_graph(graph, [1236], [1])
    assert "Wrong start" in str(ex.value)


def test_nfa_from_graph_invalid_finals():
    graph = load_test_graph()

    with pytest.raises(Exception) as ex:
        al.nfa_from_graph(graph, [0], ["test"])
    assert "Wrong final" in str(ex.value)


def test_nfa_from_graph_name():
    graph = gl.get_graph_by_name("skos")
    exp = correct_nfa_from_graph(graph)
    nfa = al.nfa_from_graph(graph, [], [])

    assert nfa.is_equivalent_to(exp)


def test_nfa_from_two_cycles_graph():
    path = "./tests/graphs/task2.dot"

    gl.make_labeled_two_cycles_graph(3, 5, ("a", "b"), path)

    graph = load_test_graph(path)
    exp = correct_nfa_from_graph(graph)
    nfa = al.nfa_from_graph(graph, [], [])

    assert nfa.is_equivalent_to(exp)
