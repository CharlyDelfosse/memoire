from copy import copy

from attractors import attractors
from pyeda.inter import *
from itertools import product


def psolQ_gen(g):
    min_even_prio = [[] for _ in range(g.k)]

    for prio_f_index in range(g.k):
        if g.p[prio_f_index] % 2 == 1:
            init_prio = g.p[prio_f_index]
        else:
            init_prio = g.p[prio_f_index] - 1
        for min_prio in range(init_prio, -1, -2):
            w = lay_ep(g, min_prio, prio_f_index)
            if not w.is_zero():
                x = attractors.attractor(g, 1, w)
                ind_game = g.induced_game(~x)
                (z0, z1) = psolQ_gen(ind_game)
                return z0, z1 | x

    for prio_f_index in range(g.k):
        if g.p[prio_f_index] % 2 == 0:
            init_prio = g.p[prio_f_index]
        else:
            init_prio = g.p[prio_f_index] - 1
        for curr_prio in range(init_prio, -1, -2):
            min_even_prio[prio_f_index].append(curr_prio)
    all_combinations = product(*min_even_prio)
    em_vars_n = g.k
    g.em_vars = bddvars('n', (0, em_vars_n))
    g.em_vars_bis = bddvars('n_bis', (0, em_vars_n))
    em_mapping = {}
    for prio_f_index in range(g.k):
        em_mapping[g.em_vars[prio_f_index]] = g.em_vars_bis[prio_f_index]
    tot_mapping = g.mapping_bis
    tot_mapping.update(em_mapping)

    for comb in all_combinations:
        w = lay_ep_full(g, comb)
        if not w.is_zero():
            x = attractors.attractor(g, 0, w)
            ind_game = g.induced_game(~x)
            (z0, z1) = psolQ_gen(ind_game)
            return z0 | x, z1

    return expr2bdd(expr(False)), expr2bdd(expr(False))


def lay_ep(g, min_prio, c_prio_f):
    f_old = g.sup_prio_expr_odd(min_prio, c_prio_f)
    while True:
        lay_attr_f = lay_attr(g, min_prio, f_old, c_prio_f)
        f = f_old & lay_attr_f
        if f is f_old:
            break
        f_old = f
    return f


def lay_ep_full(g, q):
    max_prios = []
    for c_prio in range(g.k):
        if g.p[c_prio] % 2 == 1:
            max_prios.append(g.p[c_prio] - 1)
        else:
            max_prios.append(g.p[c_prio])
    u = g.sup_all_prio_even(q)
    return lay_attr_full(g, q, u, max_prios)


def compute_tau_ext(g, min_prios):
    res_expr = g.tau

    for prio_f_index in range(g.k):
        # active in prec
        active_prio_1 = g.em_vars[prio_f_index]
        # active in current node
        active_prio_2 = g.sup_prio_expr(min_prios[prio_f_index], prio_f_index).compose(g.mapping_bis)
        active_prio = active_prio_1 | active_prio_2

        res_expr = res_expr & (active_prio & g.em_vars_bis[prio_f_index] | ~active_prio & ~g.em_vars_bis[prio_f_index])

    return res_expr


def lay_attr(g, min_prio, u, c_prio):
    if g.p[c_prio] % 2 == 0:
        init_prio = g.p[c_prio] + 1
    else:
        init_prio = g.p[c_prio] + 2

    b = expr2bdd(expr(False))
    for curr_prio in range(init_prio, min_prio - 1, - 2):
        u_p = u & g.sup_prio_expr(curr_prio, c_prio)
        u_p_bis = g.sup_prio_expr_even(curr_prio + 1, c_prio)
        p_safe_attr = attractors.p_safe_attractor(g, 1, u_p | b, u_p_bis & ~b)
        b = b | p_safe_attr
    return b


def lay_attr_full(g, q, u, max_prios):
    p = copy(max_prios)
    p_changed = True
    c = expr2bdd(expr(False))
    b = expr2bdd(expr(False))
    while p_changed:
        tau_e = compute_tau_ext(g, p)
        t = u
        for prio_f_index in range(g.k):
            t = t & g.em_vars[prio_f_index]
        t_bis = g.sup_one_prio_odd(max_prios)

        b = p_safe_attractor_full(g, 0, tau_e, t | c, t_bis & ~c)

        p_changed = False
        for c_prio in range(g.k):
            if p[c_prio] - 2 <= q[c_prio]:
                new_value = q[c_prio]
            else:
                new_value = p[c_prio] - 2
            if new_value != p[c_prio]:
                p_changed = True
            p[c_prio] = new_value
        new_c = c | b
        c = new_c
    return b.smoothing(g.em_vars)


def p_safe_attractor_full(g, i, tau_e, u, avoid):
    f_1 = (tau_e & u.compose(g.mapping_bis)) & ~avoid
    f_1 = f_1.smoothing(g.bis_vars + g.em_vars_bis)

    f_2 = tau_e & (~u).compose(g.mapping_bis)
    f_2 = (~f_2.smoothing(g.bis_vars + g.em_vars_bis)) & ~avoid
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (tau_e & attr_old.compose(g.mapping_bis)) & ~avoid
        f_1 = f_1.smoothing(g.bis_vars + g.em_vars_bis)

        f_2 = g.tau & (~attr_old).compose(g.mapping_bis)
        f_2 = (~f_2.smoothing(g.bis_vars + g.em_vars_bis)) & ~avoid
        if i == 0:
            f_1 = g.phi_0 & f_1
            f_2 = g.phi_1 & f_2
        else:
            f_1 = g.phi_1 & f_1
            f_2 = g.phi_0 & f_2

        attr_new = attr_old | f_1 | f_2
        if attr_new is attr_old:
            break
        attr_old = attr_new

    return attr_old
