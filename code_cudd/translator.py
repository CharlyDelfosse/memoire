from game.graphgame import GraphGame

def pg2bdd(input_path, bdd):
    """
    input_path: path of the .pg file
    bdd: empty bdd passed as input
    """
    with open(input_path, "r") as gpg:
        first_line = gpg.readline() # first line has special info
        infos = first_line.rstrip().split(" ")
        nbr_nodes = int(infos[1][:-1]) # remove trailing ; (btw this format is not correct)

        # init game info

        game_infos = GraphGame(bdd, nbr_nodes, nbr_nodes) # should check what the max prio is, in my example n = p

        # init bdds for V0, V1, priorities and successors
        phi_0 = bdd.false
        phi_1 = bdd.false
        gamma = [bdd.false for _ in range(game_infos.d + 1)]
        tau = bdd.false

        # all nodes (all valuations of the vars)
        all_nodes = []
        all_possiblities = list(bdd.pick_iter(bdd.true, game_infos.q_vars))

        # iterate over nodes
        for line in gpg:
            infos = line.rstrip().split(" ")
            node_index = int(infos[0]) # TODO check if indexing starts at 0 or 1
            node_priorities = [int(prio) for prio in infos[1] if prio.isdigit()] # in case of pg, there is only 1 value, this line applies well to gpg
            node_player = int(infos[2])

            # current bdd for the node
            current_node_dict = all_possiblities[node_index]
            current_node_bdd = bdd.cube(current_node_dict)

            # add node to the formula for given color
            gamma[node_priorities[0]] = gamma[node_priorities[0]] | current_node_bdd

            # add current node to all nodes
            all_nodes.append(current_node_bdd)

            # add node to correct player node bdd, 0 evaluates as false and 1 as true
            if node_player:
                phi_1 = phi_1 | current_node_bdd
            else:
                phi_0 = phi_0 | current_node_bdd

        #game_infos.set_expr(phi_0, phi_1, tau, gamma)

        return game_infos

import dd.cudd as _bdd
bdd = _bdd.BDD()
pg2bdd("example_generalized_parity.gpg", bdd)
# gpg2bdd("test.pg", bdd) alternative pour des jeux de parité