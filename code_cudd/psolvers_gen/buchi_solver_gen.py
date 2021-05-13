from itertools import product

from attractors import attractors
import buchi


def buchi_solver_gen(bdd, g):
    # Iterate over all 1-priority
    for prio_f_index in range(g.k):
        for curr_prio in range(g.d[prio_f_index] + 1):
            if curr_prio % 2 == 1 and not g.gamma[prio_f_index][curr_prio] == bdd.false:
                u = g.gamma[prio_f_index][curr_prio]
                u_bis = g.sup_prio_expr_even(bdd, curr_prio, prio_f_index)
                w = attractors.attractor(bdd, g, 1, buchi.buchi_inter_safety(bdd, g, 1, u, u_bis))
                if not w == bdd.false:
                    ind_game = g.induced_game(bdd, ~w)
                    (z0, z1) = buchi_solver_gen(bdd, ind_game)
                    return z0, z1 | w

    even_priorities = [[] for _ in range(g.k)]
    for prio_f_index in range(g.k):
        for curr_prio in range(0, g.d[prio_f_index] + 1, 2):
            if not g.gamma[prio_f_index][curr_prio] == bdd.false:
                even_priorities[prio_f_index].append(curr_prio)

    all_combinations = product(*even_priorities)
    # Iterate over all 0-priority vectors
    for curr_comb in all_combinations:
        u = [g.gamma[l][curr_comb[l]] for l in range(g.k)]
        u_bis = g.sup_one_prio_odd(bdd, curr_comb)
        w = attractors.attractor(bdd, g, 0, buchi.buchi_inter_safety_gen(bdd, g, u, u_bis))
        if not w == bdd.false:
            ind_game = g.induced_game(bdd, ~w)
            (z0, z1) = buchi_solver_gen(bdd, ind_game)
            return z0 | w, z1

    return bdd.false, bdd.false
