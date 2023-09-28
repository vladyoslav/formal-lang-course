from project.rpq_tensor import rpq_tensor
from pyformlang.finite_automaton import DeterministicFiniteAutomaton


def test_regular_path_query():
    dfa = DeterministicFiniteAutomaton()
    dfa.add_transition(0, "b", 1)
    dfa.add_transition(1, "a", 2)
    dfa.add_transition(2, "n", 2)
    dfa.add_transition(2, "a", 1)
    dfa.add_transition(1, "n", 1)
    dfa.add_transition(1, "c", 3)

    graph = dfa.to_networkx()

    regex = "b(a+n)*a"

    result = rpq_tensor(graph, regex, [0], [2, 3])
    expected = {(0, 2)}

    assert result == expected
