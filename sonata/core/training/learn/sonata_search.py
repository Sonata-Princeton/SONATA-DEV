# Author: arpitg@cs.princeton.edu

from sonata.core.training.learn.search import *
from sonata.core.training.learn.utils import *


def DirectedGraph(dict=None):
    "Build a Hypothesis where every edge (including future ones) goes both ways."
    return Graph(dict=dict, directed=True)


class GraphProblem(Problem):
    "The problem of searching a graph from one node to another."

    def __init__(self, initial, goal, graph):
        Problem.__init__(self, initial, goal)
        self.graph = graph
        self.best_node = {}

    def actions(self, A):
        "The actions at a graph node are just its neighbors."
        out = self.graph.get(A).keys()
        # Sort the neighbor tuples, TODO: make sure we don't need more sophisticated sort operation
        out.sort()
        return out

    def result(self, state, action):
        "The result of going to a neighbor is just that neighbor."
        return action

    def path_cost(self, cost_so_far, A, action, B):
        return cost_so_far + (self.graph.get(A, B) or infinity)

    def is_qualified(self, A, f):
        "Check whether the graph node is qualified to be a frontier node"
        print A.state
        if len(A.state) > 1:
            refinement_level = A.state[1]
            if refinement_level not in self.best_node:
                self.best_node[refinement_level] = A
                return True
            else:
                curr_best_node = self.best_node[refinement_level]
                if f(curr_best_node) > f(A):
                    # update the best node for this refinement level
                    self.best_node[refinement_level] = A
                    return True
                else:
                    print "Not adding node", A, "to frontier"
                    return False
        else:
            return True


class Search(object):
    graph = {}
    final_plan = {}
    target_node = None

    def __init__(self, G):
        self.G = G
        self.map_input_graph()
        self.problem = GraphProblem('S', 'G', self.graph)
        # No heuristics in f ==> uniform cost search algorithm
        self.best_first_graph_search(self.problem, lambda node: node.path_cost)
        self.generate_final_plan()

    def map_input_graph(self):
        (V, E) = self.G
        graph = {}
        for v in V:
            for (v1, v2) in E:
                if v1 == v:
                    if v not in graph:
                        graph[v] = {}
                    # TODO: make sure that their single weight metric for each edge
                    graph[v1][v2] = E[(v1, v2)]
        # TODO: take care of the corner cases
        self.graph = graph

    def generate_final_plan(self):
        self.final_plan = Path(self.graph, self.target_node.path)

    def best_first_graph_search(self, f):
        problem = self.problem
        f = memoize(f, 'f')
        node = Node(problem.initial)
        if problem.goal_test(node.state):
            return node
        frontier = PriorityQueue(min, f)
        frontier.append(node)
        explored = set()
        while frontier:
            print frontier, explored
            node = frontier.pop()
            if problem.goal_test(node.state):
                self.target_node = node
            explored.add(node.state)
            for child in node.expand(problem):
                if child.state not in explored and child not in frontier:
                    print "Adding child", child, "to the priority queue."
                    if problem.is_qualified(child, f):
                        frontier.append(child)
                elif child in frontier:
                    incumbent = frontier[child]
                    if f(child) < f(incumbent):
                        del frontier[incumbent]
                        frontier.append(child)

        print 'Failed to find the best path'