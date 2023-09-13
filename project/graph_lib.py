import cfpq_data
import networkx as nx


def get_graph_by_name(name: str) -> nx.MultiDiGraph:
    graph_path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(graph_path)


def get_graph_info(graph: nx.MultiDiGraph) -> (int, int, list[str]):
    nodes = graph.number_of_nodes()
    edges = graph.size()
    labels = [e[2] for e in graph.edges(data="label")]
    return nodes, edges, labels


def make_labeled_two_cycles_graph(
    first: int, second: int, labels: tuple[str, str], path: str
):
    graph = cfpq_data.labeled_two_cycles_graph(first, second, labels=labels)
    nx.nx_pydot.write_dot(graph, path)
