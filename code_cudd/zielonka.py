from attractors.attractors import attractor


def zielonka(bdd, g):
    if g.phi_0 == bdd.false & g.phi_1 == bdd.false:
        return bdd.false, bdd.false
    p_max, p_max_expr = g.get_max_prio(bdd)
    i = p_max % 2
    x = attractor(bdd, g, i, p_max_expr)
    g_bar = g.induced_game(bdd, ~x)

    (win_0, win_1) = zielonka(bdd, g_bar)
    if i == 0:
        win_i = win_0
        win_i_bis = win_1
    else:
        win_i = win_1
        win_i_bis = win_0
    if win_i_bis == bdd.false:
        if i == 0:
            return win_i | x, bdd.false
        else:
            return bdd.false, win_i | x
    else:
        x = attractor(bdd, g, 1 - i, win_i_bis)
        g_bar = g.induced_game(bdd, ~x)
        (win_0, win_1) = zielonka(bdd, g_bar)
        if i == 0:
            return win_0, win_1 | x
        else:
            return win_0 | x, win_1


def ziel_with_psolver(bdd, g, psolver):
    if g.phi_0 == bdd.false & g.phi_1 == bdd.false:
        return bdd.false, bdd.false
    (z_0, z_1) = psolver(bdd, g)
    if not (z_0 == bdd.false & z_1 == bdd.false):
        print("PSolver winning regions not empty")

    g_bar = g.induced_game(bdd, ~(z_0 | z_1))
    if (g_bar.phi_0 | g_bar.phi_1) == bdd.false:
        return z_0, z_1
    p_max, p_max_expr = g_bar.get_max_prio(bdd)
    i = p_max % 2
    x = attractor(bdd, g_bar, i, p_max_expr)
    g_ind = g_bar.induced_game(bdd, ~x)
    (win_0, win_1) = ziel_with_psolver(bdd, g_ind, psolver)
    if i == 0:
        win_i = win_0
        win_i_bis = win_1
    else:
        win_i = win_1
        win_i_bis = win_0
    if win_i_bis == bdd.false:
        if i == 0:
            return z_0 | win_i | x, z_1
        else:
            return z_0, z_1 | win_i | x
    else:
        x = attractor(bdd, g_bar, 1 - i, win_i_bis)
        g_ind = g_bar.induced_game(bdd, ~x)
        (win_0, win_1) = ziel_with_psolver(bdd, g_ind, psolver)
        if i == 0:
            return z_0 | win_0, z_1 | win_1 | x
        else:
            return z_0 | win_0 | x, z_1 | win_1