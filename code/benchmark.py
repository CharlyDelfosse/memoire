from pyeda.inter import *
import copy
import math
from visualize_dot import run_graphviz

from game.generator import random_game
from game.generator_sr import random_game_sr
from game.visualizer import graphgame_viz
from game import timer

from psolvers import psolB, good_ep_solver, lay_solver, buchi_solver

from gen.generator_gen import random_game_gen
from gen.visualizer_gen import graphgame_viz_gen
from gen.ext_visualizer_gen import graphgame_viz_gen_ext
from gen.classical import classical_gen, classical_with_psolver
from psolvers_gen import buchi_solver_gen, good_ep_solver_gen, lay_solver_gen

import buchi
import zielonka


def test_par_algorithms():
    benchmark_configs = [[500, 5, 1, 5], [10, 5, 1, 5]]
    all_solvers = [buchi_solver.buchi_solver, psolB.psolB, good_ep_solver.good_ep_solver, lay_solver.lay_solver]
    n_games = 1
    for curr_config in benchmark_configs:
        tot_time = [0 for i in range(len(all_solvers)+1)]
        for curr_game_index in range(n_games):
            curr_game = random_game(curr_config[0], curr_config[1], curr_config[2], curr_config[3])
            chrono = timer.Timer(verbose=False)
            g_copy = curr_game.induced_game(curr_game.phi_0 | curr_game.phi_1)
            with chrono:
                (win_0, win_1) = zielonka.zielonka(g_copy)
            tot_time[0] = chrono.interval
            win_r_ref = (win_0, win_1)

            for curr_solver in range(len(all_solvers)):
                chrono = timer.Timer(verbose=False)
                with chrono:
                    (win_0, win_1) = zielonka.ziel_with_psolver(g_copy, all_solvers[curr_solver])
                tot_time[curr_solver+1] += chrono.interval
                assert win_0 is win_r_ref[0]
                assert win_1 is win_r_ref[1]

        avg_time = [x / n_games for x in tot_time]
        print("Config " + str(curr_config) + ": " + str(avg_time))

if __name__ == "__main__":
    test_par_algorithms()