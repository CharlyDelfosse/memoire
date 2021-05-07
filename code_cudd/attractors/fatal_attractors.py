def monotone_attractor(bdd, g, i, f, d):
    inf_col_expr = g.inf_prio_expr(bdd, d)

    f_1 = g.tau & bdd.let(g.mapping_bis, f)
    f_1 = bdd.exist(g.bis_vars, f_1) & inf_col_expr

    f_2 = g.tau & bdd.let(g.mapping_bis, ~f)
    f_2 = ~ bdd.exist(g.bis_vars, f_2) & inf_col_expr

    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = g.tau & bdd.let(g.mapping_bis, attr_old)
        f_1 = bdd.exist(g.bis_vars, f_1) & inf_col_expr

        f_2 = g.tau & bdd.let(g.mapping_bis, ~ attr_old)
        f_2 = ~ bdd.exist(g.bis_vars, f_2) & inf_col_expr

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
