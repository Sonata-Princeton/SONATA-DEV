#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
from sonata.core.training.learn.learn import Learn


def alpha_tuning():
    Ns = [100, 1000, 10000, 100000, 1000000]
    Bs = [100, 1000, 10000, 100000, 1000000]
    with open('hypothesis_graph.pickle', 'r') as f:
        G = pickle.load(f)
        # print G
        operational_alphas = {}
        for n_max in Ns:
            operational_alphas[n_max] = {}
            for b_max in Bs:

                alpha = 0.5
                beta = 0
                ctr = 0
                while True:
                    print alpha
                    operational_alphas[n_max][b_max] = alpha
                    learn = Learn(G, alpha, beta, n_max, b_max)
                    print learn.n_viol, learn.b_viol
                    if learn.n_viol and not learn.b_viol:
                        alpha = (1 + alpha) / 2
                    elif not learn.n_viol and learn.b_viol:
                        alpha = (alpha) / 2
                    elif learn.n_viol and learn.b_viol:
                        operational_alphas[n_max][b_max] = -1
                        break
                    else:
                        break
                    ctr += 1
                    if ctr == 10:
                        break
                print ctr, n_max, b_max, operational_alphas[n_max][b_max]
                #return 0
        print operational_alphas


if __name__ == '__main__':
    alpha_tuning()
