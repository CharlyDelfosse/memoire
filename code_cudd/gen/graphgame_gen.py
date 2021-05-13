import math
import copy
from collections import defaultdict


class GraphGame_gen:

    def __init__(self, bdd, n, d):
        self.k = len(d)
        self.n_vars = math.ceil(math.log(n, 2))
        self.q_vars = ['x' + str(i) for i in range(self.n_vars)]
        self.bis_vars = ['x_bis' + str(i) for i in range(self.n_vars)]
        self.g_vars = self.q_vars + self.bis_vars
        bdd.declare(*self.g_vars)
        self.d = d
        self.n = n

        self.mapping_bis = dict(zip(self.q_vars, self.bis_vars))

        self.phi_0 = bdd.false
        self.phi_1 = bdd.false
        self.tau = bdd.false
        self.gamma = [defaultdict(lambda: bdd.false) for _ in range(self.k)]

    def set_expr(self, phi_0, phi_1, tau, gamma):
        self.phi_0 = phi_0
        self.phi_1 = phi_1
        self.tau = tau
        self.gamma = gamma

    def induced_game(self, bdd, x):
        tau_bar = self.tau & x & bdd.let(self.mapping_bis, x)
        phi_0_bar = self.phi_0 & x
        phi_1_bar = self.phi_1 & x
        gamma_bar = [defaultdict(lambda: bdd.false) for _ in range(self.k)]

        for curr_f in range(self.k):
            for curr_p in range(self.d[curr_f] + 1):
                new_expr = self.gamma[curr_f][curr_p] & (phi_0_bar | phi_1_bar)
                if not new_expr == bdd.false:
                    gamma_bar[curr_f][curr_p] = new_expr

        new_game = GraphGame_gen(bdd, self.n, copy.deepcopy(self.d))
        new_game.set_expr(phi_0_bar, phi_1_bar, tau_bar, gamma_bar)

        return new_game

    # Return vertices with even priorities greater or equal than min_prio on dimension f_index
    def sup_prio_expr_even(self, bdd, min_prio, f_index):
        expr_res = bdd.false
        if min_prio % 2 == 0:
            init_prio = min_prio
        else:
            init_prio = min_prio + 1
        for curr_prio in range(init_prio, self.d[f_index] + 1, 2):
            expr_res = expr_res | self.gamma[f_index][curr_prio]
        return expr_res

    # Return vertices with a odd priority greater or equal than min_prios[l] in at least one dimension l
    def sup_one_prio_odd(self, bdd, min_prios):
        expr_res = bdd.false
        for prio_f_index in range(self.k):
            if min_prios[prio_f_index] % 2 == 0:
                init_prio = min_prios[prio_f_index] + 1
            else:
                init_prio = min_prios[prio_f_index]
            for curr_prio in range(init_prio, self.d[prio_f_index] + 1, 2):
                expr_res = expr_res | self.gamma[prio_f_index][curr_prio]
        return expr_res
