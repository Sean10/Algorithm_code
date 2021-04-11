
import networkx as nx
# 使用networkx现成的toposort
g = nx.DiGraph(incoming_graph_data=name_graph)
ordered_graph = list(reversed(list(nx.algorithms.dag.topological_sort(g))))