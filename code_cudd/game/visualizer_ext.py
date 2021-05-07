import matplotlib.pyplot as plt
import networkx as nx

import utils


def graphgame_viz_ext(bdd, gg, m_vars, m_bis_vars, tau_e):
    nx_graph = nx.DiGraph()
    color_map = []

    update_mapping_inv(gg, m_vars, m_bis_vars)
    all_nodes = get_all_nodes(bdd, gg, m_vars)

    node_id = 0
    for curr_node in all_nodes:
        if bdd.let(curr_node, gg.phi_0) == bdd.true:
            curr_prio = get_prio(bdd, gg, curr_node)
            curr_m = get_m(curr_node, m_vars)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + "," + str(
                list(map(boolean_to_const, node_infos(m_vars, curr_node)))[0:gg.n_vars]) + "," + str(curr_m)
            color_map.append('green')
            node_id += 1

        elif bdd.let(curr_node, gg.phi_1) == bdd.true:
            curr_prio = get_prio(bdd, gg, curr_node)
            curr_m = get_m(curr_node, m_vars)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + "," + str(
                list(map(boolean_to_const, node_infos(m_vars, curr_node)))[0:gg.n_vars]) + "," + str(curr_m)
            color_map.append('red')
            node_id += 1

    graph_nodes = list(nx_graph.nodes(data=True))
    for c_node, node_attr in graph_nodes:
        if bdd.let(node_attr["vars"], gg.phi_0) == bdd.true or bdd.let(node_attr["vars"], gg.phi_1) == bdd.true:
            exiting_edges = bdd.let(node_attr["vars"], tau_e)

            for c_succ, succ_attr in graph_nodes:
                if bdd.let(succ_attr["vars"], bdd.let(gg.mapping_inv, exiting_edges)) == bdd.true:
                    nx_graph.add_edge(c_node, c_succ, length=100)

    labels = nx.get_node_attributes(nx_graph, "node_info")
    plt.figure(1, figsize=(8, 8))
    nx.draw(nx_graph, node_color=color_map, labels=labels, with_labels=True, node_size=700)

    plt.show()


def get_all_nodes(bdd, gg, m_vars):
    all_nodes = []
    all_possiblities = list(bdd.pick_iter(bdd.true, gg.q_vars))
    for i in range(0, gg.n):
        current_node_dict = all_possiblities[i]
        for j in range(0, gg.d + 1):
            current_m_dict = utils.num_to_map(j, m_vars)
            curr_dict = dict(current_node_dict)
            curr_dict.update(current_m_dict)
            all_nodes.append(curr_dict)
    return all_nodes


def get_prio(bdd, gg, node):
    for i in range(0, gg.d + 1):
        if bdd.let(node, gg.gamma[i]) == bdd.true:
            return i


def get_m(node, m_vars):
    m_str = ''
    for c_var in m_vars:
        m_str = str(boolean_to_const(node[c_var])) + m_str
    return int(m_str, 2)


def update_mapping_inv(gg, m_vars, m_bis_vars):

    for c_var in range(len(m_bis_vars)):
        gg.mapping_inv[m_bis_vars[c_var]] = m_vars[c_var]

def node_infos(m_vars, node):
    res = []
    index = 0
    for i in sorted(node.keys()):
        if index >= len(m_vars):
            res.append(node[i])
        index += 1
    return res

def boolean_to_const(b):
    if b:
        return 1
    else:
        return 0