from pyeda.inter import *

import buchi
from itertools import product

from attractors import attractors


def buchi_solver_gen(g):
    priorities = [[] for _ in range(g.k)]
    even_priorities = [[] for _ in range(g.k)]

    for prio_f_index in range(g.k):
        for curr_prio in range(g.d[prio_f_index] + 1):
            curr_expr = g.gamma[prio_f_index][curr_prio]
            if not curr_expr.is_zero():
                priorities[prio_f_index].append(curr_prio)

    for prio_f_index in range(g.k):
        even_priorities[prio_f_index] = filter(lambda x: x % 2 == 0, priorities[prio_f_index])
    all_combinations = product(*even_priorities)

    # Iterate over all 1-priority
    for prio_f_index in range(g.k):
        for curr_prio in range(g.d[prio_f_index] + 1):
            if curr_prio % 2 == 1 and not g.gamma[prio_f_index][curr_prio].is_zero():
                u = g.gamma[prio_f_index][curr_prio]
                u_bis = g.sup_prio_expr_even(curr_prio, prio_f_index)
                w = attractors.attractor(g, 1, buchi.buchi_inter_safety(g, 1, u, u_bis))
                if not w.is_zero():
                    ind_game = g.induced_game(~w)
                    (z0, z1) = buchi_solver_gen(ind_game)
                    return z0, z1 | w

    # Iterate over all 0-priority vectors
    for curr_comb in all_combinations:
        u = [expr2bdd(expr(False))] * g.k
        for l in range(g.k):
            u[l] = g.gamma[l][curr_comb[l]]
        u_bis = g.sup_one_prio_odd(curr_comb)
        w = attractors.attractor(g, 0, buchi.buchi_inter_safety_gen(g, 0, u, u_bis))
        if not w.is_zero():
            ind_game = g.induced_game(~w)
            (z0, z1) = buchi_solver_gen(ind_game)
            return z0 | w, z1

    return expr2bdd(expr(False)), expr2bdd(expr(False))
