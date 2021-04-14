from pyeda.inter import *
import copy
import matplotlib.pyplot as plt
import networkx as nx

from itertools import product

def graphgame_viz_gen_ext(gg, m_vars, m_bis_vars, tau_e):
    nx_graph = nx.DiGraph()
    color_map = []

    update_mapping_inv(gg, m_vars, m_bis_vars)
    all_nodes = get_all_nodes(gg, m_vars)

    node_id = 0
    for curr_node in all_nodes:
        if gg.phi_0.restrict(curr_node).is_one():
            curr_prios = get_prios(gg, curr_node)
            curr_m = get_m(gg, curr_node, m_vars)
            nx_graph.add_node(node_id, prio=str(curr_prios))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prios) + "," + str(
                list(curr_node.values())[0:gg.n_vars]) + "," + str(curr_m)
            color_map.append('green')
            node_id += 1

        elif gg.phi_1.restrict(curr_node).is_one():
            curr_prios = get_prios(gg, curr_node)
            curr_m = get_m(gg,curr_node, m_vars)
            nx_graph.add_node(node_id, prio=str(curr_prios))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prios) + "," + str(
                list(curr_node.values())[0:gg.n_vars]) + "," + str(curr_m)
            color_map.append('red')
            node_id += 1

    graph_nodes = list(nx_graph.nodes(data=True))
    for c_node, node_attr in graph_nodes:
        if gg.phi_0.restrict(node_attr["vars"]).is_one() or gg.phi_1.restrict(node_attr["vars"]).is_one():
            exiting_edges = tau_e.restrict(node_attr["vars"])
            for c_succ, succ_attr in graph_nodes:
                if exiting_edges.compose(gg.mapping_inv).restrict(succ_attr["vars"]).is_one():
                    nx_graph.add_edge(c_node, c_succ, length=100)

    labels = nx.get_node_attributes(nx_graph, "node_info")
    plt.figure(1, figsize=(8, 8))
    nx.draw(nx_graph, node_color=color_map, labels=labels, with_labels=True, node_size=700)

    plt.show()


def get_all_nodes(g, m_vars):
    all_nodes = []
    prio_combinations = [[] for _ in range(g.k)]
    for prio_f_index in range(g.k):
        for j in range(0, g.p[prio_f_index] + 1):
            prio_combinations[prio_f_index].append(j)
    all_comb = product(*prio_combinations)
    for i in range(0, g.n):
        current_node_point = num2point(i, g.q_vars)
        all_comb_copy = copy.copy(all_comb)
        for comb in all_comb_copy:
            curr_dict = dict(current_node_point)
            for prio_f_index in range(len(comb)):
                current_m_point = num2point(comb[prio_f_index], m_vars[prio_f_index])
                curr_dict.update(current_m_point)
            all_nodes.append(curr_dict)

    return all_nodes


def get_prios(g, node):
    res_prios = []
    for prio_f_index in range(g.k):
        for i in range(0, g.p[prio_f_index] + 1):
            if g.gamma[prio_f_index][i].restrict(node).is_one():
                res_prios.append(i)
                break
    return res_prios


def get_m(g, node, m_vars):
    res = []
    for prio_f_index in range(g.k):
        m_str = ''
        for c_var in m_vars[prio_f_index]:
            m_str = str(node[c_var]) + m_str
        res.append(int(m_str, 2))
    return res


def update_mapping_inv(gg, m_vars, m_bis_vars):
    for prio_f_index in range(gg.k):
        for c_var in range(len(m_bis_vars[prio_f_index])):
            gg.mapping_inv[m_bis_vars[prio_f_index][c_var]] = m_vars[prio_f_index][c_var]
