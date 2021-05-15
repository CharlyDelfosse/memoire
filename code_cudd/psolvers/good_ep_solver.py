import math
from attractors import attractors
from utils import num_to_map
import dd.cudd as _bdd

def good_ep_solver(bdd, g):
    init_ext_game_infos(bdd, g)
    (w0, w1) = good_ep_solver_r(bdd, g)
    return w0, w1


def init_ext_game_infos(bdd, g):
    m_vars_n = math.ceil(math.log(g.d + 1, 2))
    m_vars = ['m' + str(i) for i in range(m_vars_n)]
    m_vars_bis = ['m_bis' + str(i) for i in range(m_vars_n)]
    new_m_vars = m_vars + m_vars_bis
    bdd.declare(*new_m_vars)

    m_mapping = {}
    for i in range(m_vars_n):
        m_mapping[m_vars[i]] = m_vars_bis[i]
    tot_mapping = g.mapping_bis
    tot_mapping.update(m_mapping)

    g.m_vars = m_vars
    g.m_vars_bis = m_vars_bis
    g.mapping_bis = tot_mapping


def good_ep_solver_r(bdd, g):
    tau_e = compute_tau_ext(bdd, g)
    for i in [0, 1]:
        w = good_ep(bdd, g, i, tau_e)
        if not w == bdd.false:
            x = attractors.attractor(bdd, g, i, w)
            ind_game = g.induced_game(bdd, ~x)
            ind_game.m_vars = g.m_vars
            ind_game.m_vars_bis = g.m_vars_bis
            ind_game.mapping_bis = g.mapping_bis
            (win_0, win_1) = good_ep_solver_r(bdd, ind_game)

            if i == 0:
                return win_0 | x, win_1
            else:
                return win_0, win_1 | x

    return bdd.false, bdd.false


def compute_tau_ext(bdd, g):
    res_expr = bdd.false

    # Iterate over all vertices
    for curr_p in range(g.d + 1):
        # Mapping of current prio for m'
        curr_p_dict = num_to_map(curr_p, g.m_vars_bis)
        curr_p_bdd = bdd.cube(curr_p_dict)

        # Iterate over all m value possible
        for curr_m in range(g.d + 1):
            curr_m_dict = num_to_map(curr_m, g.m_vars)
            curr_m_bdd = bdd.cube(curr_m_dict)

            # Expression of (v,m)
            curr_expr = g.gamma[curr_p] & curr_m_bdd

            # m' = max{m, P(v)}
            if curr_m > curr_p:
                curr_expr = curr_expr & bdd.let(g.mapping_bis, curr_m_bdd)
                res_expr = res_expr | curr_expr
            else:
                curr_expr = curr_expr & curr_p_bdd
                res_expr = res_expr | curr_expr

    return res_expr & g.tau


def good_ep(bdd, g, i, tau_e):
    f_old = g.phi_0 | g.phi_1
    while True:
        if i == 0:
            t = f_old & ~bdd.var(g.m_vars[0])
        else:
            t = f_old & bdd.var(g.m_vars[0])

        attr_t = attractor_pos_ext(bdd, g, i, t, tau_e)
        f = f_old & attr_t

        # For a vertice (v,m) check that m = P(v)
        id_prio_m = bdd.false
        for curr_p in range(g.d + 1):
            curr_p_point = num_to_map(curr_p, g.m_vars)
            curr_p_bdd = bdd.cube(curr_p_point)
            id_prio_m = id_prio_m | (g.gamma[curr_p] & curr_p_bdd)

        # Non-optimized code
        # f = f & id_prio_m
        # f = bdd.exist(g.m_vars, f)
        f = _bdd.and_exists(f, id_prio_m, g.m_vars)

        if f == f_old:
            break
        f_old = f

    return f


def attractor_pos_ext(bdd, g, i, f, tau_e):
    # Non-optimized code
    # f_1 = (tau_e & bdd.let(g.mapping_bis, f))
    # f_1 = bdd.exist(g.bis_vars + g.m_vars_bis, f_1)
    f_1 = _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, f), g.bis_vars + g.m_vars_bis)

    # Non-optimized code
    # f_2 = tau_e & bdd.let(g.mapping_bis, ~f)
    # f_2 = ~(bdd.exist(g.bis_vars + g.m_vars_bis, f_2))
    f_2 = ~ _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, ~f), g.bis_vars + g.m_vars_bis)

    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        # Non-optimized code
        # f_1 = tau_e & bdd.let(g.mapping_bis, attr_old)
        # f_1 = bdd.exist(g.bis_vars + g.m_vars_bis, f_1)
        f_1 = _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, attr_old), g.bis_vars + g.m_vars_bis)

        # Non-optimized code
        # f_2 = tau_e & bdd.let(g.mapping_bis, ~(attr_old | f))
        # f_2 = ~(bdd.exist(g.bis_vars + g.m_vars_bis, f_2))
        f_2 = ~ _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, ~(attr_old | f)), g.bis_vars + g.m_vars_bis)

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
