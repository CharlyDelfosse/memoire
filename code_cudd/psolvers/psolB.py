from attractors import attractors
from attractors.fatal_attractors import monotone_attractor


def psolB(bdd, g):
    for curr_p in range(0, g.d + 1):
        player = curr_p % 2
        x = g.gamma[curr_p] & (g.phi_0 | g.phi_1)
        f_old = bdd.false
        while not (x == bdd.false or x == f_old):
            f_old = x
            m_attr_x = monotone_attractor(bdd, g, player, x, curr_p)
            if (m_attr_x | x) == m_attr_x:
                attr_ma = attractors.attractor(bdd, g, player, m_attr_x)
                ind_game = g.induced_game(bdd, ~attr_ma)
                (w_0, w_1) = psolB(bdd, ind_game)
                if player == 0:
                    w_0 = w_0 | attr_ma
                else:
                    w_1 = w_1 | attr_ma
                return w_0, w_1
            else:
                x = x & m_attr_x

    return bdd.false, bdd.false