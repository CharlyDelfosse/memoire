import buchi


def buchi_solver(bdd, g):
    for curr_p in range(g.d + 1):
        i = curr_p % 2
        u = g.gamma[curr_p]
        u_bis = bdd.false
        for opp_prio in range(curr_p + 1, g.d + 1):
            if opp_prio % 2 == 1 - i:
                u_bis = u_bis | g.gamma[opp_prio]
        w = buchi.buchi_inter_cobuchi(bdd, g, i, u, u_bis)
        if not w == bdd.false:
            g_bar = g.induced_game(bdd, ~w)
            (z_0, z_1) = buchi_solver(bdd, g_bar)
            if i == 0:
                return z_0 | w, z_1
            else:
                return z_0, z_1 | w
    return bdd.false, bdd.false
