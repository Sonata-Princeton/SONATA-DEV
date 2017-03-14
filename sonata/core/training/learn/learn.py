#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from sonata.system_config import FOLD_SIZE
from utils import min_error, get_min_error_path, partition_data
from sonata_search import Search, Path
import math

class Learn(object):
    def __init__(self, hypothesis):
        self.hypothesis = hypothesis
        self.query_plan = {}
        self.K = int(len(self.hypothesis.timestamps)/FOLD_SIZE)
        self.learn_query_plan()

    def learn_query_plan(self):
        H_S = {}
        H_T = {}
        E_V = {}
        candidates = {}
        for ts in self.hypothesis.G:
            g = self.hypothesis.G[ts]
            H_S[ts] = Search(g).final_plan

        for fold in range(1, 1+self.K):
            (G_t, G_v) = partition_data(self.hypothesis.G, fold, self.K)
            H_T[fold] = get_min_error_path(G_t, H_S)
            error_fold = 0
            for ts in G_v:
                path1 = H_S[ts]
                path2 = Path(G_v[ts], H_T[fold].path)
                error_fold += (path2.cost-path1.cost)*(path2.cost-path1.cost)

            E_V[fold] = math.sqrt(error_fold)
            candidates[fold] = (H_T[fold], E_V[fold])

        self.final_plan = min_error(candidates)





