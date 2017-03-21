#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from sonata.system_config import FOLD_SIZE
from utils import min_error, partition_data
from sonata_search import Search, QueryPlan, map_input_graph
from query_plan import QueryPlan
import math


def get_min_error_path(G, H):
    unique_candidates = {}
    for ts in G:
        candidate_hash = H[ts].__repr__()
        if candidate_hash not in unique_candidates:
            unique_candidates[candidate_hash] = H[ts]
    print "Unique Candidates:", unique_candidates

    error = {}
    for candidate in unique_candidates:
        error_candidate = 0
        path1 = unique_candidates[candidate]
        for ts in G:
            path2 = H[ts]
            path3 = QueryPlan(map_input_graph(G[ts]), path1.path)
            error_candidate += (path2.cost - path3.cost) * (path2.cost - path3.cost)
        error[candidate] = math.sqrt(error_candidate)
    print "Error:", error
    min_error_candidate = min(error, key=error.get)
    assert isinstance(unique_candidates[min_error_candidate], QueryPlan)
    return unique_candidates[min_error_candidate]


class Learn(object):
    final_plan = None
    query_plan = {}

    def __init__(self, hypothesis):
        self.hypothesis = hypothesis
        self.K = int(len(self.hypothesis.timestamps)/FOLD_SIZE)
        # print "Total Folds", self.K
        self.learn_query_plan()

    def learn_query_plan(self):
        h_s = {}
        h_T = {}
        e_V = {}
        candidates = {}
        for ts in self.hypothesis.G:
            # print "Searching best path for", ts
            g = self.hypothesis.G[ts]
            h_s[ts] = Search(g).final_plan
            print "Best path for ts", ts, "is", h_s[ts].path, "with cost", h_s[ts].cost

        for fold in range(1, 1+self.K):
            (G_t, G_v) = partition_data(self.hypothesis.G, fold, self.K)
            h_T[fold] = get_min_error_path(G_t, h_s)

            print "For fold", fold, "best plan", h_T[fold].path

            error_fold = 0
            for ts in G_v:
                path1 = h_s[ts]
                path2 = QueryPlan(map_input_graph(G_v[ts]), h_T[fold].path)
                error_fold += (path2.cost-path1.cost)*(path2.cost-path1.cost)

            e_V[fold] = math.sqrt(error_fold)
            candidates[fold] = (h_T[fold], e_V[fold])

        self.final_plan = min_error(candidates.values())