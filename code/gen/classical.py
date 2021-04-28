import copy

from attractors.attractors import attractor
from pyeda.inter import *


def complement_game(g):
    for prio_f_index in range(g.k):
        g.d[prio_f_index] += 1
        curr_new_func = [expr2bdd(expr(False)) for _ in range(g.d[prio_f_index] + 2)]
        for prio in range(1, g.d[prio_f_index] + 2):
            curr_new_func[prio] = g.gamma[prio_f_index][prio - 1]
        g.gamma[prio_f_index] = curr_new_func


def classical_gen(g):
    complement_game(g)
    max_values = [0] * g.k

    for prio_f_index in range(g.k):
        curr_max = g.d[prio_f_index]
        if curr_max % 2 == 0:
            max_values[prio_f_index] = curr_max + 1
        else:
            max_values[prio_f_index] = curr_max
    return disj_par_win(g, max_values)


def disj_par_win(g, max_values):
    if all(value == 1 for value in max_values) or (g.phi_0 | g.phi_1).is_zero():
        return g.phi_0 | g.phi_1, expr2bdd(expr(False))
    for curr_f in range(g.k):
        if max_values[curr_f] != 1:

            max_odd = attractor(g, 0, g.gamma[curr_f][max_values[curr_f]])
            g_j = g.induced_game(~max_odd)
            max_even = attractor(g, 1, g.gamma[curr_f][max_values[curr_f] - 1])
            h_j = g_j.induced_game(~max_even)
            j = 0
            while True:
                j = j + 1
                max_values_copy = copy.copy(max_values)
                max_values_copy[curr_f] -= 2
                w0, w1 = disj_par_win(h_j, max_values_copy)
                if (g_j.phi_0 | g_j.phi_1).is_zero() or w1 is (h_j.phi_0 | h_j.phi_1):
                    break
                attr_w0 = attractor(g_j, 0, w0)
                g_j = g_j.induced_game(~attr_w0)
                h_j = h_j.induced_game(attractor(g_j, 1, g_j.gamma[curr_f][max_values[curr_f] - 1]))

            if w1 is (h_j.phi_0 | h_j.phi_1) and not (g_j.phi_0 | g_j.phi_1).is_zero():
                attr_trap = attractor(g, 1, (g_j.phi_0 | g_j.phi_1))
                w0_bis, w1_bis = disj_par_win(g.induced_game(~attr_trap), max_values)
                w1 = attr_trap | w1_bis
                return w0_bis, w1
    return g.phi_0 | g.phi_1, expr2bdd(expr(False))


def classical_with_psolver(g, psolver):
    (z0, z1) = psolver(g)
    print(z0.is_zero())
    print(z1.is_zero())
    g_bar = g.induced_game(~(z0 | z1))

    complement_game(g_bar)
    max_values = [0] * g_bar.k
    for prio_f_index in range(g_bar.k):
        curr_max = g_bar.d[prio_f_index]
        if curr_max % 2 == 0:
            max_values[prio_f_index] = curr_max + 1
        else:
            max_values[prio_f_index] = curr_max
    (w0, w1) = disj_par_win(g_bar, max_values)
    return w0 | z0, w1 | z1