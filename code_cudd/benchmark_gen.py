import timer
from gen import classical
from gen.generator_gen import random_game_gen
from psolvers_gen import buchi_solver_gen, good_ep_solver_gen, lay_solver_gen
import dd.cudd as _bdd


def test_par_algorithms():
    benchmark_configs = [[500, [3, 4], 1, 5], [500, [3, 4], 1, 100], [500, [3, 4], 5, 10], [500, [3, 4], 50, 250],
                         [500, [6, 7, 8, 9], 1, 5], [500, [6, 7, 8, 9], 1, 100], [500, [6, 7, 8, 9], 5, 10],
                         [500, [6, 7, 8, 9], 50, 250]]
    all_solvers = [buchi_solver_gen.buchi_solver_gen, good_ep_solver_gen.good_ep_solver_gen, lay_solver_gen.lay_solver_gen]
    n_games = 100
    for curr_config in benchmark_configs:
        tot_time = [0 for i in range(len(all_solvers) + 1)]
        tot_usefull_psolver = [0 for i in range(len(all_solvers))]
        for curr_game_index in range(n_games):
            bdd = _bdd.BDD(memory_estimate=2 * 2**30)
            # bdd.configure(reordering=True)
            curr_game = random_game_gen(bdd, curr_config[0], curr_config[1], curr_config[2], curr_config[3])
            g_copy = curr_game.induced_game(bdd, curr_game.phi_0 | curr_game.phi_1)
            chrono = timer.Timer(verbose=False)
            with chrono:
                (win_0, win_1) = classical.classical(bdd, g_copy)
            tot_time[0] += chrono.interval
            win_r_ref = (win_0, win_1)

            for curr_solver in range(len(all_solvers)):
                g_copy = curr_game.induced_game(bdd, curr_game.phi_0 | curr_game.phi_1)
                chrono = timer.Timer(verbose=False)
                with chrono:
                    (win_0, win_1, psolver_solved) = classical.classical_with_psolver(bdd, g_copy, all_solvers[curr_solver])
                tot_time[curr_solver + 1] += chrono.interval
                if psolver_solved:
                    tot_usefull_psolver[curr_solver] += 1
                assert win_0 == win_r_ref[0]
                assert win_1 == win_r_ref[1]

        avg_time = [x / n_games for x in tot_time]
        print("[Classical, BuchiSolver, GoodEpSolver, LaySolver]")
        print("Config " + str(curr_config) + ": " + str(avg_time))
        print("Number of times psolvers found solution : " + str(tot_usefull_psolver))


if __name__ == "__main__":
    test_par_algorithms()
