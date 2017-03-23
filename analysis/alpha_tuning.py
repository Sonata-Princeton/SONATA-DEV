#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
from sonata.core.training.learn.learn import Learn


def alpha_tuning():
    with open('hypothesis_graph.pickle', 'r') as f:
        G = pickle.load(f)
        learn = Learn(G)
    return 0


if __name__ == '__main__':
    alpha_tuning()