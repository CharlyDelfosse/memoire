from pyeda.inter import *
from game.graphgame_sr import mapping2expr
import math
from attractors import attractors


def good_ep_solver_gen(g):
    init_ext_game_infos(g)
    return good_ep_solver_gen_r(g)

def init_ext_game_infos(g):
    m_vars = []
    m_vars_bis = []
    m_mapping = {}
    for prio_f_index in range(g.k):
        m_vars_n = math.ceil(math.log(g.d[prio_f_index] + 1, 2))

        curr_m_vars = bddvars('m' + str(prio_f_index), (0, m_vars_n))
        curr_m_vars_bis = bddvars('m_bis' + str(prio_f_index), (0, m_vars_n))

        m_vars.append(curr_m_vars)
        m_vars_bis.append(curr_m_vars_bis)

        for i in range(m_vars_n):
            m_mapping[curr_m_vars[i]] = curr_m_vars_bis[i]

    tot_mapping = g.mapping_bis
    tot_mapping.update(m_mapping)

    g.m_vars = m_vars
    g.m_vars_bis = m_vars_bis
    g.mapping_bis = tot_mapping

def good_ep_solver_gen_r(g):
    for prio_f_index in range(g.k):
        c_tau_e = compute_tau_ext(g, prio_f_index)
        w = good_ep(g, 1, c_tau_e, prio_f_index)
        if not w.is_zero():
            x = attractors.attractor(g, 1, w)
            ind_game = g.induced_game(~x)
            ind_game.m_vars = g.m_vars
            ind_game.m_vars_bis = g.m_vars_bis
            ind_game.mapping_bis = g.mapping_bis
            (z0, z1) = good_ep_solver_gen_r(ind_game)
            return z0, z1 | x
    tau_e = compute_full_tau_ext(g)
    w = good_ep_full(g, 0, tau_e)
    if not w.is_zero():
        x = attractors.attractor(g, 0, w)
        ind_game = g.induced_game(~x)
        ind_game.m_vars = g.m_vars
        ind_game.m_vars_bis = g.m_vars_bis
        ind_game.mapping_bis = g.mapping_bis
        (z0, z1) = good_ep_solver_gen_r(ind_game)
        return z0 | x, z1

    return expr2bdd(expr(False)), expr2bdd(expr(False))


def compute_tau_ext(g, c_prio):
    res_expr = expr2bdd(expr(False))

    for curr_p in range(g.d[c_prio] + 1):
        current_p_point = num2point(curr_p, g.m_vars_bis[c_prio])
        current_p_bdd = mapping2expr(g.m_vars_bis[c_prio], current_p_point)
        for curr_m_p in range(g.d[c_prio] + 1):
            current_m_p_point = num2point(curr_m_p, g.m_vars[c_prio])
            current_m_p_bdd = mapping2expr(g.m_vars[c_prio], current_m_p_point)
            curr_expr = g.gamma[c_prio][curr_p] & current_m_p_bdd
            if curr_p == curr_m_p:
                curr_expr = curr_expr & current_p_bdd
            elif curr_m_p > curr_p:
                curr_expr = curr_expr & current_m_p_bdd.compose(g.mapping_bis)
            else:
                curr_expr = curr_expr & current_p_bdd
            res_expr = res_expr | curr_expr
    res_expr = res_expr & g.tau
    return res_expr


def compute_full_tau_ext(g):
    res_expr = expr2bdd(expr(True))
    for prio_f_index in range(g.k):
        prio_res_expr = expr2bdd(expr(False))
        for curr_p in range(g.d[prio_f_index] + 1):
            current_p_point = num2point(curr_p, g.m_vars_bis[prio_f_index])
            current_p_bdd = mapping2expr(g.m_vars_bis[prio_f_index], current_p_point)
            for curr_m_p in range(g.d[prio_f_index] + 1):
                current_m_p_point = num2point(curr_m_p, g.m_vars[prio_f_index])
                current_m_p_bdd = mapping2expr(g.m_vars[prio_f_index], current_m_p_point)
                curr_expr = g.gamma[prio_f_index][curr_p] & current_m_p_bdd
                if curr_p == curr_m_p:
                    curr_expr = curr_expr & current_p_bdd
                elif curr_m_p > curr_p:
                    curr_expr = curr_expr & current_m_p_bdd.compose(g.mapping_bis)
                else:
                    curr_expr = curr_expr & current_p_bdd
                prio_res_expr = prio_res_expr | curr_expr
        res_expr = res_expr & prio_res_expr
    res_expr = res_expr & g.tau
    return res_expr


def good_ep(g, i, tau_e, c_prio):
    f_old = g.phi_0 | g.phi_1
    while True:
        if i == 0:
            t = f_old & ~g.m_vars[c_prio][0]
        else:
            t = f_old & g.m_vars[c_prio][0]
        attr_t = attractor_pos_ext(g, i, t, tau_e, g.m_vars_bis[c_prio])

        f = f_old & attr_t
        id_prio_m = expr2bdd(expr(False))
        for curr_p in range(g.d[c_prio] + 1):
            curr_p_point = num2point(curr_p, g.m_vars[c_prio])
            curr_p_bdd = mapping2expr(g.m_vars[c_prio], curr_p_point)
            id_prio_m = id_prio_m | (g.gamma[c_prio][curr_p] & curr_p_bdd)
        f = f & id_prio_m

        f = f.smoothing(g.m_vars[c_prio])

        if f is f_old:
            break
        f_old = f

    return f


def good_ep_full(g, i, tau_e):
    f_old = g.phi_0 | g.phi_1
    flat_m_vars_bis = [c_var for sublist in g.m_vars_bis for c_var in sublist]
    flat_m_vars_bis = farray(flat_m_vars_bis)
    while True:
        t = f_old
        for prio_f_index in range(g.k):
            if i == 0:
                t = t & ~g.m_vars[prio_f_index][0]
            else:
                t = t & g.m_vars[prio_f_index][0]
        attr_t = attractor_pos_ext(g, i, t, tau_e, flat_m_vars_bis)
        f = f_old & attr_t
        #Ensure that a vertice with no predecessor have a correct m
        id_prio_m = expr2bdd(expr(False))
        for prio_f_index in range(g.k):
            curr_prio_m = expr2bdd(expr(False))
            for curr_p in range(g.d[prio_f_index] + 1):
                curr_p_point = num2point(curr_p, g.m_vars[prio_f_index])
                curr_p_bdd = mapping2expr(g.m_vars[prio_f_index], curr_p_point)
                curr_prio_m = curr_prio_m | (g.gamma[prio_f_index][curr_p] & curr_p_bdd)
            id_prio_m = id_prio_m & curr_prio_m
        f = f & id_prio_m
        f = f.smoothing(flat_m_vars_bis)
        if f is f_old:
            break
        f_old = f

    return f


def attractor_pos_ext(g, i, f, tau_e, flat_m_vars_bis):
    f_1 = (tau_e & f.compose(g.mapping_bis))
    f_1 = f_1.smoothing(g.bis_vars + flat_m_vars_bis)

    f_2 = tau_e & (~f).compose(g.mapping_bis)
    f_2 = ~(f_2.smoothing(g.bis_vars + flat_m_vars_bis))
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (tau_e & attr_old.compose(g.mapping_bis))
        f_1 = f_1.smoothing(g.bis_vars + flat_m_vars_bis)

        f_2 = tau_e & (~attr_old).compose(g.mapping_bis)
        f_2 = ~(f_2.smoothing(g.bis_vars + flat_m_vars_bis))

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
