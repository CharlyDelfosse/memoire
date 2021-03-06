import math


class GraphGame:

    def __init__(self, bdd, n, d):
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
        self.gamma = bdd.false

    def set_expr(self, phi_0, phi_1, tau, gamma):
        self.phi_0 = phi_0
        self.phi_1 = phi_1
        self.tau = tau
        self.gamma = gamma

    def get_max_prio(self, bdd):
        curr_max = self.d
        curr_max_bdd = self.gamma[curr_max]
        while curr_max_bdd == bdd.false:
            curr_max = curr_max - 1
            curr_max_bdd = self.gamma[curr_max]
        return curr_max, curr_max_bdd

    def induced_game(self, bdd, x):
        tau_bar = self.tau & x & bdd.let(self.mapping_bis, x)
        phi_0_bar = self.phi_0 & x
        phi_1_bar = self.phi_1 & x
        gamma_bar = []

        for curr_p in range(self.d + 1):
            gamma_bar.append(self.gamma[curr_p] & (phi_0_bar | phi_1_bar))

        new_game = GraphGame(bdd, self.n, self.d)
        new_game.set_expr(phi_0_bar, phi_1_bar, tau_bar, gamma_bar)

        return new_game

    # Return the expression which is evaluate to True for vertices with priority less or equal than max_color
    def inf_prio_expr(self, bdd, max_prio):
        expr_res = bdd.false
        for curr_prio in range(0, max_prio + 1):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    # Return the expression which is evaluate to True for vertices with prio greater or equal than min_color
    def sup_prio_expr(self, bdd, min_prio):
        expr_res = bdd.false
        for curr_prio in range(min_prio, self.d + 1):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    def sup_prio_expr_odd(self, bdd, min_prio):
        expr_res = bdd.false
        if min_prio % 2 == 0:
            init_prio = min_prio + 1
        else:
            init_prio = min_prio
        for curr_prio in range(init_prio, self.d + 1, 2):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res

    def sup_prio_expr_even(self, bdd, min_prio):
        expr_res = bdd.false
        if min_prio % 2 == 0:
            init_prio = min_prio
        else:
            init_prio = min_prio + 1
        for curr_prio in range(init_prio, self.d + 1, 2):
            expr_res = expr_res | self.gamma[curr_prio]
        return expr_res
