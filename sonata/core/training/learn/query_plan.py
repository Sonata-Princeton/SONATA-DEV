# Author: arpitg@cs.princeton.edu

import numpy as np
from sonata.core.training.learn.search import map_input_graph


class QueryPlan(object):
    cost = 0

    def __init__(self, g, p):
        self.graph = g
        self.path = p
        self.get_cost()

    def __repr__(self):
        return ",".join([str(e) for e in self.path[1:-1]])

    def get_cost(self):
        cost = 0
        #print self.graph.dict
        for (A, B) in zip(self.path, self.path[1:]):
            cost += self.graph.get(A.state, B.state)
        self.cost = cost


class QueryPlanMulti(object):
    # Defined over multiple graphs
    cost = 0
    ncosts = {}
    bcosts = {}

    def __init__(self, G, weighted_g, p, rmse):
        self.G = G
        self.graphs = dict((ts, map_input_graph(g)) for ts,g in weighted_g.iteritems())
        self.path = p
        self.rmse = rmse
        self.get_cost()
        self.get_n_cost()
        self.get_b_cost()

    def __repr__(self):
        return ",".join([str(e) for e in self.path[1:-1]])

    def get_cost(self):
        cost = 0
        costs = {}
        for ts in self.graphs:
            costs[ts] = 0
            #print self.graph.dict
            for (A, B) in zip(self.path, self.path[1:]):
                costs[ts] += self.graphs[ts].get(A.state, B.state)

        self.cost = np.mean(costs.values())

    def get_n_cost(self):
        ncosts = {}
        for ts in self.G:
            v,e = self.G[ts]
            ncosts[ts] = 0
            for (A, B) in zip(self.path[:-1], self.path[1:-1]):
                ncosts[ts] += e[(A.state, B.state)][1]

        self.ncosts = ncosts

    def get_b_cost(self):
        bcosts = {}
        for ts in self.G:
            v,e = self.G[ts]
            bcosts[ts] = 0
            for (A, B) in zip(self.path[:-1], self.path[1:-1]):
                bcost = e[(A.state, B.state)][0]
                if type(bcost) == type(1):
                    bcosts[ts] = bcost
                else:
                    bcosts[ts] += min(bcost)

        self.bcosts = bcosts



