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

    def __init__(self, G, p, rmse):
        self.graphs = dict((ts, map_input_graph(g)) for ts,g in G.iteritems())
        self.path = p
        self.rmse = rmse
        self.get_cost()

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
