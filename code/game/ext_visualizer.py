from pyeda.inter import *

import matplotlib.pyplot as plt
import networkx as nx


def graphgame_viz(gg, m_vars, m_bis_vars, tau_e):
    nx_graph = nx.DiGraph()
    color_map = []

    update_mapping_inv(gg, m_vars, m_bis_vars)
    print(gg.mapping_inv)
    all_nodes = get_all_nodes(gg, m_vars)

    node_id = 0
    for curr_node in all_nodes:
        if gg.phi_0.restrict(curr_node).is_one():
            curr_prio = get_prio(gg, curr_node)
            curr_m = get_m(curr_node, m_vars)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + "," + str(
                list(curr_node.values())[0:gg.n_vars]) + "," + str(curr_m)
            color_map.append('green')
            node_id += 1

        elif gg.phi_1.restrict(curr_node).is_one():
            curr_prio = get_prio(gg, curr_node)
            curr_m = get_m(curr_node, m_vars)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + "," + str(
                list(curr_node.values())[0:gg.n_vars]) + "," + str(curr_m)
            color_map.append('red')
            node_id += 1

    graph_nodes = list(nx_graph.nodes(data=True))
    for c_node, node_attr in graph_nodes:
        if gg.phi_0.restrict(node_attr["vars"]).is_one() or gg.phi_1.restrict(node_attr["vars"]).is_one():
            exiting_edges = tau_e.restrict(node_attr["vars"])
            print(bdd2expr(exiting_edges))
            for c_succ, succ_attr in graph_nodes:
                if exiting_edges.compose(gg.mapping_inv).restrict(succ_attr["vars"]).is_one():
                    nx_graph.add_edge(c_node, c_succ, length=100)

    labels = nx.get_node_attributes(nx_graph, "node_info")
    plt.figure(1, figsize=(8, 8))
    nx.draw(nx_graph, node_color=color_map, labels=labels, with_labels=True, node_size=700)

    plt.show()


def get_all_nodes(gg, m_vars):
    all_nodes = []
    for i in range(0, gg.n):
        current_node_point = num2point(i, gg.q_vars)
        for j in range(0, gg.p + 1):
            current_m_point = num2point(j, m_vars)
            curr_dict = dict(current_node_point)
            curr_dict.update(current_m_point)
            all_nodes.append(curr_dict)

    return all_nodes


def get_prio(gg, node):
    for i in range(0, gg.p + 1):
        if gg.gamma[i].restrict(node).is_one():
            return i
    return -1


def get_m(node, m_vars):
    m_str = ''
    for c_var in m_vars:
        m_str = str(node[c_var]) + m_str
    return int(m_str, 2)


def update_mapping_inv(gg, m_vars, m_bis_vars):

    for c_var in range(len(m_bis_vars)):
        gg.mapping_inv[m_bis_vars[c_var]] = m_vars[c_var]
