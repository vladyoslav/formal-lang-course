from collections import defaultdict

from pyformlang.finite_automaton import FiniteAutomaton, NondeterministicFiniteAutomaton
from scipy import sparse


def bool_decompose(fa: FiniteAutomaton) -> defaultdict[str, sparse.spmatrix]:
    graph = fa.to_networkx()
    states_number = len(fa.states)

    matrices = defaultdict(
        lambda: sparse.csr_matrix((states_number, states_number), dtype=bool)
    )
    states = list(fa.states)

    for start, end, label in graph.edges(data="label"):
        if not label:
            continue

        i = states.index(start)
        j = states.index(end)

        matrices[label][i, j] = True

    return matrices


def intersect(first_fa: FiniteAutomaton, second_fa: FiniteAutomaton) -> FiniteAutomaton:
    first_matrices = bool_decompose(first_fa)
    second_matrices = bool_decompose(second_fa)

    labels = first_matrices.keys() & second_matrices.keys()
    matrices = {
        label: sparse.kron(first_matrices[label], second_matrices[label])
        for label in labels
    }

    fa = NondeterministicFiniteAutomaton()

    first_states = list(first_fa.states)
    second_states = list(second_fa.states)

    def to_indices(search_in: list, states: list) -> list:
        return [search_in.index(s) for s in states]

    first_starts = to_indices(first_states, first_fa.start_states)
    second_starts = to_indices(second_states, second_fa.start_states)

    for i in first_starts:
        for j in second_starts:
            fa.add_start_state(i * len(second_states) + j)

    first_finals = to_indices(first_states, first_fa.final_states)
    second_finals = to_indices(second_states, second_fa.final_states)

    for i in first_finals:
        for j in second_finals:
            fa.add_final_state(i * len(second_states) + j)

    for label, matrix in matrices.items():
        cx = matrix.tocoo()
        for i, j, v in zip(cx.row, cx.col, cx.data):
            if not v:
                continue
            fa.add_transition(i, label, j)

    return fa
