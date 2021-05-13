from attractors import attractors


def buchi(bdd, g, i, f):
    return attractors.attractor(bdd, g, i, attractors.recur(bdd, g, i, f))


def buchi_inter_safety(bdd, g, i, f, s):
    attr_adv_f = attractors.attractor(bdd, g, 1 - i, s)
    g_bar = g.induced_game(bdd, ~attr_adv_f)
    return buchi(bdd, g_bar, i, f)


def buchi_inter_cobuchi(bdd, g, i, f, s):
    win_i = buchi_inter_safety(bdd, g, i, f, s)
    attr_i_win_i = attractors.attractor(bdd, g, i, win_i)
    return attr_i_win_i


# Return winning regions in a game with a generalized Buchi objective for player 0
def buchi_gen(bdd, g, f):
    g_copy = g.induced_game(bdd, g.phi_0 | g.phi_1)
    while True:
        for curr_f in range(g.k):
            b0 = attractors.attractor(bdd, g_copy, 0, f[curr_f])
            not_b0 = (g_copy.phi_0 | g_copy.phi_1) & ~b0
            if not not_b0 == bdd.false:
                break
        b1 = attractors.attractor(bdd, g_copy, 1, not_b0)
        if b1 == bdd.false:
            break
        not_b1 = ~b1
        g_copy = g_copy.induced_game(bdd, not_b1)

    return g_copy.phi_0 | g_copy.phi_1


# Return winning regions in a game with a conjunction of a generalized Buchi objective
# and a safety objective for player 0
def buchi_inter_safety_gen(bdd, g, f, s):
    attr_adv_f = attractors.attractor(bdd, g, 1, s)
    g_bar = g.induced_game(bdd, ~attr_adv_f)
    return buchi_gen(bdd, g_bar, f)
