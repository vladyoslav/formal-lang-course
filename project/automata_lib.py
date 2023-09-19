import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    EpsilonNFA,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex


def min_dfa_from_regex(string: str) -> DeterministicFiniteAutomaton:
    regex = Regex(string)
    enfa: EpsilonNFA = regex.to_epsilon_nfa()
    dfa: DeterministicFiniteAutomaton = enfa.to_deterministic()
    mdfa = dfa.minimize()
    return mdfa


def nfa_from_graph(
    graph: nx.MultiDiGraph, starts: list[int] = None, finals: list[int] = None
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    nodes = list(map(int, graph.nodes))
    for start in starts if starts is not None else nodes:
        if start not in nodes or not nfa.add_start_state(start):
            raise Exception(f"Wrong start state: {start}")

    for final in finals if finals is not None else nodes:
        if final not in nodes or not nfa.add_final_state(final):
            raise Exception(f"Wrong final state: {final}")

    return nfa
