#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime

def get_training_graph(G, n):
    G_out = {}
    timestamps = G.keys()
    timestamps.sort()
    for ts in timestamps[:n]:
        G_out[ts] = G[ts]

    return G_out


def do_alpha_tuning(Ns, Bs, fname, mode):
    from sonata.core.training.learn.learn import Learn
    with open(fname, 'r') as f:
        G = pickle.load(f)
        G_Train = get_training_graph(G, 30)
        # print G
        operational_alphas = {}
        unique_plans = {}
        for n_max in Ns:
            for b_max in Bs:
                alpha = 0.1
                beta = 0
                ctr = 0
                while True:
                    # print alpha
                    operational_alphas[(n_max, b_max)] = alpha
                    learn = Learn(G_Train, alpha, beta, n_max, b_max, mode)
                    # print alpha, n_max, learn.n_viol, b_max,  learn.b_viol
                    if not learn.n_viol and learn.b_viol:
                        alpha = (alpha) / 2
                    elif learn.n_viol and not learn.b_viol:
                        alpha = (1 + alpha) / 2

                    elif learn.n_viol and learn.b_viol:
                        operational_alphas[(n_max, b_max)] = -1
                        break
                    else:
                        # print learn.final_plan.path
                        path_string = learn.final_plan.__repr__()
                        if path_string not in unique_plans:
                            unique_plans[path_string] = {}
                        unique_plans[path_string][(n_max, b_max)] = alpha
                        break
                    ctr += 1
                    if ctr == 10:
                        operational_alphas[(n_max, b_max)] = -1
                        break

                if ctr < 10:
                    print ctr, n_max, b_max, operational_alphas[(n_max, b_max)], learn.final_plan.path
                    # return 0
        # print operational_alphas
        print [(k, len(v)) for k, v in unique_plans.iteritems()]

        return operational_alphas, unique_plans


if __name__ == '__main__':
    Ns = [1000]
    Bs = [10000]
    # Ns = range(100, 5100, 1000)
    # Bs = range(1000, 51000, 10000)
    mode = 3
    fname = 'data/hypothesis_graph_2017-03-29 03:29:50.290812.pickle'
    #fname = 'data/hypothesis_graph_2017-03-29 00:21:42.251074.pickle'
    operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fname, mode)
    data_dump = (Ns, Bs, operational_alphas, unique_plans)
    fname = 'data/alpha_tuning_dump_'+str(datetime.datetime.fromtimestamp(time.time()))+'.pickle'
    with open(fname, 'w') as f:
        pickle.dump(data_dump, f)
