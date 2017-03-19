#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

# from __future__ import print_function
from sonata.core.utils import *
from counts import *
from sonata.core.training.hypothesis.costs.costs import Costs
from sonata.core.partition import Partition


class Hypothesis(object):
    """
    Generates the hypothesis graphs using the input query and training data (from runtime) as input
    """
    E = {}
    G = {}

    def __init__(self, query, sc, training_data, timestamps, refinement_object, target):
        self.sc = sc
        self.training_data = training_data
        self.timestamps = timestamps
        self.query = query
        self.refinement_object = refinement_object
        self.target = target
        
        self.refinement_key = refinement_object.refinement_key
        self.refinement_levels = self.refinement_object.ref_levels
        self.alpha = ALPHA
        self.beta = BETA
        self.get_refinement_levels()
        self.get_partitioning_plans()
        self.get_iteration_levels()
        self.get_vertices()
        self.add_edges()
        self.update_graphs()

    def get_refinement_levels(self):
        self.R = self.refinement_object.ref_levels[1:]

    def get_partitioning_plans(self):
        partition_object = Partition(self.query, self.target)
        query_2_plans = partition_object.get_query_2_plans()

        # TODO: add support for queries with join operations
        # P = {}
        for qid in query_2_plans:
            P = query_2_plans[qid]
        print "Partitioning Plans (P)", P
        self.P = P

    def get_iteration_levels(self):
        self.L = range(1, 1+len(self.R))

    def get_vertices(self):
        # TODO: add support for queries with join operations
        vertices = []
        for r in self.R:
            for p in self.P:
                for l in self.L:
                    vertices.append((r, p, l))
        # Add start node
        vertices.append((self.refinement_levels[0], 0, 0))
        # Add target node
        vertices.append((self.refinement_levels[-1], 0, 0))
        self.V = vertices

    def add_edges(self):
        usePickle = False
        if usePickle:
            with open('costs.pickle', 'r') as f:
                print "Loading costs from pickle..."
                costs = pickle.load(f)
        else:
            # Run the query over training data to get various counts
            counts = Counts(self.query, self.sc, self.training_data, self.timestamps, self.refinement_object, self.target)
            # Apply the costs model over counts to estimate costs for different edges
            costs = Costs(counts, self.P).costs
            print costs
            with open('costs.pickle', 'w') as f:
                print "Dumping costs into pickle..."
                pickle.dump(costs, f)

        E = {}
        print "Vertices", self.V
        for (r1, p1, l1) in self.V:
            for (r2, p2, l2) in self.V:
                if r1 < r2 and l2 == l1 + 1:
                    edge = ((r1, p1, l1), (r2, p2, l2))

                    # initialize edges for all timestamps
                    for ts in self.timestamps:
                        if ts not in E:
                            E[ts] = {}
                        E[ts][edge] = 0

                    # for timestamps for which we have cost data, we will update the edge values
                    # this ensures that we graphs for every timestamp.
                    transit = (r1, r2)
                    partition_plan = p2
                    qid = self.query.qid
                    print qid, transit, partition_plan
                    if partition_plan in costs[qid][transit]:
                        for (ts, (b, n)) in costs[qid][transit][partition_plan]:
                            E[ts][edge] = (self.alpha * n + (1 - self.alpha) * b)

        # Add edges for the final refinement level and the final target (T) node
        for (r, p, l) in self.V:
            if r == self.refinement_levels[-1] and p != -1:
                edge = ((r, p, l), (r, 0, 0))
                for ts in self.timestamps:
                    if ts not in E:
                        E[ts] = {}
                    E[ts][edge] = 0

        self.E = E

    def update_graphs(self):
        G = {}
        for ts in self.timestamps:
            G[ts] = (self.V, self.E[ts])
        self.G = G
