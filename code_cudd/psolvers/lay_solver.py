from attractors import attractors


def lay_solver(bdd, g):
    for min_prio in range(g.d, -1, -1):
        i = min_prio % 2
        w = lay_ep(bdd, g, min_prio)
        if not w == bdd.false:
            x = attractors.attractor(bdd, g, i, w)
            ind_game = g.induced_game(bdd, ~x)
            (z_0, z_1) = lay_solver(bdd, ind_game)
            if i == 0:
                return z_0 | x, z_1
            else:
                return z_0, z_1 | x
    return bdd.false, bdd.false


def lay_ep(bdd, g, min_prio):
    if min_prio % 2 == 0:
        i = 0
        f_old = g.sup_prio_expr_even(bdd, min_prio)
    else:
        i = 1
        f_old = g.sup_prio_expr_odd(bdd, min_prio)
    while True:
        lay_attr_f = lay_attr(bdd, g, i, min_prio, f_old)
        f = f_old & lay_attr_f
        if f == f_old:
            break
        f_old = f
    return f


def lay_attr(bdd, g, i, min_prio, u):
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

    b = bdd.false
    for curr_prio in range(init_prio, min_prio - 1, - 2):
        u_p = u & g.sup_prio_expr(bdd, curr_prio)
        if i == 0:
            u_p_bis = g.sup_prio_expr_odd(bdd, curr_prio + 1)
        else:
            u_p_bis = g.sup_prio_expr_even(bdd, curr_prio + 1)

        p_safe_attr = attractors.p_safe_attractor(bdd, g, i, u_p | b, u_p_bis & ~b)
        b = b | p_safe_attr
    return b
