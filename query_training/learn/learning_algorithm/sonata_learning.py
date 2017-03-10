# Author: arpitg@cs.princeton.edu

from search import *
from utils import *

def DirectedGraph(dict=None):
    "Build a Graph where every edge (including future ones) goes both ways."
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
        return cost_so_far + (self.graph.get(A,B) or infinity)

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


def best_first_graph_search(problem, f):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
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
            return node
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
    return None


graph = DirectedGraph({('S'):{(1, 8):100, (1, 16):300, (1, 24):500, (1, 32):1000},
                   (1,8):{(2,16):250, (2,24):450, (2,32):500}, (1,16):{(2,24):200, (2,32):200}, (1,24):{(2,32):100},
                   (2,16):{(3,24):200, (3,32):200}, (2,24):{(3,32):100},
                   (3,24):{(4,32):100},
                   (1,32):{'G':1},(2,32):{'G':1},(3,32):{'G':1},(4,32):{'G':1}
                   })
print graph

problem = GraphProblem('S', 'G', graph)
out = best_first_graph_search(problem, lambda node: node.path_cost)
print out.path()
