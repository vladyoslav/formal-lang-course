import networkx as nx
import pyformlang.cfg as cfg
from collections import defaultdict
from scipy.sparse import csr_matrix

from project.task6 import cfg_to_weak_normal_form


def matrix_based_cfpq(
    grammar: cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    wnf = cfg_to_weak_normal_form(grammar)

    nodes = list(graph.nodes)
    n = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    matrices: dict[cfg.Variable, csr_matrix] = defaultdict(
        lambda: csr_matrix((n, n), dtype=bool)
    )

    for nonterm in wnf.get_nullable_symbols():
        matrices[nonterm].setdiag(True)

    for production in wnf.productions:
        if len(production.body) == 1:
            terminal = production.body[0]
            for u, v, data in graph.edges(data=True):
                if data.get("label") == terminal.value:
                    matrices[production.head][node_to_idx[u], node_to_idx[v]] = True

    binary_productions = [p for p in wnf.productions if len(p.body) == 2]

    changed = True
    while changed:
        changed = False
        for production in binary_productions:
            a, b = production.body
            head = production.head
            old_nnz = matrices[head].nnz
            matrices[head] += matrices[a] @ matrices[b]
            if matrices[head].nnz > old_nnz:
                changed = True

    start_nodes = set(graph.nodes) if start_nodes is None else start_nodes
    final_nodes = set(graph.nodes) if final_nodes is None else final_nodes

    pairs = set()
    start_matrix = matrices.get(wnf.start_symbol)
    if start_matrix is None:
        return pairs

    for u in start_nodes:
        for v in final_nodes:
            if start_matrix[node_to_idx[u], node_to_idx[v]]:
                pairs.add((u, v))

    return pairs
