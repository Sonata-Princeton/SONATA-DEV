#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
from multiprocessing import Process, Queue
from sonata.core.training.learn.learn import Learn
from analysis.utils import chunkify, get_training_graph


def alpha_tuning_iter(G_Train, n_max, b_max, mode, q=None):
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

    max_iter = 10

    print n_max, b_max
    debug = False
    debug = True
    while True:
        # print alpha
        operational_alphas[(n_max, b_max)] = alpha
        learn = Learn(G_Train, alpha, beta, n_max, b_max, mode)
        path_string = learn.final_plan.__repr__()

        if debug: print alpha, n_max, learn.n_viol, b_max, learn.b_viol, path_string

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
            print cost_left, curr_cost, cost_right
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

    if q is None:
        return operational_alphas, unique_plans
    else:
        q.put((operational_alphas, unique_plans))


def process_chunk(G_Train, chunk, mode, q=None):
    operational_alphas = {}
    unique_plans = {}
    for (n_max, b_max) in chunk:
        tmp1, tmp2 = alpha_tuning_iter(G_Train, n_max, b_max, mode)
        operational_alphas.update(tmp1)
        for path_string in tmp2:
            if path_string not in unique_plans:
                unique_plans[path_string] = tmp2[path_string]
            else:
                unique_plans[path_string].update(tmp2[path_string])
    # print unique_plans, operational_alphas
    if q is None:
        return operational_alphas, unique_plans
    else:
        q.put((operational_alphas, unique_plans))


def do_alpha_tuning(Ns, Bs, fname, mode):
    with open(fname, 'r') as f:
        G = pickle.load(f)
        G_Train = get_training_graph(G, 40)
        v,e = G_Train[G_Train.keys()[0]]
        for ((r1,p1,l1),(r2,p2,l2)) in e:
            if r2 == 32 and l2 == 1:
                print e[((r1,p1,l1),(r2,p2,l2))]
        operational_alphas = {}
        unique_plans = {}
        configs = []
        for n_max in Ns:
            for b_max in Bs:
                configs.append((n_max, b_max))
        n_cores = 8
        cfg_chunks = chunkify(configs, n_cores)
        queues = []
        processes = []
        for chunk in cfg_chunks:
            if len(chunk) > 0:
                q = Queue()
                queues.append(q)
                p = Process(target=process_chunk, args=(G_Train, chunk, mode, q,))
                processes.append(p)
                p.start()
        for ctr in range(len(processes)):
            p = processes[ctr]
            q = queues[ctr]

            (tmp1, tmp2) = q.get()
            print tmp1, tmp2
            operational_alphas.update(tmp1)
            for path_string in tmp2:
                if path_string not in unique_plans:
                    unique_plans[path_string] = tmp2[path_string]
                else:
                    unique_plans[path_string].update(tmp2[path_string])
            p.join()

        print operational_alphas
        print unique_plans
        # print [(k, len(v)) for k, v in unique_plans.iteritems()]

        return operational_alphas, unique_plans


def get_system_configs(fname):
    import math

    nmax = 0
    bmax = 0
    p_max = 0
    with open(fname, 'r') as f:
        G = pickle.load(f)
        G_Train = get_training_graph(G, 20)
        for ts in G_Train:
            v, e = G_Train[ts]
            for r, p, l in v:
                if p > p_max:
                    p_max = p
            n = int(e[(0, 0, 0), (32, 0, 1)][1])
            if type(e[(0, 0, 0), (32, p_max, 1)][0]) == type(1):
                b = int(e[(0, 0, 0), (32, p_max, 1)][0])
            else:
                b = int(max(e[(0, 0, 0), (32, p_max, 1)][0]))

            if b > bmax:
                bmax = b
            if n > nmax:
                nmax = n

    nStep = math.ceil(float(nmax) / 10)
    bStep = math.ceil(float(bmax) / 10)

    print "Nmax:", nmax, "Bmax:", bmax
    print nStep, bStep

    Ns = range(1, int(11*nStep + 1), int(nStep))
    Bs = range(1, int(11*bStep + 1), int(bStep))
    print "Ns:", Ns, "Bs:", Bs
    return Ns, Bs


if __name__ == '__main__':
    Ns = [200]
    Bs = [500]
    # Ns = range(100, 11000, 1000)
    # Bs = range(1000, 110000, 10000)

    fname = 'data/hypothesis_graph_2017-03-29 03:29:50.290812.pickle'
    # fname = 'data/hypothesis_graph_2017-03-29 00:21:42.251074.pickle'
    fname = 'data/hypothesis_graph_6_2017-04-09 15:07:16.014979.pickle'
    # fname = 'data/hypothesis_graph_2_2017-04-09 14:51:55.766276.pickle'
    fname = 'data/data/hypothesis_graph_2_2017-04-09 14:51:55.766276.pickle'

    # latest 1 minute data with all the fixes
    fname = 'data/hypothesis_graph_6_2017-04-11 02:55:06.032332.pickle'
    # fname = 'data/hypothesis_graph_2_2017-04-11 02:32:08.513236.pickle'
    fname = 'data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'
    fname = 'data/hypothesis_graph_5_2017-04-11 02:47:30.593298.pickle'
    fname ='data/hypothesis_graph_4_2017-04-11 02:42:58.077458.pickle'


    fname = 'data/hypothesis_graph_4_2017-04-11 22:58:56.434682.pickle'
    Ns, Bs = get_system_configs(fname)
    Ns = [100]
    Bs = [20000]

    modes = [2, 3, 4, 5, 6]
    modes = [4,6]
    data_dump = {}
    for mode in modes:
        print mode
        operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fname, mode)
        data_dump[mode] = (Ns, Bs, operational_alphas, unique_plans)

    qid = 6
    fname = 'data/alpha_tuning_dump_' +str(qid)+'_'+ str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping data to", fname
    # with open(fname, 'w') as f:
    #     pickle.dump(data_dump, f)
