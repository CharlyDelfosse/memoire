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


def buchi_gen(bdd, g, i, f):
    expr_res = bdd.false
    for curr_target in f:
        expr_res = expr_res & buchi(bdd, g, i, curr_target)
    return expr_res


def buchi_inter_safety_gen(bdd, g, i, f, s):
    attr_adv_f = attractors.attractor(bdd, g, 1 - i, s)
    g_bar = g.induced_game(bdd, ~attr_adv_f)
    return buchi_gen(bdd, g_bar, i, f)