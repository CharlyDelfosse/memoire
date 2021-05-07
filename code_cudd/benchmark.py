import timer
import zielonka
from game.generator import random_game
from psolvers import buchi_solver, good_ep_solver, lay_solver, psolB
import dd.cudd as _bdd


def test_par_algorithms():
    benchmark_configs = [[500, 5, 1, 5], [500, 5, 1, 100], [500, 5, 5, 10], [500, 5, 50, 250], [500, 50, 1, 5],
                         [500, 50, 1, 100], [500, 50, 5, 10], [500, 50, 50, 250]]
    all_solvers = [buchi_solver.buchi_solver, psolB.psolB, good_ep_solver.good_ep_solver, lay_solver.lay_solver]
    n_games = 100
    for curr_config in benchmark_configs:
        tot_time = [0 for i in range(len(all_solvers) + 1)]
        tot_usefull_psolver = [0 for i in range(len(all_solvers))]
        for curr_game_index in range(n_games):
            bdd = _bdd.BDD()
            curr_game = random_game(bdd, curr_config[0], curr_config[1], curr_config[2], curr_config[3])
            g_copy = curr_game.induced_game(bdd, curr_game.phi_0 | curr_game.phi_1)
            chrono = timer.Timer(verbose=False)
            with chrono:
                (win_0, win_1) = zielonka.zielonka(bdd, g_copy)
            tot_time[0] += chrono.interval
            win_r_ref = (win_0, win_1)

            for curr_solver in range(len(all_solvers)):
                g_copy = curr_game.induced_game(bdd, curr_game.phi_0 | curr_game.phi_1)
                chrono = timer.Timer(verbose=False)
                with chrono:
                    (win_0, win_1, psolver_solved) = zielonka.ziel_with_psolver(bdd, g_copy, all_solvers[curr_solver])
                tot_time[curr_solver + 1] += chrono.interval
                if psolver_solved:
                    tot_usefull_psolver[curr_solver] += 1
                assert win_0 == win_r_ref[0]
                assert win_1 == win_r_ref[1]

        avg_time = [x / n_games for x in tot_time]
        print("Config " + str(curr_config) + ": " + str(avg_time))
        print("Number of times psolvers found solution : " + str(tot_usefull_psolver))


if __name__ == "__main__":
    test_par_algorithms()
