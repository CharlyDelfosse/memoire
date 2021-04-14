import math
import random
import copy
from pyeda.inter import *


def mapping2expr(p_vars, point):
    res_expr = expr2bdd(expr(True))
    for curr_var in p_vars:
        if point[curr_var] == 0:
            res_expr = res_expr & ~curr_var
        else:
            res_expr = res_expr & curr_var
    return res_expr


class GraphGame:

    def __init__(self, n, p):
        self.n_q_vars = math.ceil(math.log(n, 2))
        self.n_col_vars = math.ceil(math.log(p+1,2))
        self.n_vars = self.n_q_vars + self.n_col_vars

        self.q_vars = bddvars('x', (0, self.n_q_vars))
        self.col_vars = bddvars('x', (self.n_q_vars, self.n_vars))

        self.bis_q_vars = bddvars('x_bis', (0, self.n_q_vars))
        self.bis_col_vars = bddvars('x_bis', (self.n_q_vars, self.n_vars))

        self.g_vars = self.q_vars + self.col_vars + self.bis_q_vars + self.bis_col_vars
        self.bis_vars = self.bis_q_vars + self.bis_col_vars
        self.p = p
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

    def set_expr(self, phi_0, phi_1, tau):
        self.phi_0 = phi_0
        self.phi_1 = phi_1
        self.tau = tau

    def get_max_prio(self):
        curr_max = self.p
        q_expr = (self.phi_0 | self.phi_1)
        curr_max_bdd = q_expr & mapping2expr(self.col_vars,num2point(curr_max,self.col_vars))
        while curr_max_bdd.is_zero():
            curr_max = curr_max - 1
            curr_max_bdd = q_expr & mapping2expr(self.col_vars,num2point(curr_max,self.col_vars))
        return curr_max, curr_max_bdd

    def induced_game(self, x):
        tau_bar = self.tau & x & x.compose(self.mapping_bis)
        phi_0_bar = self.phi_0 & x
        phi_1_bar = self.phi_1 & x

        new_game = GraphGame(self.n, self.p)
        new_game.set_expr(phi_0_bar, phi_1_bar, tau_bar)

        return new_game