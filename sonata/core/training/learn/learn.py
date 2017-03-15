#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from sonata.system_config import FOLD_SIZE
from utils import min_error, partition_data
from sonata_search import Search, Path, map_input_graph
import math


def get_min_error_path(G, H):
    unique_candidates = dict((x.__repr__(), x) for x in H.values())
    error = {}
    for candidate in unique_candidates:
        error_candidate = 0
        for ts in G:
            path1 = unique_candidates[candidate]
            path2 = H[ts]
            #path3 = Path(map_input_graph(G[ts]), path1.path)
            #error_candidate += (path2.cost - path3.cost) * (path2.cost - path3.cost)
        error[candidate] = error_candidate
    print unique_candidates, error
    min_error_candidate = min(error, key=error.get)
    print min_error_candidate
    return unique_candidates[min_error_candidate]


class Learn(object):
    def __init__(self, hypothesis):
        self.hypothesis = hypothesis
        self.query_plan = {}
        self.K = int(len(self.hypothesis.runtime.timestamps)/FOLD_SIZE)
        self.learn_query_plan()

    def learn_query_plan(self):
        h_s = {}
        h_T = {}
        e_V = {}
        candidates = {}
        for ts in self.hypothesis.G:
            print "Searching best path for", ts
            g = self.hypothesis.G[ts]
            h_s[ts] = Search(g).final_plan
            print "Best path for ts", ts, "is", h_s[ts].path, "with cost", h_s[ts].cost

        for fold in range(1, 1+self.K):
            (G_t, G_v) = partition_data(self.hypothesis.G, fold, self.K)
            h_T[fold] = get_min_error_path(G_t, h_s)

            error_fold = 0
            for ts in G_v:
                path1 = h_s[ts]
                #path2 = Path(map_input_graph(G_v[ts]), h_T[fold].path)
                #error_fold += (path2.cost-path1.cost)*(path2.cost-path1.cost)

            e_V[fold] = math.sqrt(error_fold)
            candidates[fold] = (h_T[fold], e_V[fold])

        self.final_plan = min_error(candidates)