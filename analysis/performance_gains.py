#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
import math

from sonata.core.training.learn.learn import Learn
from analysis.utils import chunkify, get_training_graph, get_test_graph
from alpha_tuning import alpha_tuning_iter

from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph


def alpha_tuning_iter(G_Train, n_max, b_max, mode):
    # TODO: this function is redundant, get rid of it in future
    operational_alphas = {}
    unique_plans = {}
    prev_alpha = 0
    alpha = 0.5
    prev_cost = 0
    curr_cost = 0

    upper_limit = 1.0
    lower_limit = 0
    beta = 0
    ctr = 0
    learn = None

    max_iter = 10

    debug = False
    # debug = True

    if debug: print n_max, b_max
    while True:
        # print alpha
        operational_alphas[(n_max, b_max)] = alpha
        learn = Learn(G_Train, alpha, beta, n_max, b_max, mode)
        path_string = learn.final_plan.__repr__()

        if debug: print alpha, n_max, learn.n_viol, b_max, learn.b_viol

        if not learn.n_viol and learn.b_viol:
            upper_limit = alpha
            alpha = (upper_limit + lower_limit) / 2
            if ctr == max_iter - 1:
                if path_string not in unique_plans:
                    unique_plans[path_string] = {}
                unique_plans[path_string][(n_max, b_max)] = alpha
                operational_alphas[(n_max, b_max)] = -1
        elif learn.n_viol and not learn.b_viol:
            lower_limit = alpha
            alpha = (upper_limit + lower_limit) / 2
            if ctr == max_iter - 1:
                if path_string not in unique_plans:
                    unique_plans[path_string] = {}
                unique_plans[path_string][(n_max, b_max)] = alpha
                operational_alphas[(n_max, b_max)] = -1
        elif learn.n_viol and learn.b_viol:
            if path_string not in unique_plans:
                unique_plans[path_string] = {}
            unique_plans[path_string][(n_max, b_max)] = alpha
            operational_alphas[(n_max, b_max)] = -1
            break
        else:
            # print trained_learn.local_best_plan.path
            path_string = learn.final_plan.__repr__()
            if path_string not in unique_plans:
                unique_plans[path_string] = {}
            curr_cost = learn.final_plan.cost

            alpha_right = (alpha + upper_limit) / 2
            learn_right = Learn(G_Train, alpha_right, beta, n_max, b_max, mode)
            if not learn_right.n_viol and not learn_right.b_viol:
                cost_right = learn_right.final_plan.cost
            else:
                cost_right = 100

            alpha_left = (alpha + lower_limit) / 2
            learn_left = Learn(G_Train, alpha_left, beta, n_max, b_max, mode)
            if not learn_left.n_viol and not learn_left.b_viol:
                cost_left = learn_left.final_plan.cost
            else:
                cost_left = 100
            if debug: print cost_left, curr_cost, cost_right
            if cost_left < curr_cost:
                upper_limit = alpha_left
                alpha = alpha_left
            elif cost_right < curr_cost:
                lower_limit = alpha_right
                alpha = alpha_right
            else:
                operational_alphas[(n_max, b_max)] = alpha
                unique_plans[path_string][(n_max, b_max)] = alpha
                break
            if ctr == max_iter - 1:
                if path_string not in unique_plans:
                    unique_plans[path_string] = {}
                unique_plans[path_string][(n_max, b_max)] = alpha
                operational_alphas[(n_max, b_max)] = alpha

        ctr += 1
        if ctr == max_iter:
            break

    return alpha, learn


def update_edges(G, n_max, b_max, alpha, mode):
    G_new = {}
    (v, edges) = G
    updated_edges = {}
    for edge in edges:
        (r1, p1, l1), (r2, p2, l2) = edge
        # print edge, edges[edge]
        # These are tmp fixes
        if l2 > 0 and edges[edge] != (0, 0):
            (b_hash, b_sketch), n = edges[edge]
            if mode >= 4:
                # Use sketches
                b = min([b_hash, b_sketch])
            else:
                # Use hash tables only
                b = b_hash

            weight = (alpha * float(n) / n_max) + ((1 - alpha) * float(b) / b_max)
            updated_edges[edge] = weight
        else:
            updated_edges[edge] = 0

    G_new = (v, updated_edges)

    return G_new


def do_performance_gains_analysis(Ns, Bs):
    fname = 'data/hypothesis_graph_2017-03-29 03:29:50.290812.pickle'
    with open(fname, 'r') as f:
        G = pickle.load(f)
        print "Loaded graph file", fname
        modes = [2, 3, 4, 5, 6]
        # modes = [4, 6]

        debug = False
        debug = True

        data_dump = {}
        for mode in modes:
            print "Mode:", mode
            data_dump[mode] = {}
            for n_max in Ns:
                for b_max in Bs:
                    data_dump[mode][(n_max, b_max)] = {}
                    td = 5
                    G_Train = get_training_graph(G, td)
                    G_Test = get_test_graph(G, td)
                    print len(G_Train.keys()), len(G_Test.keys())
                    alpha, trained_learn = alpha_tuning_iter(G_Train, n_max, b_max, mode)
                    if debug: print "After tuning for config", n_max, b_max, "we get alpha", alpha, "path", \
                        trained_learn.final_plan, trained_learn.final_plan.rmse
                    timestamps = G.keys()
                    timestamps.sort()
                    ctr = 1
                    trained_path = trained_learn.final_plan.path

                    for ts in timestamps[td:]:
                        v, e = G[ts]
                        # print e
                        n_cost = 0
                        b_cost = 0
                        for (e1, e2) in zip(trained_path[:-1], trained_path[1:])[:-1]:
                            # print e1, e2, e[(e1.state, e2.state)], type((e[(e1.state, e2.state)][0]))
                            if type(e[(e1.state, e2.state)][0]) == type(1):
                                b_cost += e[(e1.state, e2.state)][0]
                            else:
                                b_cost += min(e[(e1.state, e2.state)][0])
                            n_cost += e[(e1.state, e2.state)][1]

                        data_dump[mode][(n_max, b_max)][ts] = (n_cost, b_cost)
        # print data_dump
        fname_dump = 'data/performance_gains_' + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
        print "Dumping data to", fname_dump
        with open(fname_dump, 'w') as f:
            pickle.dump(data_dump, f)


if __name__ == '__main__':
    Ns = [3100]
    Bs = [21000]
    do_performance_gains_analysis(Ns, Bs)
