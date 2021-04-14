from pyeda.inter import *
from attractors import attractors


def buchi(g, i, f):
    return attractors.attractor(g, i, attractors.recur(g, i, f))


def buchi_inter_safety(g, i, f, s):
    attr_adv_f = attractors.attractor(g, 1 - i, s)
    g_bar = g.induced_game(~attr_adv_f)
    return buchi(g_bar, i, f)


def buchi_inter_cobuchi(g, i, f, s):
    current_game = g
    res = expr2bdd(expr(False))
    while True:
        win_i = buchi_inter_safety(current_game, i, f, s)
        if win_i.is_zero():
            break
        res = res | win_i
        attr_i_win_i = attractors.attractor(g, i, win_i)
        res = res | attr_i_win_i
        current_game = g.induced_game(~attr_i_win_i)
    return res


def buchi_gen(g, i, f):
    expr_res = expr2bdd(expr(True))
    for curr_target in f:
        expr_res = expr_res & buchi(g, i, curr_target)
    return expr_res


def buchi_inter_safety_gen(g, i, f, s):
    attr_adv_f = attractors.attractor(g, 1 - i, s)
    g_bar = g.induced_game(~attr_adv_f)
    return buchi_gen(g_bar, i, f)
