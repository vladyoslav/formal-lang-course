import networkx as nx
from scipy.sparse import csr_matrix, kron

from project.task2 import graph_to_nfa, regex_to_dfa
from project.task3 import AdjacencyMatrixFA


def ms_bfs_based_rpq(
    regex: str,
    graph: nx.MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
) -> set[tuple[int, int]]:
    graph_fa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    regex_fa = AdjacencyMatrixFA(regex_to_dfa(regex))

    n_graph = graph_fa.num_states
    n_regex = regex_fa.num_states

    if n_graph == 0 or n_regex == 0:
        return set()

    start_list = list(graph_fa.start_states)

    rows, cols = [], []
    for i_s, i_graph_start in enumerate(start_list):
        for i_regex_start in regex_fa.start_states:
            rows.append(i_s)
            cols.append(i_graph_start * n_regex + i_regex_start)

    front = csr_matrix(
        ([True] * len(rows), (rows, cols)),
        shape=(len(start_list), n_graph * n_regex),
        dtype=bool,
    )
    visited = front.copy()

    common_labels = graph_fa.bool_decomp.keys() & regex_fa.bool_decomp.keys()

    kron_matrices = {
        label: kron(
            graph_fa.bool_decomp[label], regex_fa.bool_decomp[label], format="csr"
        )
        for label in common_labels
    }

    while front.nnz > 0:
        new_front = csr_matrix((len(start_list), n_graph * n_regex), dtype=bool)

        for label in common_labels:
            new_front += front @ kron_matrices[label]

        front = new_front > visited
        visited += front

    result = set()

    for i_s, i_graph_start in enumerate(start_list):
        for i_graph_final in graph_fa.final_states:
            reachable = any(
                visited[i_s, i_graph_final * n_regex + i_regex_final]
                for i_regex_final in regex_fa.final_states
            )

            if reachable:
                start_node = graph_fa.idx_to_state[i_graph_start].value
                final_node = graph_fa.idx_to_state[i_graph_final].value
                result.add((start_node, final_node))

    return result
