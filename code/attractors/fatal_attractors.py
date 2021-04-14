

def monotone_attractor(g, i, f, d):
    inf_col_expr = g.inf_prio_expr(d)

    k = 1
    f_1 = (g.tau & f.compose(g.mapping_bis))
    f_1 = f_1.smoothing(g.bis_vars) & inf_col_expr

    f_2 = g.tau & (~f).compose(g.mapping_bis)
    f_2 = ~(f_2.smoothing(g.bis_vars)) & inf_col_expr
    if i == 0:
        f_1 = g.phi_0 & f_1
        f_2 = g.phi_1 & f_2
    else:
        f_1 = g.phi_1 & f_1
        f_2 = g.phi_0 & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = (g.tau & attr_old.compose(g.mapping_bis))
        f_1 = f_1.smoothing(g.bis_vars) & inf_col_expr

        f_2 = g.tau & (~attr_old).compose(g.mapping_bis)
        f_2 = ~(f_2.smoothing(g.bis_vars)) & inf_col_expr

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