from pyeda.inter import *
import buchi


def buchi_solver(g):
    for curr_p in range(g.p + 1):
        i = curr_p % 2
        u = g.gamma[curr_p]
        u_bis = expr2bdd(expr(False))
        for opp_prio in range(curr_p + 1, g.p + 1):
            if opp_prio % 2 == 1 - i:
                u_bis = u_bis | g.gamma[opp_prio]
        w = buchi.buchi_inter_cobuchi(g, i, u, u_bis)
        if not w.is_zero():
            g_bar = g.induced_game(~w)
            (z_0, z_1) = buchi_solver(g_bar)
            if i == 0:
                return z_0 | w, z_1
            else:
                return z_0, z_1 | w
    return expr2bdd(expr(False)), expr2bdd(expr(False))


