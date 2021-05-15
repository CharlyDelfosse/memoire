import dd.cudd as _bdd


def attractor(bdd, g, i, f):
    k = 0
    attr_old = f
    while True:
        # Code non-optimized
        # f_1 = g.tau & bdd.let(g.mapping_bis, attr_old)
        # f_1 = bdd.exist(g.bis_vars, f_1)
        f_1 = _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, attr_old), g.bis_vars)

        # Code non-optimized
        # f_2 = g.tau & bdd.let(g.mapping_bis, (~attr_old))
        # f_2 = ~(bdd.exist(g.bis_vars, f_2))

        f_2 = ~ _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, ~attr_old), g.bis_vars)

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

    # Code non-optimized
    # f_1 = (g.tau & bdd.let(g.mapping_bis, f))
    # f_1 = bdd.exist(g.bis_vars, f_1)
    f_1 = _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, f), g.bis_vars)

    # Code non-optimized
    # f_2 = g.tau & bdd.let(g.mapping_bis, ~f)
    # f_2 = ~(bdd.exist(g.bis_vars, f_2))
    f_2 = ~ _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, ~f), g.bis_vars)
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        # Code non-optimized
        # f_1 = (g.tau & bdd.let(g.mapping_bis, attr_old))
        # f_1 = (bdd.exist(g.bis_vars, f_1))
        f_1 = _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, attr_old), g.bis_vars)

        # Code non-optimized
        # f_2 = g.tau & bdd.let(g.mapping_bis, ~(attr_old | f))
        # f_2 = ~(bdd.exist(g.bis_vars, f_2))
        f_2 = ~ _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, ~(attr_old | f)), g.bis_vars)

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


def p_safe_attractor(bdd, g, i, u, avoid):
    # Code non-optimized
    # f_1 = (g.tau & bdd.let(g.mapping_bis, u)) & ~avoid
    # f_1 = bdd.exist(g.bis_vars, f_1)
    f_1 = _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, u) & ~ avoid, g.bis_vars)

    # Code non-optimized
    # f_2 = g.tau & bdd.let(g.mapping_bis, ~u)
    # f_2 = ~ bdd.exist(g.bis_vars, f_2) & ~ avoid
    f_2 = ~ _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, ~u), g.bis_vars) & ~avoid
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        # Code non-optimized
        # f_1 = g.tau & bdd.let(g.mapping_bis, attr_old) & ~avoid
        # f_1 = bdd.exist(g.bis_vars, f_1)
        f_1 = _bdd.and_exists(g.tau, bdd.let(g.mapping_bis, attr_old) & ~avoid, g.bis_vars)

        # Code non-optimized
        # f_2 = g.tau & bdd.let(g.mapping_bis, ~(attr_old | u))
        # f_2 = ~bdd.exist(g.bis_vars, f_2) & ~avoid
        f_2 = ~_bdd.and_exists(g.tau, bdd.let(g.mapping_bis, ~(attr_old | u)), g.bis_vars) & ~avoid

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

    return attr_old
