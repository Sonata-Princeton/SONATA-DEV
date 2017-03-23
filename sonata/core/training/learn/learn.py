#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from sonata.system_config import FOLD_SIZE
from utils import min_error, partition_data
from sonata_search import Search, QueryPlan, map_input_graph
from query_plan import QueryPlan
import math

debug = False


def get_min_error_path(G, H):
    unique_candidates = {}
    for ts in G:
        candidate_hash = H[ts].__repr__()
        if candidate_hash not in unique_candidates:
            unique_candidates[candidate_hash] = H[ts]
    if debug: print "Unique Candidates:", unique_candidates

    error = {}
    for candidate in unique_candidates:
        error_candidate = 0
        path1 = unique_candidates[candidate]
        for ts in G:
            path2 = H[ts]
            path3 = QueryPlan(map_input_graph(G[ts]), path1.path)
            error_candidate += (path2.cost - path3.cost) * (path2.cost - path3.cost)
        error[candidate] = math.sqrt(error_candidate)
    if debug: print "Error:", error
    min_error_candidate = min(error, key=error.get)
    assert isinstance(unique_candidates[min_error_candidate], QueryPlan)
    return unique_candidates[min_error_candidate]


class Learn(object):
    final_plan = None
    query_plan = {}
    b_viol = False
    n_viol = False

    def __init__(self, G, alpha, beta, n_max, b_max):
        self.G = G
        self.G_orig = G
        self.timestamps = G.keys()
        self.alpha = alpha
        self.beta = beta
        self.n_max = n_max
        self.b_max = b_max

        # sort the timestamps for sanity reasons
        self.timestamps.sort()

        self.K = int(len(self.timestamps)/FOLD_SIZE)
        # print "Total Folds", self.K

        # Update the edges for the graph
        self.update_edges()
        self.learn_query_plan()

    def update_edges(self):
        G_new = {}
        for ts in self.G:
            (v,edges) = self.G[ts]
            updated_edges = {}
            for edge in edges:
                (b,n) = edges[edge]
                updated_edges[edge] = (self.alpha*float(n)/self.n_max)+((1-self.alpha)*float(b)/self.b_max)
                # if ts == 1440289056: print ts, edge, edges[edge], updated_edges[edge]
            G_new[ts] = (v, updated_edges)

        self.G = G_new

    def learn_query_plan(self):
        h_s = {}
        h_T = {}
        e_V = {}
        candidates = {}
        #debug = True
        for ts in self.G:
            # print "Searching best path for", ts
            g = self.G[ts]
            #if ts == 1440289041:
            if True:
                h_s[ts] = Search(g).final_plan
                if debug: print "Best path for ts", ts, "is", h_s[ts].path, "with cost", h_s[ts].cost
                n = 0
                b = 0
                V,E = self.G_orig[ts]
                for n1,n2 in zip(h_s[ts].path, h_s[ts].path[1:]):
                    edge = tuple([n1.state, n2.state])
                    b += E[edge][0]
                    n += E[edge][1]
                if debug: print "N:", n, "B:", b
                if n > self.n_max:
                    self.n_viol = True
                if b > self.b_max:
                    self.b_viol = False
                if self.b_viol or self.n_viol:
                    self.final_plan = [(self.b_viol, self.n_viol)]
                    return 0




        for fold in range(1, 1+self.K):
            (G_t, G_v) = partition_data(self.G, fold, self.K)
            h_T[fold] = get_min_error_path(G_t, h_s)

            if debug: print "For fold", fold, "best plan", h_T[fold].path

            error_fold = 0
            for ts in G_v:
                path1 = h_s[ts]
                path2 = QueryPlan(map_input_graph(G_v[ts]), h_T[fold].path)
                error_fold += (path2.cost-path1.cost)*(path2.cost-path1.cost)

            e_V[fold] = math.sqrt(error_fold)
            candidates[fold] = (h_T[fold], e_V[fold])
        final_plan = min_error(candidates.values())
        if debug: print "Final Plan:", final_plan.path
        self.final_plan = final_plan