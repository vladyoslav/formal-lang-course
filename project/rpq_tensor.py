import networkx as nx
import project.automata_lib as al
import project.fa_intersection as il


def rpq_tensor(
    graph: nx.MultiDiGraph, regex: str, starts: list[int] = None, finals: list[int] = None
) -> set[(int, int)]:
    regex_dfa = al.min_dfa_from_regex(regex)
    graph_nfa = al.nfa_from_graph(graph, starts, finals)

    ifa = il.intersect(graph_nfa, regex_dfa)
    ifa_graph = ifa.to_networkx()

    transitive_closure = nx.transitive_closure(ifa_graph, reflexive=True)

    result = set()

    dfa_states_number = len(list(regex_dfa.states))
    nfa_states = list(graph_nfa.states)

    for start in ifa.start_states:
        for final in ifa.final_states:
            if (start, final) in transitive_closure.edges():
                start_index = start.value // dfa_states_number
                final_index = final.value // dfa_states_number

                result.add((nfa_states[start_index], nfa_states[final_index]))

    return result
