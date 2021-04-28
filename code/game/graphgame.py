import math

from pyeda.inter import *


class GraphGame:

    def __init__(self, n, d):
        self.n_vars = math.ceil(math.log(n, 2))
        self.q_vars = bddvars('x', (0, self.n_vars))
        self.bis_vars = bddvars('x_bis', (0, self.n_vars))
        self.g_vars = self.q_vars + self.bis_vars
        self.d = d
        self.n = n

        self.mapping_bis = {}
        for i in range(self.n_vars):
            self.mapping_bis[self.g_vars[i]] = self.g_vars[i + self.n_vars]

        self.mapping_inv = {}
        for i in range(self.n_vars):
            self.mapping_inv[self.g_vars[i + self.n_vars]] = self.g_vars[i]

        self.phi_0 = expr2bdd(expr(False))
        self.phi_1 = expr2bdd(expr(False))
        self.tau = expr2bdd(expr(False))
        self.gamma = expr2bdd(expr(False))

    def set_expr(self, phi_0, phi_1, tau, gamma):
        self.phi_0 = phi_0
        self.phi_1 = phi_1
        self.tau = tau
        self.gamma = gamma

    def get_max_prio(self):
        curr_max = self.d
        curr_max_bdd = self.gamma[curr_max]
        while curr_max_bdd.is_zero():
            curr_max = curr_max - 1
            curr_max_bdd = self.gamma[curr_max]
        return curr_max, curr_max_bdd

    def get_prio(self, node):
        curr_prio = 0
        while curr_prio <= self.d:
            if self.gamma[curr_prio] & node is self.gamma[curr_prio]:
                return curr_prio
            curr_prio += 1
        raise IndexError

    # Return the expression which is evaluate to True for vertices with priority less or equal than max_color
    def inf_prio_expr(self, max_prio):
        expr_res = expr2bdd(expr(False))
        for curr_prio in range(0, max_prio + 1):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    # Return the expression which is evaluate to True for vertices with prio greater or equal than min_color
    def sup_prio_expr(self, min_prio):
        expr_res = expr2bdd(expr(False))
        for curr_prio in range(min_prio, self.d + 1):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    def sup_prio_expr_odd(self, min_prio):
        expr_res = expr2bdd(expr(False))
        if min_prio % 2 == 0:
            init_prio = min_prio + 1
        else:
            init_prio = min_prio
        for curr_prio in range(init_prio, self.d + 1, 2):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    def sup_prio_expr_even(self, min_prio):
        expr_res = expr2bdd(expr(False))
        if min_prio % 2 == 0:
            init_prio = min_prio
        else:
            init_prio = min_prio + 1
        for curr_prio in range(init_prio, self.d + 1, 2):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    def induced_game(self, x):
        tau_bar = self.tau & x & x.compose(self.mapping_bis)
        phi_0_bar = self.phi_0 & x
        phi_1_bar = self.phi_1 & x
        gamma_bar = []

        for curr_p in range(self.d + 1):
            gamma_bar.append(self.gamma[curr_p] & (phi_0_bar | phi_1_bar))

        new_game = GraphGame(self.n, self.d)
        new_game.set_expr(phi_0_bar, phi_1_bar, tau_bar, gamma_bar)

        return new_game

