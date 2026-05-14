from typing import Iterable

import networkx as nx
import numpy as np
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol
from scipy.sparse import csr_matrix, eye, kron

from project.task2 import graph_to_nfa, regex_to_dfa


class AdjacencyMatrixFA:
    def __init__(self, automaton: NondeterministicFiniteAutomaton | None = None):
        if automaton is None:
            self.state_to_idx = {}
            self.idx_to_state = {}
            self.num_states = 0
            self.start_states = set()
            self.final_states = set()
            self.bool_decomp = {}
            return

        states = list(automaton.states)

        self.state_to_idx = {state: i for i, state in enumerate(states)}
        self.idx_to_state = {i: state for state, i in self.state_to_idx.items()}

        self.num_states = len(states)

        self.start_states = {self.state_to_idx[s] for s in automaton.start_states}
        self.final_states = {self.state_to_idx[s] for s in automaton.final_states}

        self.bool_decomp: dict[Symbol, csr_matrix] = {}

        for from_state, label, to_state in automaton:
            if label not in self.bool_decomp:
                self.bool_decomp[label] = csr_matrix(
                    (self.num_states, self.num_states), dtype=bool
                )

            i = self.state_to_idx[from_state]
            j = self.state_to_idx[to_state]

            self.bool_decomp[label][i, j] = True

    def accepts(self, word: Iterable[Symbol]) -> bool:
        current = np.zeros(self.num_states, dtype=bool)
        current[list(self.start_states)] = True

        for symbol in word:
            if symbol not in self.bool_decomp:
                return False
            current = current @ self.bool_decomp[symbol]

        return any(current[i] for i in self.final_states)

    def transitive_closure(self) -> csr_matrix:
        identity = eye(self.num_states, dtype=bool, format="csr")

        if not self.bool_decomp:
            return identity

        reach = identity + sum(self.bool_decomp.values())

        while True:
            new_reach = reach + reach @ reach

            if (new_reach - reach).nnz == 0:
                break

            reach = new_reach

        return reach

    def is_empty(self) -> bool:
        reach = self.transitive_closure()

        return not any(
            reach[start, final]
            for start in self.start_states
            for final in self.final_states
        )


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    result = AdjacencyMatrixFA()
    result.num_states = automaton1.num_states * automaton2.num_states

    for s1, i1 in automaton1.state_to_idx.items():
        for s2, i2 in automaton2.state_to_idx.items():
            state = State((s1, s2))
            idx = i1 * automaton2.num_states + i2

            result.state_to_idx[state] = idx
            result.idx_to_state[idx] = state

            if i1 in automaton1.start_states and i2 in automaton2.start_states:
                result.start_states.add(idx)

            if i1 in automaton1.final_states and i2 in automaton2.final_states:
                result.final_states.add(idx)

    common_labels = automaton1.bool_decomp.keys() & automaton2.bool_decomp.keys()

    result.bool_decomp = {
        label: kron(
            automaton1.bool_decomp[label], automaton2.bool_decomp[label], format="csr"
        )
        for label in common_labels
    }

    return result


def tensor_based_rpq(
    regex: str,
    graph: nx.MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
) -> set[tuple[int, int]]:
    graph_fa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    regex_fa = AdjacencyMatrixFA(regex_to_dfa(regex))

    intersection = intersect_automata(graph_fa, regex_fa)
    reach = intersection.transitive_closure()

    result = set()

    for start in intersection.start_states:
        for final in intersection.final_states:
            if reach[start, final]:
                graph_from, _ = intersection.idx_to_state[start].value
                graph_to, _ = intersection.idx_to_state[final].value
                result.add((graph_from.value, graph_to.value))

    return result
