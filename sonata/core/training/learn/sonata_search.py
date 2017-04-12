# author: arpitg@cs.princeton.edu

from sonata.core.training.learn.search import *
from sonata.core.training.learn.utils import *

from query_plan import QueryPlan

debug = False




class GraphProblem(Problem):
    "The problem of searching a graph from one node to another."
    def __init__(self, initial, goal, graph):
        Problem.__init__(self, initial, goal)
        self.graph = graph
        self.best_node = {}

    def actions(self, a):
        "The actions at a graph node are just its neighbors."
        # print "actions for a: ",self.graph
        # print "a: ",a
        out = self.graph.get(a).keys()
        # Sort the neighbor tuples, TODO: make sure we don't need more sophisticated sort operation
        out.sort()
        return out

    def result(self, state, action):
        """The result of going to a neighbor is just that neighbor."""
        return action

    def path_cost(self, cost_so_far, a, action, b):
        # print "path_cost:",a, B, cost_so_far
        return cost_so_far + (self.graph.get(a, b) or 0)

    def is_qualified(self, a, f):
        "Check whether the graph node is qualified to be a frontier node"
        # print a.state
        if len(a.state) > 1:
            refinement_level = a.state[1]
            if refinement_level not in self.best_node:
                self.best_node[refinement_level] = a
                return True
            else:
                curr_best_node = self.best_node[refinement_level]
                if f(curr_best_node) > f(a):
                    # update the best node for this refinement level
                    self.best_node[refinement_level] = a
                    return True
                else:
                    # print "Not adding node", a, "to frontier"
                    return False
        else:
            return True

    def goal_test(self, node):
        return node.state == self.goal


class Search(object):
    graph = {}
    final_plan = None
    target_node = None

    def __init__(self, G):
        self.G = G
        self.graph = map_input_graph(self.G)

        # TODO: hardcoding fix required
        self.problem = GraphProblem((0, 0, 0), (32, 0, 0), self.graph)
        # No heuristics in f ==> uniform cost search algorithm
        self.best_first_graph_search(lambda node: node.path_cost)
        if self.target_node is None:
            if debug: print "Failed to find the best path :("
        else:
            # print "Best path is", self.target_node.path()
            self.generate_final_plan()

    def generate_final_plan(self):
        self.final_plan = QueryPlan(self.graph, self.target_node.path())

    def best_first_graph_search(self, f):
        debug = True
        debug = False
        if debug: print self.graph.dict
        problem = self.problem
        f = memoize(f, 'f')
        node = Node(problem.initial)
        if debug: print "Initial Node", node
        if problem.goal_test(node):
            self.target_node = node
        frontier = PriorityQueue(min, f)
        frontier.append(node)
        explored = set()
        while frontier:
            # if debug: print frontier, explored
            node = frontier.pop()
            if debug: print "Exploring", node, node.path(), node.path_cost
            if problem.goal_test(node):
                # Check whether we need to update the target node
                if self.target_node is None:
                    self.target_node = node
                else:
                    curr_target_cost = QueryPlan(self.graph, self.target_node.path()).cost
                    new_target_cost = QueryPlan(self.graph, node.path()).cost
                    if debug: print "Current Target", self.target_node.path(), "cost:", curr_target_cost
                    if debug: print "New Target", node.path(), "cost:", new_target_cost
                    if new_target_cost < curr_target_cost:
                        if debug: print "Updated the target path"
                        self.target_node = node
                    else:
                        if debug: print "Target path not updated"
            else:
                # Don't add the node target node in explored set
                explored.add(node.state)

            for child in node.expand(problem):
                if child.state not in explored and child not in frontier:
                    if debug: print "adding child", child, "to frontier."
                    frontier.append(child)
                elif child in frontier:
                    incumbent = frontier[child]
                    if f(child) < f(incumbent):
                        # if debug: print "Deleting incumbent", incumbent, "from frontier"
                        # del frontier[incumbent]
                        if debug: print "adding child", child, "to frontier."
                        frontier.append(child)
