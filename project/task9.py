import networkx as nx
import pyformlang.rsa as rsa


def gll_based_cfpq(
    rsm: rsa.RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    start_nodes = set(graph.nodes) if start_nodes is None else start_nodes
    final_nodes = set(graph.nodes) if final_nodes is None else final_nodes

    initial_label = rsm.initial_label

    box_start = {}
    box_final = {}
    box_terms = {}
    box_nonterms = {}
    for label, box in rsm.boxes.items():
        box_start[label] = next(iter(box.dfa.start_states))
        box_final[label] = box.final_states
        terms = {}
        nonterms = {}
        for from_s, sym, to_s in box.dfa:
            if sym in rsm.boxes:
                nonterms.setdefault(from_s, []).append((sym, to_s))
            else:
                terms.setdefault(from_s, []).append((sym.value, to_s))
        box_terms[label] = terms
        box_nonterms[label] = nonterms

    graph_adj = {}
    for u, v, data in graph.edges(data=True):
        lbl = data.get("label")
        if lbl is not None:
            graph_adj.setdefault(lbl, {}).setdefault(u, []).append(v)

    gss_returns = {}
    pop_set = {}

    visited = set()
    queue = []

    def add_descriptor(label, rsm_state, graph_node, gss_key):
        desc = (label, rsm_state, graph_node, gss_key)
        if desc not in visited:
            visited.add(desc)
            queue.append(desc)

    def add_gss_return(gss_key, ret_label, ret_state, parent_gss_key):
        ret = (ret_label, ret_state, parent_gss_key)
        returns = gss_returns.setdefault(gss_key, set())
        if ret not in returns:
            returns.add(ret)
            for popped_node in pop_set.get(gss_key, set()):
                add_descriptor(ret_label, ret_state, popped_node, parent_gss_key)

    def do_pop(gss_key, graph_node):
        popped = pop_set.setdefault(gss_key, set())
        if graph_node not in popped:
            popped.add(graph_node)
            for ret_label, ret_state, parent_gss_key in gss_returns.get(gss_key, set()):
                add_descriptor(ret_label, ret_state, graph_node, parent_gss_key)

    for start_node in start_nodes:
        gss_key = (initial_label, start_node)
        add_descriptor(initial_label, box_start[initial_label], start_node, gss_key)

    while queue:
        label, rsm_state, graph_node, gss_key = queue.pop()

        for sym_value, next_state in box_terms[label].get(rsm_state, []):
            for next_graph_node in graph_adj.get(sym_value, {}).get(graph_node, []):
                add_descriptor(label, next_state, next_graph_node, gss_key)

        for nonterm_sym, next_state in box_nonterms[label].get(rsm_state, []):
            new_gss_key = (nonterm_sym, graph_node)
            add_gss_return(new_gss_key, label, next_state, gss_key)
            add_descriptor(nonterm_sym, box_start[nonterm_sym], graph_node, new_gss_key)

        if rsm_state in box_final[label]:
            do_pop(gss_key, graph_node)

    result = set()
    for start_node in start_nodes:
        gss_key = (initial_label, start_node)
        for end_node in pop_set.get(gss_key, set()):
            if end_node in final_nodes:
                result.add((start_node, end_node))

    return result
