#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
from multiprocessing import Process, Queue
from sonata.core.training.learn.learn import Learn

def get_training_graph(G, n):
    G_out = {}
    timestamps = G.keys()
    timestamps.sort()
    for ts in timestamps[:n]:
        G_out[ts] = G[ts]

    return G_out


def alpha_tuning_iter(G_Train, n_max, b_max, mode, q= None):
    operational_alphas = {}
    unique_plans = {}
    alpha = 0.5
    upper_limit = 1.0
    lower_limit = 0
    beta = 0
    ctr = 0
    print n_max, b_max
    debug = False
    debug = True
    while True:
        # print alpha
        operational_alphas[(n_max, b_max)] = alpha
        learn = Learn(G_Train, alpha, beta, n_max, b_max, mode)
        # print alpha, n_max, learn.n_viol, b_max,  learn.b_viol
        if not learn.n_viol and learn.b_viol:
            upper_limit = alpha
            alpha = (upper_limit+lower_limit) / 2
        elif learn.n_viol and not learn.b_viol:
            lower_limit = alpha
            alpha = (upper_limit+lower_limit) / 2

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
        if learn.final_plan is not None:
            print ctr, n_max, b_max, operational_alphas[(n_max, b_max)], learn.final_plan.path
        else:
            print ctr, n_max, b_max, operational_alphas[(n_max, b_max)], learn.final_plan


    if q is None:
        return operational_alphas, unique_plans
    else:
        q.put((operational_alphas, unique_plans))


def chunkify(lst, n):
    return [lst[i::n] for i in xrange(n) ]


def process_chunk(G_Train, chunk, mode, q=None):
    operational_alphas = {}
    unique_plans = {}
    for (n_max, b_max) in chunk:
        tmp1, tmp2 = alpha_tuning_iter(G_Train, n_max, b_max, mode)
        operational_alphas.update(tmp1)
        unique_plans.update(tmp2)
    # print unique_plans, operational_alphas
    if q is None:
        return operational_alphas, unique_plans
    else:
        q.put((operational_alphas, unique_plans))


def do_alpha_tuning(Ns, Bs, fname, mode):
    with open(fname, 'r') as f:
        G = pickle.load(f)
        G_Train = get_training_graph(G, 10)
        # print G
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
            unique_plans.update(tmp2)
            p.join()


        print operational_alphas
        print [(k, len(v)) for k, v in unique_plans.iteritems()]

        return operational_alphas, unique_plans


if __name__ == '__main__':
    Ns = [3000]
    Bs = [20000]
    # Ns = range(100, 5100, 100)
    # Bs = range(1000, 51000, 1000)
    mode = 6
    fname = 'data/hypothesis_graph_2017-03-29 03:29:50.290812.pickle'
    #fname = 'data/hypothesis_graph_2017-03-29 00:21:42.251074.pickle'
    operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fname, mode)
    data_dump = (Ns, Bs, operational_alphas, unique_plans)
    fname = 'data/alpha_tuning_dump_'+str(datetime.datetime.fromtimestamp(time.time()))+'.pickle'
    print "Dumping data to", fname
    # with open(fname, 'w') as f:
    #     pickle.dump(data_dump, f)
