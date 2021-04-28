from attractors import attractors
from pyeda.inter import *


def lay_solver(g):
    for min_prio in range(g.d, -1, -1):
        i = min_prio % 2
        w = lay_ep(g, min_prio)
        if not w.is_zero():
            x = attractors.attractor(g, i, w)
            ind_game = g.induced_game(~x)
            (z_0, z_1) = lay_solver(ind_game)
            if i == 0:
                return z_0 | x, z_1
            else:
                return z_0, z_1 | x
    return expr2bdd(expr(False)), expr2bdd(expr(False))


def lay_ep(g, min_prio):
    if min_prio % 2 == 0:
        i = 0
        f_old = g.sup_prio_expr_even(min_prio)
    else:
        i = 1
        f_old = g.sup_prio_expr_odd(min_prio)
    while True:
        lay_attr_f = lay_attr(g, i, min_prio, f_old)
        f = f_old & lay_attr_f
        if f is f_old:
            break
        f_old = f
    return f


def lay_attr(g, i, min_prio, u):
    if i == 0:
        if g.d % 2 == 0:
            init_prio = g.d + 2
        else:
            init_prio = g.d + 1
    else:
        if g.d % 2 == 0:
            init_prio = g.d + 1
        else:
            init_prio = g.d + 2

    b = expr2bdd(expr(False))
    for curr_prio in range(init_prio, min_prio - 1, - 2):
        u_p = u & g.sup_prio_expr(curr_prio)
        if i == 0:
            u_p_bis = g.sup_prio_expr_odd(curr_prio + 1)
        else:
            u_p_bis = g.sup_prio_expr_even(curr_prio + 1)

        p_safe_attr = attractors.p_safe_attractor(g, i, u_p | b, u_p_bis & ~b)
        b = b | p_safe_attr
    return b
