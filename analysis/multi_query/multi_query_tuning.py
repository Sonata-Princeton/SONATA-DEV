#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
from multiprocessing import Process, Queue
from sonata.core.training.learn.learn import Learn
from analysis.utils import chunkify, get_training_graph

TRAIN_DURATION = 10


def get_violation_flags(G_Trains, learn, n_max, b_max, alpha):
    n_viol = False
    b_viol = False
    total_n = {}
    total_b = {}
    debug = True

    for fname in learn:
        if debug: print alpha, fname, learn[fname].final_plan
        print max(learn[fname].final_plan.ncosts.values()), max(learn[fname].final_plan.bcosts.values())
        for ts in G_Trains[fname]:
            if ts not in total_n:
                total_n[ts] = 0
                total_b[ts] = 0
            # print total_n[ts], total_b[ts], learn[fname].final_plan.ncosts[ts], learn[fname].final_plan.bcosts[ts]
            total_n[ts] += learn[fname].final_plan.ncosts[ts]
            total_b[ts] += learn[fname].final_plan.bcosts[ts]

    max_n = max(total_n.values())
    max_b = max(total_b.values())
    if debug: print "max tuples for this plan", alpha, max_n
    if debug: print "max bits for this plan", alpha, max_b
    if max_n > n_max:
        n_viol = True
    if max_b > b_max:
        b_viol = True

    return n_viol, b_viol


def update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha):
    operational_alphas[(n_max, b_max)] = alpha


def update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha):
    for fname in fnames:
        path_string = path_strings[fname]
        if path_string not in unique_plans[fname]:
            unique_plans[fname][path_string] = {}
        unique_plans[fname][path_string][(n_max, b_max)] = alpha


def alpha_tuning_iter(fnames, n_max, b_max, mode, td, q=None):
    memoized_learning = {}

    def memoize_learning(G, alpha, beta, n_max, b_max, mode, fname):
        if (alpha, beta, n_max, b_max, mode, fname) not in memoized_learning:
            memoized_learning[(alpha, beta, n_max, b_max, mode, fname)] = Learn(G, alpha, beta, n_max, b_max, mode)
        return memoized_learning[(alpha, beta, n_max, b_max, mode, fname)]

    def learn_for_alpha(G, fnames, alpha, beta, n_max, b_max, mode):
        learn = {}
        path_strings = {}
        cost = 0
        for fname in fnames:
            learn[fname] = memoize_learning(G[fname], alpha, beta, n_max, b_max, mode, fname)
            path_strings[fname] = learn[fname].final_plan.__repr__()
            cost += learn[fname].final_plan.cost

        n_viol, b_viol = get_violation_flags(G_Trains, learn, n_max, b_max, alpha)

        return learn, path_strings, cost, n_viol, b_viol

    G_Trains = {}
    operational_alphas = {}
    unique_plans = {}
    for fname in fnames:
        with open(fname,'r') as f:
            G = pickle.load(f)
            # print "Training Duration", td
            G_Trains[fname] = get_training_graph(G, td)
        unique_plans[fname] = {}

    prev_alpha = 0
    alpha = 0.5
    prev_cost = 0
    curr_cost = 0

    upper_limit = 1.0
    lower_limit = 0
    beta = 0
    ctr = 0

    max_iter = 10

    # print n_max, b_max
    debug = False
    debug = True
    while True:
        # print alpha
        operational_alphas[(n_max, b_max)] = alpha
        learn, path_strings, curr_cost, n_viol, b_viol = learn_for_alpha(G_Trains, fnames, alpha, beta, n_max, b_max, mode)

        if debug: print alpha, n_max, n_viol, b_max, b_viol

        if not n_viol and b_viol:
            upper_limit = alpha
            alpha = (upper_limit + lower_limit) / 2
            update_operational_alphas(operational_alphas, fnames, n_max, b_max, -1)
            update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
        elif n_viol and not b_viol:
            lower_limit = alpha
            alpha = (upper_limit + lower_limit) / 2
            if ctr == max_iter - 1:
                update_operational_alphas(operational_alphas, fnames, n_max, b_max, -1)
                update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
        elif n_viol and b_viol:
            update_operational_alphas(operational_alphas, fnames, n_max, b_max, -1)
            update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
            break
        else:
            # print trained_learn.local_best_plan.path

            alpha_right = (alpha + upper_limit) / 2
            learn_right, _, cost_right, n_viol_right, b_viol_right = learn_for_alpha(G_Trains, fnames, alpha_right,
                                                                                     beta, n_max, b_max, mode)
            if n_viol_right or b_viol_right:
                cost_right = 100

            alpha_left = (alpha + lower_limit) / 2
            learn_left, _, cost_left, n_viol_left, b_viol_left = learn_for_alpha(G_Trains, fnames, alpha_left,
                                                                                     beta, n_max, b_max, mode)
            if n_viol_left or b_viol_left:
                cost_left = 100

            if debug: print cost_left, curr_cost, cost_right
            if cost_left < curr_cost:
                upper_limit = alpha_left
                alpha = alpha_left
            elif cost_right < curr_cost:
                lower_limit = alpha_right
                alpha = alpha_right
            else:
                update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha)
                update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
                break
            if ctr == max_iter - 1:
                update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha)
                update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)

        ctr += 1
        if ctr == max_iter:
            break

    if q is None:
        return operational_alphas, unique_plans
    else:
        q.put((operational_alphas, unique_plans))


def process_chunk(fnames, chunk, mode, td, q=None):
    operational_alphas = {}
    unique_plans = {}
    print chunk
    for (n_max, b_max) in chunk:
        tmp1, tmp2 = alpha_tuning_iter(fnames, n_max, b_max, mode, td)
        print tmp1
        operational_alphas.update(tmp1)
        for fname in fnames:
            if fname not in unique_plans:
                unique_plans[fname] = {}

            for path_string in tmp2[fname]:
                if path_string not in unique_plans[fname]:
                    unique_plans[fname][path_string] = tmp2[fname][path_string]
                else:
                    unique_plans[fname][path_string].update(tmp2[fname][path_string])
    if q is None:
        return operational_alphas, unique_plans
    else:
        q.put((operational_alphas, unique_plans))


def do_alpha_tuning(Ns, Bs, fnames, mode, td):
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
            p = Process(target=process_chunk, args=(fnames, chunk, mode, td, q,))
            processes.append(p)
            p.start()
    for ctr in range(len(processes)):
        p = processes[ctr]
        q = queues[ctr]

        (tmp1, tmp2) = q.get()
        # print tmp1, tmp2
        operational_alphas.update(tmp1)
        for fname in fnames:
            if fname not in unique_plans:
                unique_plans[fname] = {}

            for path_string in tmp2[fname]:
                if path_string not in unique_plans[fname]:
                    unique_plans[fname][path_string] = tmp2[fname][path_string]
                else:
                    unique_plans[fname][path_string].update(tmp2[fname][path_string])
        p.join()

    # print operational_alphas
    # print unique_plans
    # print [(k, len(v)) for k, v in unique_plans.iteritems()]

    return operational_alphas, unique_plans


def get_system_configs(fnames):
    import math
    max_counts = {}
    total_nmax = 0
    total_bmax = 0
    for fname in fnames:
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
                    b = int(min(e[(0, 0, 0), (32, p_max, 1)][0]))

                if b > bmax:
                    bmax = b
                if n > nmax:
                    nmax = n
        total_nmax += nmax
        total_bmax += bmax
        max_counts[fname] = (nmax,bmax)
    print max_counts


    nStep = math.ceil(float(total_nmax) / 10)
    bStep = math.ceil(float(total_bmax) / 10)

    print "Nmax:", total_nmax, "Bmax:", total_bmax
    print nStep, bStep

    Ns = range(int(nStep), 20*int(nStep), int(nStep))
    Bs = range(int(nStep), 20*int(bStep), int(bStep))
    print "Ns:", Ns, "Bs:", Bs
    return Ns, Bs


if __name__ == '__main__':
    Ns = [200]
    Bs = [500]
    # Ns = range(100, 11000, 1000)
    # Bs = range(1000, 110000, 10000)

    fname1 = 'data/hypothesis_graph_2017-03-29-03:29:50.290812_1.pickle'
    fname2 = 'data/hypothesis_graph_2017-03-29-03:29:50.290812_2.pickle'
    # fname = 'data/hypothesis_graph_2017-03-29 00:21:42.251074.pickle'
    # fname = 'data/hypothesis_graph_6_2017-04-09 15:07:16.014979.pickle'
    # fname = 'data/hypothesis_graph_2_2017-04-09 14:51:55.766276.pickle'
    # fname1 = 'data/hypothesis_graph_2_2017-04-09 14:51:55.766276.pickle'
    # fname2 = 'data/hypothesis_graph_6_2017-04-09 15:07:16.014979.pickle'

    fname1 = 'data/hypothesis_graph_1_2017-04-12 11:50:20.246240.pickle'
    fname6 = 'data/hypothesis_graph_6_2017-04-12 12:36:50.995811.pickle'

    fname6 = 'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'
    fname1 = 'data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'
    fname2 = 'data/hypothesis_graph_2_2017-04-16 23:29:09.655075.pickle'
    fname1 = 'data/hypothesis_graph_1_merged_2017-04-17 17:57:50.958863.pickle'
    fname6 = 'data/hypothesis_graph_6_merged_2017-04-17 17:57:50.958863.pickle'
    fname2 = 'data/hypothesis_graph_2_2017-04-17 00:40:52.285241.pickle'
    # fname2 = 'data/hypothesis_graph_2_2017-04-16 23:29:09.655075.pickle'

    # port scanning
    fname2 = 'data/hypothesis_graph_2_min_0_2017-04-18 02:21:52.502334.pickle' # 99.9
    fname2 = 'data/hypothesis_graph_2_min_0_2017-04-18 02:55:20.608072.pickle' # 99.99
    # Query 2: 5min : 99.99 thres port scan
    fname2 = 'data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle'
    fnames = [fname2]
    fnames = ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
          'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle',
          'data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle']
    Ns, Bs = get_system_configs(fnames)
    Ns = [5000]
    Bs = [90000]

    modes = [2, 3, 4, 5]
    modes = [5]
    Td = 20
    data_dump = {}
    for mode in modes:
        print mode
        operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fnames, mode, Td)
        data_dump[mode] = (Ns, Bs, operational_alphas, unique_plans)

    fname = 'data/alpha_tuning_dump_multi_'+str(datetime.datetime.fromtimestamp(time.time()))+ '.pickle'

    print "Dumping data to", fname
    # with open(fname, 'w') as f:
    #     pickle.dump(data_dump, f)
