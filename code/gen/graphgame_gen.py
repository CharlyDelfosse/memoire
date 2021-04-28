import math
import copy
from pyeda.inter import *


class GraphGame_gen:

    def __init__(self, n, d):
        self.k = len(d)
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

        for prio_f_index in range(self.k):
            self.gamma[prio_f_index].append(expr2bdd(expr(False)))

    def induced_game(self, x):
        tau_bar = self.tau & x & x.compose(self.mapping_bis)
        phi_0_bar = self.phi_0 & x
        phi_1_bar = self.phi_1 & x
        gamma_bar = []

        for curr_k in range(self.k):
            curr_new_gamma = []
            for curr_p in range(self.d[curr_k] + 1):
                curr_new_gamma.append(self.gamma[curr_k][curr_p] & (phi_0_bar | phi_1_bar))
            gamma_bar.append(curr_new_gamma)

        new_game = GraphGame_gen(self.n, copy.copy(self.d))
        new_game.set_expr(phi_0_bar, phi_1_bar, tau_bar, gamma_bar)

        return new_game

    # Return the expression which is evaluate to True for vertices with prio greater or equal than min_prios in at least one dimension
    def sup_one_prio_odd(self, min_prios):
        expr_res = expr2bdd(expr(False))
        for prio_f_index in range(self.k):
            if min_prios[prio_f_index] % 2 == 0:
                init_prio = min_prios[prio_f_index] + 1
            else:
                init_prio = min_prios[prio_f_index]
            for curr_prio in range(init_prio, self.d[prio_f_index] + 1, 2):
                expr_res = expr_res | self.gamma[prio_f_index][curr_prio]
        return expr_res

    # Return the expression which is evaluate to True for vertices with prio greater or equal than min_prios in all dimensions
    def sup_all_prio(self, min_prios):
        expr_res = expr2bdd(expr(True))
        for prio_f_index in range(self.k):
            curr_expr = expr2bdd(expr(False))
            for curr_prio in range(min_prios[prio_f_index], self.d[prio_f_index] + 1):
                curr_expr = curr_expr | self.gamma[prio_f_index][curr_prio]
            expr_res = expr_res & curr_expr
        return expr_res

    def sup_all_prio_even(self, min_prios):
        expr_res = expr2bdd(expr(True))
        for prio_f_index in range(self.k):
            curr_expr = expr2bdd(expr(False))
            if min_prios[prio_f_index] % 2 == 0:
                init_prio = min_prios[prio_f_index]
            else:
                init_prio = min_prios[prio_f_index] + 1
            for curr_prio in range(init_prio, self.d[prio_f_index] + 1):
                curr_expr = curr_expr | self.gamma[prio_f_index][curr_prio]
            expr_res = expr_res & curr_expr
        return expr_res


    # Return the expression which is evaluate to True for vertices with prio greater or equal than min_prio in dimension prio_f_index
    def sup_prio_expr(self, min_prio, prio_f_index):
        expr_res = expr2bdd(expr(False))
        for curr_prio in range(min_prio, self.d[prio_f_index] + 1, 1):
            expr_res = expr_res | self.gamma[prio_f_index][curr_prio]
        return expr_res


    def sup_prio_expr_odd(self, min_prio, prio_f_index):
        expr_res = expr2bdd(expr(False))
        if min_prio % 2 == 0:
            init_prio = min_prio + 1
        else:
            init_prio = min_prio
        for curr_prio in range(init_prio, self.d[prio_f_index] + 1, 2):
            expr_res = expr_res | self.gamma[prio_f_index][curr_prio]
        return expr_res

    def sup_prio_expr_even(self, min_prio, prio_f_index):
        expr_res = expr2bdd(expr(False))
        if min_prio % 2 == 0:
            init_prio = min_prio
        else:
            init_prio = min_prio + 1
        for curr_prio in range(init_prio, self.d[prio_f_index] + 1, 2):
            expr_res = expr_res | self.gamma[prio_f_index][curr_prio]
        return expr_res
