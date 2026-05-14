from typing import Set

import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    enfa = Regex(regex).to_epsilon_nfa()

    if enfa is None:
        raise ValueError(f"Failed to convert regex to epsilon NFA: {regex}")

    return enfa.to_deterministic().minimize()


def graph_to_nfa(
    graph: nx.MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    nodes = list(map(int, graph.nodes))
    for start in start_states if len(start_states) > 0 else nodes:
        if start not in nodes or not nfa.add_start_state(State(start)):
            raise Exception(f"Wrong start state: {start}")

    for final in final_states if len(final_states) > 0 else nodes:
        if final not in nodes or not nfa.add_final_state(State(final)):
            raise Exception(f"Wrong final state: {final}")

    return nfa
