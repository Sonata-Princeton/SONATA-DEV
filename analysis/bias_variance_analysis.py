#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
import math
from multiprocessing import Process, Queue
from sonata.core.training.learn.learn import Learn
from analysis.utils import chunkify, get_training_graph, get_test_graph
from alpha_tuning import alpha_tuning_iter

from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph

debug = False

# TODO: this function is redundant, get rid of it in future
def alpha_tuning_iter(G_Train, n_max, b_max, mode):
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


def do_bias_variance_analysis(fname,Ns, Bs):
    with open(fname, 'r') as f:
        G = pickle.load(f)
        print "Loaded graph file", fname
        modes = [2, 3, 4, 5, 6]
        modes = [5]
        TDs = range(0, 101, 10)[1:]
        # TDs = [5, 10, 20, 30]

        debug = False
        # debug = True

        data_dump = {}
        for mode in modes:
            print "Mode:", mode
            data_dump[mode] = {}
            for n_max in Ns:
                for b_max in Bs:
                    data_dump[mode][(n_max, b_max)] = {}
                    for td in TDs:
                        G_Train = get_training_graph(G, td)
                        G_Test = get_test_graph(G, td)
                        print len(G_Train.keys()), len(G_Test.keys())
                        alpha, trained_learn = alpha_tuning_iter(G_Train, n_max, b_max, mode)
                        if debug: print "After tuning for config", n_max, b_max, "we get alpha", alpha, "path", \
                            trained_learn.final_plan, trained_learn.final_plan.rmse

                        in_sample_error = {}
                        out_sample_error = {}
                        timestamps = G.keys()
                        timestamps.sort()
                        ctr = 1
                        for ts in timestamps[:50]:
                            g = update_edges(G[ts], n_max, b_max, alpha, mode)
                            training_plan = QueryPlan(map_input_graph(g), trained_learn.final_plan.path)
                            local_best_plan = QueryPlan(map_input_graph(g), Search(g).final_plan.path)
                            local_error = (training_plan.cost - local_best_plan.cost)
                            if debug: print "time", ts, "learned plan", training_plan, "local best plan", local_best_plan
                            if debug: print "Cost1", training_plan.cost, "Cost2", local_best_plan.cost, local_error

                            if ctr > td:
                                if local_best_plan.cost > 0:
                                    out_sample_error[ts] = local_error
                                else:
                                    out_sample_error[ts] = 0
                            else:
                                in_sample_error[ts] = local_error
                            ctr += 1
                        # print in_sample_error.values(), out_sample_error.values()
                        in_rmse = (math.sqrt(sum([x*x for x in in_sample_error.values()])))/len(in_sample_error.keys())
                        out_rmse = math.sqrt(sum([x*x for x in out_sample_error.values()]))/len(out_sample_error.keys())
                        print in_rmse, out_rmse
                        data_dump[mode][(n_max, b_max)][td] = (in_rmse, out_rmse)
                        # break

        fname_dump = 'data/bias_var_analysis_' + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
        print "Dumping data to", fname_dump
        # with open(fname_dump, 'w') as f:
        #     pickle.dump(data_dump, f)
        return data_dump


if __name__ == '__main__':
    # Ns = [3100]
    # Bs = [21000]

    Ns = [1000]
    Bs = [20000]

    fname = 'data/hypothesis_graph_2017-03-29 03:29:50.290812.pickle'

    fname = 'data/hypothesis_graph_4_2017-04-11 22:58:56.434682.pickle'
    fname6 = 'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'
    fname1 = 'data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'

    do_bias_variance_analysis(fname1, Ns, Bs)



