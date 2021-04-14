from pyeda.inter import *


def attractor(g, i, f):
    k = 0
    attr_old = f
    while True:
        f_1 = (g.tau & attr_old.compose(g.mapping_bis))
        f_1 = f_1.smoothing(g.bis_vars)

        f_2 = g.tau & (~attr_old).compose(g.mapping_bis)
        f_2 = ~(f_2.smoothing(g.bis_vars))

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
        k = k + 1
    return attr_old


def attractor_pos(g, i, f):
    k = 1
    f_1 = (g.tau & f.compose(g.mapping_bis))
    f_1 = f_1.smoothing(g.bis_vars)

    f_2 = g.tau & (~f).compose(g.mapping_bis)
    f_2 = ~(f_2.smoothing(g.bis_vars))
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (g.tau & attr_old.compose(g.mapping_bis))
        f_1 = f_1.smoothing(g.bis_vars)

        f_2 = g.tau & (~attr_old).compose(g.mapping_bis)
        f_2 = ~(f_2.smoothing(g.bis_vars))

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
        k = k + 1
    return attr_old


def recur(g, i, f):
    k = 0
    recur_old = f
    while True:
        f_1 = attractor_pos(g, i, recur_old)
        recur_new = f & f_1
        if recur_new is recur_old:
            break
        recur_old = recur_new
        k = k + 1
    return recur_old


def p_safe_attractor(g, i, u, avoid):
    f_1 = (g.tau & u.compose(g.mapping_bis)) & ~avoid
    f_1 = f_1.smoothing(g.bis_vars)

    f_2 = g.tau & (~u).compose(g.mapping_bis)
    f_2 = (~f_2.smoothing(g.bis_vars)) & ~avoid
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (g.tau & attr_old.compose(g.mapping_bis)) & ~avoid
        f_1 = f_1.smoothing(g.bis_vars)

        f_2 = g.tau & (~attr_old).compose(g.mapping_bis)
        f_2 = (~f_2.smoothing(g.bis_vars)) & ~avoid
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
        f_2 = ~f_2 & ~avoid
        f_2 = f_2.smoothing(g.bis_vars)

    return attr_old
