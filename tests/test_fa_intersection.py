import project.fa_intersection as fa_intersection
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)


def test_fa_bool_decompose():
    dfa = DeterministicFiniteAutomaton()

    dfa.add_transition(0, "a", 0)
    dfa.add_transition(0, "b", 1)
    dfa.add_transition(1, "c", 1)
    dfa.add_transition(1, "b", 0)

    matrices = fa_intersection.bool_decompose(dfa)

    exp = {
        "a": [[1, 0], [0, 0]],
        "b": [[0, 1], [1, 0]],
        "c": [[0, 0], [0, 1]],
    }

    for label, matrix in exp.items():
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                assert matrices[label][i, j] == bool(value)


def test_intersect_fa():
    first = DeterministicFiniteAutomaton()

    first.add_transition(0, "a", 0)
    first.add_transition(0, "b", 1)
    first.add_transition(1, "c", 1)
    first.add_transition(1, "b", 0)

    first.add_start_state(0)
    first.add_final_state(1)

    second = NondeterministicFiniteAutomaton()

    second.add_transition(0, "a", 0)
    second.add_transition(0, "a", 1)
    second.add_transition(1, "b", 1)
    second.add_transition(1, "c", 1)

    second.add_start_state(0)
    second.add_final_state(1)

    exp = NondeterministicFiniteAutomaton()

    exp.add_transition(0, "a", 0)
    exp.add_transition(0, "a", 1)
    exp.add_transition(1, "b", 3)
    exp.add_transition(3, "b", 1)
    exp.add_transition(3, "c", 3)

    exp.add_start_state(0)
    exp.add_final_state(3)

    assert exp.is_equivalent_to(fa_intersection.intersect(first, second))
