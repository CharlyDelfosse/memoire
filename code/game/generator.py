import math
import random
from game.graphgame import GraphGame

from pyeda.inter import *


def random_phi_and_p(game_infos):
    phi_0 = expr2bdd(expr(False))
    phi_1 = expr2bdd(expr(False))
    gamma = [expr2bdd(expr(False)) for _ in range(game_infos.p + 1)]

    all_nodes = []

    for i in range(0, game_infos.n):

        current_node_point = num2point(i, game_infos.q_vars)
        current_node_bdd = expr2bdd(expr(True))

        for curr_var in game_infos.q_vars:
            if current_node_point[curr_var] == 0:
                current_node_bdd = current_node_bdd & ~curr_var
            else:
                current_node_bdd = current_node_bdd & curr_var
        all_nodes.append(current_node_bdd)
        rand_player = random.randint(0, 1)
        if rand_player == 0:
            phi_0 = phi_0 | current_node_bdd
        else:
            phi_1 = phi_1 | current_node_bdd
        rand_priority = random.randint(0, game_infos.p)

        gamma[rand_priority] = gamma[rand_priority] | current_node_bdd

    return phi_0, phi_1, gamma, all_nodes


def random_tau(game_infos, i, o, all_nodes):
    tau = expr2bdd(expr(False))
    for c_node in range(0, game_infos.n):
        rand_degree = random.randint(i, o)
        succ_list = [c_node]
        for j in range(0, rand_degree):
            node_cand = [k for k in range(0, game_infos.n) if k not in succ_list]
            rand_succ = random.choice(node_cand)
            succ_list.append(rand_succ)

            tau = tau | (all_nodes[c_node] & all_nodes[rand_succ].compose(game_infos.mapping_bis))

    return tau


def random_game(n, p, i, o):
    game_infos = GraphGame(n, p)

    (phi_0, phi_1, gamma, all_nodes) = random_phi_and_p(game_infos)
    tau = random_tau(game_infos, i, o, all_nodes)
    game_infos.set_expr(phi_0, phi_1, tau, gamma)

    return game_infos
