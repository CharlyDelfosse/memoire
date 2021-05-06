import random
from game.graphgame import GraphGame


def random_phi_and_p(bdd, game_infos):
    phi_0 = bdd.false
    phi_1 = bdd.false
    gamma = [bdd.false for _ in range(game_infos.d + 1)]

    all_nodes = []
    all_possiblities = list(bdd.pick_iter(bdd.true, game_infos.q_vars))
    for i in range(0, game_infos.n):
        current_node_dict = all_possiblities[i]
        current_node_bdd = bdd.cube(current_node_dict)

        all_nodes.append(current_node_bdd)
        rand_player = random.randint(0, 1)
        if rand_player == 0:
            phi_0 = phi_0 | current_node_bdd
        else:
            phi_1 = phi_1 | current_node_bdd
        rand_priority = random.randint(0, game_infos.d)

        gamma[rand_priority] = gamma[rand_priority] | current_node_bdd

    return phi_0, phi_1, gamma, all_nodes


def random_tau(bdd, game_infos, i, o, all_nodes):
    tau = bdd.false
    for c_node in range(0, game_infos.n):
        rand_degree = random.randint(i, o)
        succ_list = [c_node]
        for j in range(0, rand_degree):
            node_cand = [k for k in range(0, game_infos.n) if k not in succ_list]
            rand_succ = random.choice(node_cand)
            succ_list.append(rand_succ)

            tau = tau | (all_nodes[c_node] & bdd.let(game_infos.mapping_bis, all_nodes[rand_succ]))

    return tau


def random_game(bdd, n, p, i, o):
    game_infos = GraphGame(bdd, n, p)

    (phi_0, phi_1, gamma, all_nodes) = random_phi_and_p(bdd, game_infos)
    tau = random_tau(bdd, game_infos, i, o, all_nodes)
    game_infos.set_expr(phi_0, phi_1, tau, gamma)

    return game_infos
