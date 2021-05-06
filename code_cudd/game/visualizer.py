import networkx as nx
from matplotlib import pyplot as plt


def boolean_to_const(b):
    if b:
        return 1
    else:
        return 0


def graphgame_viz(bdd, gg):
    nx_graph = nx.DiGraph()
    color_map = []

    all_nodes = get_all_nodes(bdd, gg)

    node_id = 0
    for curr_node in all_nodes:
        if bdd.let(curr_node, gg.phi_0) == bdd.true:
            curr_prio = get_prio(bdd, gg, curr_node)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + " , " + str(
                list(map(boolean_to_const, list(curr_node.values()))))
            color_map.append('green')
            node_id += 1

        elif bdd.let(curr_node, gg.phi_1) == bdd.true:
            curr_prio = get_prio(bdd, gg, curr_node)
            nx_graph.add_node(node_id, prio=str(curr_prio))
            nx_graph.nodes[node_id]["vars"] = curr_node
            nx_graph.nodes[node_id]["node_info"] = str(curr_prio) + " , " + str(
                list(map(boolean_to_const, list(curr_node.values()))))
            color_map.append('red')
            node_id += 1

    graph_nodes = list(nx_graph.nodes(data=True))
    for c_node, node_attr in graph_nodes:
        if bdd.let(node_attr["vars"], gg.phi_0) == bdd.true or bdd.let(node_attr["vars"], gg.phi_1) == bdd.true:
            exiting_edges = bdd.let(node_attr["vars"], gg.tau)
            for c_succ, succ_attr in graph_nodes:
                if bdd.let(succ_attr["vars"], bdd.let(gg.mapping_inv, exiting_edges)) == bdd.true:
                    nx_graph.add_edge(c_node, c_succ)

    labels = nx.get_node_attributes(nx_graph, "node_info")
    nx.draw(nx_graph, node_color=color_map, labels=labels, with_labels=True, node_size=700)

    plt.show()


def get_all_nodes(bdd, gg):
    all_nodes = []
    all_possiblities = list(bdd.pick_iter(bdd.true, gg.q_vars))
    for i in range(0, gg.n):
        current_node_dict = all_possiblities[i]
        all_nodes.append(current_node_dict)
    return all_nodes


def get_prio(bdd, gg, node):
    for i in range(0, gg.d + 1):
        if bdd.let(node, gg.gamma[i]) == bdd.true:
            return i
