from attractors.attractors import attractor
from collections import defaultdict

import time
import copy


def complement_prios(bdd, g):
    for prio_f_index in range(g.k):
        new_dict = defaultdict(lambda: bdd.false)
        for k, v in g.gamma[prio_f_index].items():
            new_dict[k + 1] = v
        g.gamma[prio_f_index] = new_dict
        g.d[prio_f_index] += 1


def classical(bdd, g):
    complement_prios(bdd, g)

    for curr_f in range(g.k):
        curr_max = g.d[curr_f]
        if curr_max % 2 == 0:
            g.d[curr_f] = curr_max + 1
        else:
            g.d[curr_f] = curr_max
    max_values = copy.copy(g.d)
    return disj_par_win(bdd, g, max_values)


# Solve a game with a disjunction of even parity objectives as winning condition for player 1
def disj_par_win(bdd, g, max_values):
    if all(value == 1 for value in max_values) or (g.phi_0 | g.phi_1) == bdd.false:
        return g.phi_0 | g.phi_1, bdd.false
    for curr_f in range(g.k):
        if max_values[curr_f] != 1:
            a0 = attractor(bdd, g, 0, g.gamma[curr_f][max_values[curr_f]])
            g_bar = g.induced_game(bdd, ~a0)
            a1 = attractor(bdd, g_bar, 1, g_bar.gamma[curr_f][max_values[curr_f] - 1])
            h = g_bar.induced_game(bdd, ~a1)

            while True:
                copy_max_values = copy.copy(max_values)
                copy_max_values[curr_f] -= 2

                w0, w1 = disj_par_win(bdd, h, copy_max_values)
                if g_bar.phi_0 | g_bar.phi_1 == bdd.false or w1 == (h.phi_0 | h.phi_1):
                    break
                a0 = attractor(bdd, g_bar, 0, w0)
                g_bar = g_bar.induced_game(bdd, ~a0)
                a1 = attractor(bdd, g_bar, 1, g_bar.gamma[curr_f][max_values[curr_f] - 1])
                h = g_bar.induced_game(bdd, ~a1)
            q_bar = g_bar.phi_0 | g_bar.phi_1
            if w1 == (h.phi_0 | h.phi_1) and not q_bar == bdd.false:
                a1 = attractor(bdd, g, 1, q_bar)
                w0_bis, w1_bis = disj_par_win(bdd, g.induced_game(bdd, ~a1), max_values)
                return w0_bis, a1 | w1_bis
    return g.phi_0 | g.phi_1, bdd.false


def classical_with_psolver(bdd, g, psolver):
    psolver_solved = False
    (z0, z1) = psolver(bdd, g)

    g_bar = g.induced_game(bdd, ~(z0 | z1))

    if (g_bar.phi_0 | g_bar.phi_1) == bdd.false:
        psolver_solved = True
        return z0, z1, psolver_solved

    complement_prios(bdd, g_bar)

    for curr_f in range(g_bar.k):
        curr_max = g_bar.d[curr_f]
        if curr_max % 2 == 0:
            g_bar.d[curr_f] = curr_max + 1
        else:
            g_bar.d[curr_f] = curr_max
    max_values = copy.copy(g_bar.d)
    (w0, w1) = disj_par_win(bdd, g_bar, max_values)
    return w0 | z0, w1 | z1, psolver_solved
