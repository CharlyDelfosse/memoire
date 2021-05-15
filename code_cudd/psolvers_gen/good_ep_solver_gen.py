import math
from attractors import attractors
from utils import num_to_map
import dd.cudd as _bdd

def good_ep_solver_gen(bdd, g):
    init_ext_game_infos(bdd, g)
    return good_ep_solver_gen_r(bdd, g)


def init_ext_game_infos(bdd, g):
    m_vars = []
    m_vars_bis = []
    m_mapping = {}
    for prio_f_index in range(g.k):
        m_vars_n = math.ceil(math.log(g.d[prio_f_index] + 1, 2))

        curr_m_vars = ['m{f}_{i}'.format(f=prio_f_index, i=i) for i in range(m_vars_n)]
        curr_m_vars_bis = ['m{f}_{i}_bis'.format(f=prio_f_index, i=i) for i in range(m_vars_n)]

        m_vars.append(curr_m_vars)
        m_vars_bis.append(curr_m_vars_bis)
        bdd.declare(*curr_m_vars)
        bdd.declare(*curr_m_vars_bis)
        m_mapping.update(dict(zip(curr_m_vars, curr_m_vars_bis)))

    g.mapping_bis.update(m_mapping)
    g.m_vars = m_vars
    g.m_vars_bis = m_vars_bis


def good_ep_solver_gen_r(bdd, g):
    # Search for winning vertices for player 1
    for prio_f_index in range(g.k):
        c_tau_e = compute_tau_ext(bdd, g, prio_f_index)
        w = good_ep(bdd, g, 1, c_tau_e, prio_f_index)
        if not w == bdd.false:
            x = attractors.attractor(bdd, g, 1, w)
            ind_game = g.induced_game(bdd, ~x)
            ind_game.m_vars = g.m_vars
            ind_game.m_vars_bis = g.m_vars_bis
            ind_game.mapping_bis = g.mapping_bis
            (z0, z1) = good_ep_solver_gen_r(bdd, ind_game)
            return z0, z1 | x

    # Search for winning vertices for player 0
    tau_e = compute_full_tau_ext(bdd, g)
    w = good_ep_full(bdd, g, 0, tau_e)
    if not w == bdd.false:
        x = attractors.attractor(bdd, g, 0, w)
        ind_game = g.induced_game(bdd, ~x)
        ind_game.m_vars = g.m_vars
        ind_game.m_vars_bis = g.m_vars_bis
        ind_game.mapping_bis = g.mapping_bis
        (z0, z1) = good_ep_solver_gen_r(bdd, ind_game)
        return z0 | x, z1

    return bdd.false, bdd.false


def compute_tau_ext(bdd, g, prio_f_index):
    res_expr = bdd.false

    # Iterate over all vertices
    for curr_p in range(g.d[prio_f_index] + 1):
        # Mapping of current prio for m'
        curr_p_dict = num_to_map(curr_p, g.m_vars_bis[prio_f_index])
        curr_p_bdd = bdd.cube(curr_p_dict)

        # Iterate over all m value possible
        for curr_m in range(g.d[prio_f_index] + 1):
            curr_m_dict = num_to_map(curr_m, g.m_vars[prio_f_index])
            curr_m_bdd = bdd.cube(curr_m_dict)

            # Expression of (v,m)
            curr_expr = g.gamma[prio_f_index][curr_p] & curr_m_bdd

            # m' = max{m, P(v)}
            if curr_m > curr_p:
                curr_expr = curr_expr & bdd.let(g.mapping_bis, curr_m_bdd)
            else:
                curr_expr = curr_expr & curr_p_bdd
            res_expr = res_expr | curr_expr
    return res_expr & g.tau


def compute_full_tau_ext(bdd, g):
    res_expr = bdd.true
    for prio_f_index in range(g.k):

        prio_res_expr = bdd.false
        # Iterate over all vertices
        for curr_p in range(g.d[prio_f_index] + 1):
            # Mapping of current prio for m'
            curr_p_dict = num_to_map(curr_p, g.m_vars_bis[prio_f_index])
            curr_p_bdd = bdd.cube(curr_p_dict)

            # Iterate over all m value possible
            for curr_m in range(g.d[prio_f_index] + 1):
                curr_m_dict = num_to_map(curr_m, g.m_vars[prio_f_index])
                curr_m_bdd = bdd.cube(curr_m_dict)

                # Expression of (v,m)
                curr_expr = g.gamma[prio_f_index][curr_p] & curr_m_bdd

                # m' = max{m, P(v)}
                if curr_m > curr_p:
                    curr_expr = curr_expr & bdd.let(g.mapping_bis, curr_m_bdd)
                else:
                    curr_expr = curr_expr & curr_p_bdd
                prio_res_expr = prio_res_expr | curr_expr

        res_expr = res_expr & prio_res_expr
    res_expr = res_expr & g.tau
    return res_expr


def good_ep(bdd, g, i, tau_e, prio_f_index):
    f_old = g.phi_0 | g.phi_1
    while True:
        if i == 0:
            t = f_old & ~bdd.var(g.m_vars[prio_f_index][0])
        else:
            t = f_old & bdd.var(g.m_vars[prio_f_index][0])

        attr_t = attractor_pos_ext(bdd, g, i, t, tau_e, g.m_vars_bis[prio_f_index])
        f = f_old & attr_t

        # For a vertice (v,m) check that m = P(v)
        id_prio_m = bdd.false
        for curr_p in range(g.d[prio_f_index] + 1):
            curr_p_point = num_to_map(curr_p, g.m_vars[prio_f_index])
            curr_p_bdd = bdd.cube(curr_p_point)
            id_prio_m = id_prio_m | (g.gamma[prio_f_index][curr_p] & curr_p_bdd)

        # Non-optimized code
        # f = f & id_prio_m
        # f = bdd.exist(g.m_vars[prio_f_index], f)
        f = _bdd.and_exists(f, id_prio_m, g.m_vars[prio_f_index])

        if f == f_old:
            break
        f_old = f

    return f


def good_ep_full(bdd, g, i, tau_e):
    f_old = g.phi_0 | g.phi_1
    flat_m_vars_bis = [c_var for sublist in g.m_vars_bis for c_var in sublist]
    flat_m_vars = [c_var for sublist in g.m_vars for c_var in sublist]
    while True:
        t = f_old
        for prio_f_index in range(g.k):
            if i == 0:
                t = t & ~bdd.var(g.m_vars[prio_f_index][0])
            else:
                t = t & bdd.var(g.m_vars[prio_f_index][0])
        attr_t = attractor_pos_ext(bdd, g, i, t, tau_e, flat_m_vars_bis)
        f = f_old & attr_t
        # For a vertice (v,m_0, ..., m_k-1) check that m_l = P_l(v)
        id_prio_m = bdd.true
        for prio_f_index in range(g.k):
            curr_prio_m = bdd.false
            for curr_p in range(g.d[prio_f_index] + 1):
                curr_p_point = num_to_map(curr_p, g.m_vars[prio_f_index])
                curr_p_bdd = bdd.cube(curr_p_point)
                curr_prio_m = curr_prio_m | (g.gamma[prio_f_index][curr_p] & curr_p_bdd)
            id_prio_m = id_prio_m & curr_prio_m

        # Non-optimized code
        # f = f & id_prio_m
        # f = bdd.exist(flat_m_vars, f)
        f = _bdd.and_exists(f, id_prio_m, flat_m_vars)

        if f == f_old:
            break
        f_old = f
    return f


def attractor_pos_ext(bdd, g, i, f, tau_e, curr_m_vars_bis):
    # Non-optimized code
    # f_1 = (tau_e & bdd.let(g.mapping_bis, f))
    # f_1 = bdd.exist(g.bis_vars + curr_m_vars_bis, f_1)
    f_1 = _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, f), g.bis_vars + curr_m_vars_bis)

    # Non-optimized code
    # f_2 = tau_e & bdd.let(g.mapping_bis, ~f)
    # f_2 = ~(bdd.exist(g.bis_vars + curr_m_vars_bis, f_2))
    f_2 = ~ _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, ~f), g.bis_vars + curr_m_vars_bis)

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
        # f_1 = bdd.exist(g.bis_vars + curr_m_vars_bis, f_1)
        f_1 = _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, attr_old), g.bis_vars + curr_m_vars_bis)

        # Non-optimized code
        # f_2 = tau_e & bdd.let(g.mapping_bis, ~(attr_old | f))
        # f_2 = ~(bdd.exist(g.bis_vars + curr_m_vars_bis, f_2))
        f_2 = ~ _bdd.and_exists(tau_e, bdd.let(g.mapping_bis, ~(attr_old | f)), g.bis_vars + curr_m_vars_bis)

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
