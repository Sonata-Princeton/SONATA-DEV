#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from sonata.core.partition import get_query_2_plans
from sonata.core.utils import *
from counts import *
from sonata.core.training.hypothesis.costs.costs import Costs


class Hypothesis(object):
    """
    Generates the hypothesis graphs using the input query and training data (from runtime) as input
    """
    def __init__(self, runtime, query):
        self.query = query
        self.runtime = runtime
        self.get_refinement_levels()
        self.get_partitioning_plans()
        self.get_iteration_levels()
        self.get_vertices()
        self.add_edges()
        self.update_graphs()

    def get_refinement_levels(self):
        refinement_keys = get_refinement_keys(self.query)
        # TODO: support multiple candidate refinement keys
        refinement_key = list(refinement_keys)[0]
        ref_levels = range(0, GRAN_MAX, GRAN)
        if refinement_key != '':
            print "Reduction key for Query", self.query.qid, " is ", refinement_key
        else:
            print "Query", self.query.qid, " cannot be refined"
            ref_levels = []
        self.refinement_key = refinement_key
        self.refinement_levels = ref_levels
        R = []
        for ref_level in ref_levels:
            R.append(ref_level)
        self.R = R

    def get_partitioning_plans(self):
        self.flattened_queries = get_flattened_sub_queries(self.query)
        query_2_plans = get_query_2_plans(self.flattened_queries, self.runtime)
        # TODO: add support for queries with join operations
        #P = {}
        for qid in query_2_plans:
            P = query_2_plans[qid]
        self.P = P

    def get_iteration_levels(self):
        self.L = range(1, len(self.R))

    def get_vertices(self):
        # TODO: add support for queries with join operations
        vertices = []
        for r in self.R:
            for p in self.P:
                for l in self.L:
                    vertices.append((r,p,l))
        # Add start node
        vertices.append((self.refinement_levels[0],0,0))
        # Add target node
        vertices.append((self.refinement_levels[-1],0,0))
        self.V = vertices

    def add_edges(self):
        # Run the query over training data to get various counts
        counts = Counts(self.runtime.sc, self.runtime.timestamps, self.refinement_key,
                         self.runtime.training_data, self.refinement_levels, self.query)

        # Apply the costs model over counts to estimate costs for different edges
        costs = Costs(counts, self.P).costs
        print costs

        E = {}
        timestamps = []
        for (r1,p1,l1) in self.V:
            for (r2,p2,l2) in self.V:
                if r1 < r2 and l2 == l1+1:
                    edge = ((r1,p1,l1), (r2,p2,l2))
                    transit = (r1,r2)
                    partition_plan = p2
                    qid = self.query.qid
                    print qid, transit, partition_plan
                    for (ts, w) in costs[qid][transit][partition_plan]:
                        if ts not in E:
                            E[ts] = {}
                        E[ts][edge] = w
                        #timestamps[ts] = 0
        self.E = E
        #self.timestamps = timestamps

    def update_graphs(self):
        G = {}
        for ts in self.runtime.timestamps:
            G[ts] = (self.V, self.E[ts])
        self.G = G