from collections import defaultdict

import networkx as nx
import pyformlang.cfg as cfg
import pyformlang.rsa as rsa
from scipy.sparse import csr_matrix, eye, kron


def cfg_to_rsm(grammar: cfg.CFG) -> rsa.RecursiveAutomaton:
    return ebnf_to_rsm(grammar.to_text())


def ebnf_to_rsm(ebnf: str) -> rsa.RecursiveAutomaton:
    return rsa.RecursiveAutomaton.from_text(ebnf)


def tensor_based_cfpq(
    rsm: rsa.RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    graph_nodes = list(graph.nodes)
    n_graph = len(graph_nodes)
    node_to_idx = {node: i for i, node in enumerate(graph_nodes)}

    rsm_states = []
    for label, box in rsm.boxes.items():
        for state in box.dfa.states:
            rsm_states.append((label, state))
    rsm_state_to_idx = {s: i for i, s in enumerate(rsm_states)}
    n_rsm = len(rsm_states)

    graph_bool_decomp: dict = defaultdict(
        lambda: csr_matrix((n_graph, n_graph), dtype=bool)
    )
    for u, v, data in graph.edges(data=True):
        label = data.get("label")
        if label is not None:
            graph_bool_decomp[label][node_to_idx[u], node_to_idx[v]] = True

    rsm_bool_decomp: dict = defaultdict(lambda: csr_matrix((n_rsm, n_rsm), dtype=bool))
    rsm_final_states = {}
    start_state_to_label = {}
    for label, box in rsm.boxes.items():
        for from_state, sym, to_state in box.dfa:
            i = rsm_state_to_idx[(label, from_state)]
            j = rsm_state_to_idx[(label, to_state)]
            rsm_bool_decomp[sym.value][i, j] = True

        for start_state in box.dfa.start_states:
            start_state_to_label[rsm_state_to_idx[(label, start_state)]] = label

        rsm_final_states[label] = {
            rsm_state_to_idx[(label, s)] for s in box.final_states
        }

        if box.dfa.start_states & box.final_states:
            graph_bool_decomp[label.value].setdiag(True)

    start_nodes = set(graph.nodes) if start_nodes is None else start_nodes
    final_nodes = set(graph.nodes) if final_nodes is None else final_nodes

    prev_nnz = -1
    while True:
        curr_nnz = sum(mat.nnz for mat in graph_bool_decomp.values())
        if curr_nnz == prev_nnz:
            break
        prev_nnz = curr_nnz

        kron_product = csr_matrix((n_rsm * n_graph, n_rsm * n_graph), dtype=bool)
        for sym in rsm_bool_decomp:
            if sym in graph_bool_decomp:
                kron_product += kron(
                    rsm_bool_decomp[sym], graph_bool_decomp[sym], format="csr"
                )

        reach = eye(n_rsm * n_graph, dtype=bool, format="csr") + kron_product
        while True:
            new_reach = reach + reach @ reach
            if (new_reach - reach).nnz == 0:
                break
            reach = new_reach

        for row, col in zip(*reach.nonzero()):
            rsm_from = row // n_graph
            rsm_to = col // n_graph
            graph_from = row % n_graph
            graph_to = col % n_graph

            label = start_state_to_label.get(rsm_from)
            if label is not None and rsm_to in rsm_final_states[label]:
                graph_bool_decomp[label.value][graph_from, graph_to] = True

    result = set()
    start_matrix = graph_bool_decomp.get(rsm.initial_label.value)
    if start_matrix is None:
        return result

    for u in start_nodes:
        for v in final_nodes:
            if start_matrix[node_to_idx[u], node_to_idx[v]]:
                result.add((u, v))

    return result
