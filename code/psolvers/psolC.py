from pyeda.inter import *
from game.graphgame_sr import mapping2expr
import math
from attractors import attractors

def psolC(g):
    m_vars_n = math.ceil(math.log(g.p + 1, 2))
    m_vars = bddvars('m', (0, m_vars_n))
    m_vars_bis = bddvars('m_bis', (0, m_vars_n))

    m_mapping = {}
    for i in range(m_vars_n):
        m_mapping[m_vars[i]] = m_vars_bis[i]
    tot_mapping = g.mapping_bis
    tot_mapping.update(m_mapping)

    g.m_vars = m_vars
    g.m_vars_bis = m_vars_bis
    g.mapping_bis = tot_mapping

    return good_ep_solver(g)


def good_ep_solver(g):
    tau_e = compute_tau_ext(g)
    for i in [0, 1]:
        w = good_ep(g, i, tau_e)
        if not w.is_zero():
            x = attractors.attractor(g, i, w)
            ind_game = g.induced_game(~x)
            ind_game.m_vars = g.m_vars
            ind_game.m_vars_bis = g.m_vars_bis
            (win_0, win_1) = good_ep_solver(ind_game)

            if i == 0:
                return win_0 | x, win_1
            else:
                return win_0, win_1 | x

    return expr2bdd(expr(False)), expr2bdd(expr(False))


def compute_tau_ext(g):
    res_expr = expr2bdd(expr(False))
    for curr_p in range(g.p + 1):
        current_p_point = num2point(curr_p, g.m_vars_bis)
        current_p_bdd = mapping2expr(g.m_vars_bis, current_p_point)
        for curr_m_p in range(g.p + 1):
            current_m_p_point = num2point(curr_m_p, g.m_vars)
            current_m_p_bdd = mapping2expr(g.m_vars, current_m_p_point)

            curr_expr = g.gamma[curr_p] & current_m_p_bdd

            if curr_p == curr_m_p:
                curr_expr = curr_expr & current_p_bdd
                res_expr = res_expr | curr_expr
            elif curr_m_p > curr_p:
                curr_expr = curr_expr & current_m_p_bdd.compose(g.mapping_bis)
                res_expr = res_expr | curr_expr
            else:
                curr_expr = curr_expr & current_p_bdd
                res_expr = res_expr | curr_expr

    res_expr = res_expr & g.tau
    return res_expr


def good_ep(g, i, tau_e):
    f_old = g.phi_0 | g.phi_1
    while True:
        if i == 0:
            t = f_old & ~g.m_vars[0]
        else:
            t = f_old & g.m_vars[0]

        attr_t = attractor_pos_ext(g, i, t, tau_e)
        f = f_old & attr_t
        id_prio_m = expr2bdd(expr(False))
        for curr_p in range(g.p + 1):
            curr_p_point = num2point(curr_p, g.m_vars)
            curr_p_bdd = mapping2expr(g.m_vars, curr_p_point)
            id_prio_m = id_prio_m | (g.gamma[curr_p] & curr_p_bdd)
        f = f & id_prio_m
        f = f.smoothing(g.m_vars)
        if f is f_old:
            break
        f_old = f

    return f


def attractor_pos_ext(g, i, f, tau_e):
    f_1 = (tau_e & f.compose(g.mapping_bis))
    f_1 = f_1.smoothing(g.bis_vars + g.m_vars_bis)

    f_2 = tau_e & (~f).compose(g.mapping_bis)
    f_2 = ~(f_2.smoothing(g.bis_vars + g.m_vars_bis))
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (tau_e & attr_old.compose(g.mapping_bis))
        f_1 = f_1.smoothing(g.bis_vars + g.m_vars_bis)

        f_2 = tau_e & (~attr_old).compose(g.mapping_bis)
        f_2 = ~(f_2.smoothing(g.bis_vars + g.m_vars_bis))

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
