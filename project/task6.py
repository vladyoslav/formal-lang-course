import networkx as nx
import pyformlang.cfg as cfg


def cfg_to_weak_normal_form(grammar: cfg.CFG) -> cfg.CFG:
    wnf = (
        grammar.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )

    new_productions = wnf._get_productions_with_only_single_terminals()
    new_productions = wnf._decompose_productions(new_productions)
    wnf = cfg.CFG(start_symbol=wnf.start_symbol, productions=set(new_productions))

    return wnf


def hellings_based_cfpq(
    grammar: cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    wnf = cfg_to_weak_normal_form(grammar)

    result = set()

    for nonterm in wnf.get_nullable_symbols():
        for v in graph.nodes:
            result.add((nonterm, v, v))

    for production in wnf.productions:
        if len(production.body) == 1:
            terminal = production.body[0]
            for u, v, data in graph.edges(data=True):
                if data.get("label") == terminal.value:
                    result.add((production.head, u, v))

    queue = set(result)

    binary_productions = [p for p in wnf.productions if len(p.body) == 2]

    while queue:
        nonterm, from_node, to_node = queue.pop()

        for other_nonterm, other_from, other_to in list(result):
            for production in binary_productions:
                if other_to == from_node and production.body == [
                    other_nonterm,
                    nonterm,
                ]:
                    triple = (production.head, other_from, to_node)
                    if triple not in result:
                        queue.add(triple)
                        result.add(triple)

                if other_from == to_node and production.body == [
                    nonterm,
                    other_nonterm,
                ]:
                    triple = (production.head, from_node, other_to)
                    if triple not in result:
                        queue.add(triple)
                        result.add(triple)

    start_nodes = set(graph.nodes) if start_nodes is None else start_nodes
    final_nodes = set(graph.nodes) if final_nodes is None else final_nodes

    pairs = set()
    for nonterm, from_node, to_node in result:
        if (
            nonterm == wnf.start_symbol
            and from_node in start_nodes
            and to_node in final_nodes
        ):
            pairs.add((from_node, to_node))

    return pairs
