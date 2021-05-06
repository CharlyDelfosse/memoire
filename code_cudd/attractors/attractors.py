

def attractor(bdd, g, i, f):
    k = 0
    attr_old = f
    while True:
        f_1 = g.tau & bdd.let(g.mapping_bis, attr_old)
        f_2 = g.tau & bdd.let(g.mapping_bis,(~attr_old))
        f_1 = bdd.exist(g.bis_vars,f_1)
        f_2 = ~(bdd.exist(g.bis_vars, f_2))

        if i == 0:
            f_1 = g.phi_0 & f_1
            f_2 = g.phi_1 & f_2
        else:
            f_1 = g.phi_1 & f_1
            f_2 = g.phi_0 & f_2

        attr_new = attr_old | f_1 | f_2
        if attr_new == attr_old:
            break
        attr_old = attr_new
        k = k + 1
    return attr_old


def attractor_pos(bdd, g, i, f):
    k = 1
    f_1 = (g.tau & bdd.let(g.mapping_bis, f))
    f_1 = bdd.exist(g.bis_vars, f_1)

    f_2 = g.tau & bdd.let(g.mapping_bis, ~f)
    f_2 = ~(bdd.exist(g.bis_vars, f_2))
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (g.tau & bdd.let(g.mapping_bis, attr_old))
        f_1 = (bdd.exist(g.bis_vars, f_1))

        f_2 = g.tau & bdd.let(g.mapping_bis, ~attr_old)
        f_2 = ~(bdd.exist(g.bis_vars, f_2))

        if i == 0:
            f_1 = g.phi_0 & f_1
            f_2 = g.phi_1 & f_2
        else:
            f_1 = g.phi_1 & f_1
            f_2 = g.phi_0 & f_2

        attr_new = attr_old | f_1 | f_2
        if attr_new == attr_old:
            break
        attr_old = attr_new
        k = k + 1
    return attr_old


def recur(bdd, g, i, f):
    k = 0
    recur_old = f
    while True:
        f_1 = attractor_pos(bdd, g, i, recur_old)
        recur_new = f & f_1
        if recur_new == recur_old:
            break
        recur_old = recur_new
        k = k + 1
    return recur_old