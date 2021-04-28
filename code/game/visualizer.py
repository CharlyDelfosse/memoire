from pyeda.inter import *
from pyeda.boolalg.boolfunc import num2upoint

import matplotlib.pyplot as plt
import networkx as nx


def graphgame_viz(gg):
    nx_graph = nx.DiGraph()
    color_map = []

    all_nodes = get_all_nodes(gg)

    node_id = 0
    for curr_node in all_nodes:
        if gg.phi_0.restrict(curr_node).is_one():
            curr_prio = get_prio(gg,curr_node)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + " , " + str(list(curr_node.values()))
            color_map.append('green')
            node_id += 1

        elif gg.phi_1.restrict(curr_node).is_one():
            curr_prio = get_prio(gg, curr_node)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + " , "+ str(list(curr_node.values()))
            color_map.append('red')
            node_id += 1

    graph_nodes = list(nx_graph.nodes(data=True))
    for c_node, node_attr in graph_nodes:
        if gg.phi_0.restrict(node_attr["vars"]).is_one() or gg.phi_1.restrict(node_attr["vars"]).is_one():
            exiting_edges = gg.tau.restrict(node_attr["vars"])
            for c_succ, succ_attr in graph_nodes:
                if exiting_edges.compose(gg.mapping_inv).restrict(succ_attr["vars"]).is_one():
                    nx_graph.add_edge(c_node, c_succ)

    labels = nx.get_node_attributes(nx_graph,"node_info")
    nx.draw(nx_graph, node_color=color_map, labels=labels, with_labels=True, node_size=700)

    plt.show()


def get_all_nodes(gg):
    all_nodes = []
    for i in range(0, gg.n):
        current_node_point = num2point(i, gg.q_vars)

        all_nodes.append(current_node_point)
    return all_nodes


def get_prio(gg, node):
    for i in range(0, gg.d + 1):
        if gg.gamma[i].restrict(node).is_one():
            return i
