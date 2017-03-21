# Author: arpitg@cs.princeton.edu

class QueryPlan(object):
    cost = 0

    def __init__(self, g, p):
        self.graph = g
        self.path = p
        self.get_cost()

    def __repr__(self):
        return ",".join([str(e) for e in self.path])

    def get_cost(self):
        cost = 0
        #print self.graph.dict
        for (A, B) in zip(self.path, self.path[1:]):
            cost += self.graph.get(A.state, B.state)
        self.cost = cost
