from pyeda.inter import *
from attractors.attractors import attractor, attractor_pos


def zielonka(g):

    if g.phi_0.is_zero() & g.phi_1.is_zero():
        return expr2bdd(expr(False)), expr2bdd(expr(False))
    p_max, p_max_expr = g.get_max_prio()
    i = p_max % 2
    print("Start zielonka")
    x = attractor(g, i, p_max_expr)
    print("Zielonka check")
    g_bar = g.induced_game(~x)

    (win_0, win_1) = zielonka(g_bar)
    if i == 0:
        win_i = win_0
        win_i_bis = win_1
    else:
        win_i = win_1
        win_i_bis = win_0
    if win_i_bis == expr2bdd(expr(False)):
        if i == 0:
            return win_i | x, expr2bdd(expr(False))
        else:
            return expr2bdd(expr(False)), win_i | x
    else:
        x = attractor(g, 1 - i, win_i_bis)
        g_bar = g.induced_game(~x)
        (win_0, win_1) = zielonka(g_bar)
        if i == 0:
            return win_0, win_1 | x
        else:
            return win_0 | x, win_1


def ziel_with_psolver(g, psolver):
    if g.phi_0.is_zero() & g.phi_1.is_zero():
        return expr2bdd(expr(False)), expr2bdd(expr(False))
    (z_0, z_1) = psolver(g)

    g_bar = g.induced_game(~(z_0 | z_1))
    if (g_bar.phi_0 | g_bar.phi_1).is_zero():
        return z_0, z_1
    p_max, p_max_expr = g_bar.get_max_prio()
    i = p_max % 2
    x = attractor(g_bar, i, p_max_expr)
    g_ind = g_bar.induced_game(~x)
    (win_0, win_1) = ziel_with_psolver(g_ind, psolver)
    if i == 0:
        win_i = win_0
        win_i_bis = win_1
    else:
        win_i = win_1
        win_i_bis = win_0
    if win_i_bis == expr2bdd(expr(False)):
        if i == 0:
            return z_0 | win_i | x, z_1
        else:
            return z_0, z_1 | win_i | x
    else:
        x = attractor(g_bar, 1 - i, win_i_bis)
        g_ind = g_bar.induced_game(~x)
        (win_0, win_1) = ziel_with_psolver(g_ind, psolver)
        if i == 0:
            return z_0 | win_0, z_1 | win_1 | x
        else:
            return z_0 | win_0 | x, z_1 | win_1
