from copy import copy

from attractors import attractors
from itertools import product
import dd.cudd as _bdd

def lay_solver_gen(bdd, g):
    if g.phi_0 | g.phi_1 == bdd.false:
        return bdd.false, bdd.false

    # Search for winning vertices for player 1
    for prio_f_index in range(g.k):
        if g.d[prio_f_index] % 2 == 1:
            init_prio = g.d[prio_f_index]
        else:
            init_prio = g.d[prio_f_index] - 1
        for min_prio in range(init_prio, -1, -2):
            w = lay_ep_1(bdd, g, min_prio, prio_f_index)
            if not w == bdd.false:
                x = attractors.attractor(bdd, g, 1, w)
                ind_game = g.induced_game(bdd, ~x)
                (z0, z1) = lay_solver_gen(bdd, ind_game)
                return z0, z1 | x

    # Search for winning vertices for player 0
    min_even_prio = [[] for _ in range(g.k)]
    for prio_f_index in range(g.k):
        if g.d[prio_f_index] % 2 == 0:
            init_prio = g.d[prio_f_index]
        else:
            init_prio = g.d[prio_f_index] - 1
        for curr_prio in range(init_prio, -1, -2):
            min_even_prio[prio_f_index].append(curr_prio)
    all_combinations = product(*min_even_prio)
    init_ext_game_infos(bdd, g)

    for comb in all_combinations:
        w = lay_ep_full_0(bdd, g, comb)
        if not w == bdd.false:
            x = attractors.attractor(bdd, g, 0, w)
            ind_game = g.induced_game(bdd, ~x)
            (z0, z1) = lay_solver_gen(bdd, ind_game)
            return z0 | x, z1

    return bdd.false, bdd.false


def init_ext_game_infos(bdd, g):
    em_vars_n = g.k
    g.em_vars = ['n{i}'.format(i=i) for i in range(em_vars_n)]
    g.em_vars_bis = ['n{i}_bis'.format(i=i) for i in range(em_vars_n)]
    em_mapping = dict(zip(g.em_vars, g.em_vars_bis))
    bdd.declare(*g.em_vars)
    bdd.declare(*g.em_vars_bis)
    g.mapping_bis.update(em_mapping)


def lay_ep_1(bdd, g, min_prio, c_prio_f):
    f_old = g.sup_prio_expr_odd(bdd, min_prio, c_prio_f)
    while True:
        lay_attr_f = lay_attr(bdd, g, min_prio, f_old, c_prio_f)
        f = f_old & lay_attr_f
        if f == f_old or f == bdd.false:
            break
        f_old = f
    return f


def lay_ep_full_0(bdd, g, q):
    max_prios = [0 for i in range(g.k)]
    for c_prio in range(g.k):
        if g.d[c_prio] % 2 == 1:
            max_prios[c_prio] = (g.d[c_prio] - 1)
        else:
            max_prios[c_prio] = (g.d[c_prio])
    f_old = g.sup_all_prio_even(bdd, q)
    while True:
        lay_attr_f = lay_attr_full(bdd, g, q, f_old, max_prios)

        f = f_old & lay_attr_f

        if f == f_old or f == bdd.false:
            break
        f_old = f
    return f


def compute_tau_ext(bdd, g, min_prios):
    res_expr = bdd.true

    for prio_f_index in range(g.k):
        # active in prec
        active_prio_1 = bdd.var(g.em_vars[prio_f_index])
        # active in current node
        active_prio_2 = bdd.let(g.mapping_bis, g.sup_prio_expr_even(bdd, min_prios[prio_f_index], prio_f_index))
        active_prio = active_prio_1 | active_prio_2

        res_expr = res_expr & (active_prio & bdd.var(g.em_vars_bis[prio_f_index]) | ~active_prio & ~bdd.var(
            g.em_vars_bis[prio_f_index]))

    return res_expr & g.tau


def lay_attr(bdd, g, min_prio, u, c_prio):
    if g.d[c_prio] % 2 == 0:
        init_prio = g.d[c_prio] + 1
    else:
        init_prio = g.d[c_prio] + 2

    b = bdd.false
    for curr_prio in range(init_prio, min_prio - 1, - 2):
        u_p = u & g.sup_prio_expr(bdd, curr_prio, c_prio)
        u_p_bis = g.sup_prio_expr_even(bdd, curr_prio + 1, c_prio)
        p_safe_attr = attractors.p_safe_attractor(bdd, g, 1, u_p | b, u_p_bis & ~b)
        b = b | p_safe_attr
    return b


def lay_attr_full(bdd, g, q, u, max_prios):
    p = copy(max_prios)
    p_changed = True
    c = bdd.false
    b = bdd.false
    while p_changed:
        tau_e = compute_tau_ext(bdd, g, p)
        t = u
        for prio_f_index in range(g.k):
            t = t & bdd.var(g.em_vars[prio_f_index])
        t_bis = g.sup_one_prio_odd(bdd, p)
        b = p_safe_attractor_full(bdd, g, 0, tau_e, t | c, t_bis & ~c)

        # For a vertice (v,n) check that n = N_p(v)
        id_prio_n = bdd.true
        for curr_f in range(g.k):
            greater_even_prio = g.sup_prio_expr_even(bdd, p[curr_f], curr_f)
            corr_n = greater_even_prio & bdd.var(g.em_vars[curr_f])
            not_corr_n = ~greater_even_prio & ~bdd.var(g.em_vars[curr_f])
            id_prio_n = id_prio_n & (corr_n | not_corr_n)

        b = b & id_prio_n
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
    return bdd.exist(g.em_vars, b)


def p_safe_attractor_full(bdd, g, i, tau_e, u, avoid):
    # Non-optimized code
    # f_1 = (tau_e & bdd.let(g.mapping_bis, u)) & ~avoid
    # f_1 = bdd.exist(g.bis_vars + g.em_vars_bis, f_1)
    f_1 = _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, u) & ~avoid, g.bis_vars + g.em_vars_bis)

    # Non-optimized code
    # f_2 = tau_e & bdd.let(g.mapping_bis, ~u)
    # f_2 = ~ bdd.exist(g.bis_vars + g.em_vars_bis, f_2) & ~avoid
    f_2 = ~_bdd.and_exists(tau_e, bdd.let(g.mapping_bis, ~u), g.bis_vars + g.em_vars_bis) & ~avoid

    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        # Non-optimized code
        # f_1 = (tau_e & bdd.let(g.mapping_bis, attr_old)) & ~avoid
        # f_1 = bdd.exist(g.bis_vars + g.em_vars_bis, f_1)
        f_1 = _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, attr_old) & ~avoid, g.bis_vars + g.em_vars_bis)

        # Non-optimized code
        # f_2 = tau_e & bdd.let(g.mapping_bis, ~(attr_old | u))
        # f_2 = ~ bdd.exist(g.bis_vars + g.em_vars_bis, f_2) & ~avoid
        f_2 = ~ _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, ~(attr_old | u)), g.bis_vars + g.em_vars_bis) & ~ avoid

        if i == 0:
            f_1 = g.phi_0 & f_1
            f_2 = g.phi_1 & f_2
        else:
            f_1 = g.phi_1 & f_1
            f_2 = g.phi_0 & f_2

        attr_new = attr_old | f_1 | f_2
        if attr_new == attr_old:
            break
        attr_old = attr_new

    return attr_old
