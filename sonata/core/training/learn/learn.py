#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from sonata.system_config import FOLD_SIZE, GRAN, GRAN_MAX
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

    def __init__(self, G, alpha, beta, n_max, b_max, mode):
        self.G = G
        self.G_orig = G
        self.timestamps = G.keys()
        self.alpha = alpha
        self.beta = beta
        self.n_max = n_max
        self.b_max = b_max
        self.mode = mode

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
                (r1, p1, l1), (r2, p2, l2) = edge
                #print edge, edges[edge]
                # These are tmp fixes
                if l2 > 0 and edges[edge] != (0,0):
                    (b_hash, b_sketch), n  = edges[edge]
                    if self.mode >= 4:
                        # Use sketches
                        b = b_sketch
                    else:
                        # Use hash tables only
                        b = b_hash
                    updated_edges[edge] = (self.alpha*float(n)/self.n_max)+((1-self.alpha)*float(b)/self.b_max)
                else:
                    updated_edges[edge] = 0

                # if ts == 1440289056: print ts, edge, edges[edge], updated_edges[edge]
            G_new[ts] = (v, updated_edges)

        self.G = G_new

    def learn_query_plan(self):
        gran = GRAN
        G_new = {}

        # Update the graph for different operational modes
        if self.mode == 6:
            # Config 6, best SONATA config, no change required
            G_new = self.G

        elif self.mode == 5:
            # mode where we only chose static refinement plan, only keep edges that move one refinement level unit for every iteration
            for ts in self.G:
                v_orig, e_orig = self.G[ts]
                v_new = v_orig
                e_new = {}
                for ((r1, p1, l1), (r2, p2, l2)) in e_orig:
                    edge = (r1, p1, l1), (r2, p2, l2)
                    if r2-r1 == gran:
                        e_new[edge] = e_orig[edge]
                    if p2 == 0 and l2 == 0:
                        e_new[edge] = e_orig[edge]

                G_new[ts] = (v_new, e_new)

        elif self.mode == 4 or self.mode == 3:
            # mode where there is no refinement at all
            for ts in self.G:
                v_orig, e_orig = self.G[ts]
                v_new = v_orig
                e_new = {}
                for ((r1, p1, l1), (r2, p2, l2)) in e_orig:
                    edge = (r1, p1, l1), (r2, p2, l2)
                    #print edge, (l2 in [0, 1]) and (l1 in [0,1]) and r2 == GRAN_MAX-1
                    if (l2 in [0, 1]) and (l1 in [0,1]) and r2 == GRAN_MAX-1:
                        #print edge, (l2 in [0, 1]) and (l1 in [0,1])  and r2 == GRAN_MAX-1
                        e_new[edge] = e_orig[edge]
                #break
                G_new[ts] = (v_new, e_new)

        elif self.mode == 2:
            # mode where there is no stateful dataflow operation in the dataplane, i.e. p2 ==0
            for ts in self.G:
                v_orig, e_orig = self.G[ts]
                v_new = v_orig
                e_new = {}
                for ((r1, p1, l1), (r2, p2, l2)) in e_orig:
                    edge = (r1, p1, l1), (r2, p2, l2)
                    if (l2 in [0, 1]) and p2 == 0 and (l1 in [0,1]) and p1 == 0 and r2 == GRAN_MAX-1:
                        e_new[edge] = e_orig[edge]
                G_new[ts] = (v_new, e_new)

        self.G = G_new
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
                self.update_violation_flags(h_s[ts], ts)

                if self.b_viol or self.n_viol:
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


    def update_violation_flags(self, h, ts):
        n = 0
        b = 0
        V,E = self.G_orig[ts]
        for n1,n2 in zip(h.path, h.path[1:]):
            edge = tuple([n1.state, n2.state])
            (r1, p1, l1), (r2, p2, l2) = edge
            if l2 > 0 and E[edge] != (0,0):
                #print edge, E[edge]
                b += E[edge][0][0]
                n += E[edge][1]
        if debug: print "N:", n, "B:", b
        if n > self.n_max:
            self.n_viol = True
        if b > self.b_max:
            self.b_viol = False