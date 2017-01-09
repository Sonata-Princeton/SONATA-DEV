#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import random
import sys
import time
import networkx as nx

def swap(input, ind1, ind2):
    tmp = input[ind2]
    input[ind2] = input[ind1]
    input[ind1] = tmp
    return input


def permutation(input, start, end):
    if start == end:
        print input
    else:
        for i in range(start, end + 1):
            swap(input, start, i)
            permutation(input, start + 1, end)
            swap(input, start, i)


def get_all_possible_transits(a):
    transits = []
    ind = 1
    for elem1 in a:
        for elem2 in a[ind:]:
            transits.append((elem1, elem2))
        ind += 1
    return transits


def generate_costs(p1, p2, ref_levels):
    """

    :rtype: object
    """
    costs = {}
    plan_id = 1+int(str(p2), 2)
    # Higher the plan_id, higher should be the cost
    low = 1000*plan_id+1
    high = 2000*plan_id
    ind1 = 1
    for elem1 in ref_levels:
        low = int(low / ind1)
        high = int(high / ind1)
        ind2 = 1
        for elem2 in ref_levels[ind1:]:
            low = low * ind2
            high = high * ind2
            # print (elem1, elem2), low, high
            costs[(elem1, elem2)] = random.randint(low, high)
            ind2 += 1
        ind1 += 1
        low = 1000
        high = 2000
    # print costs
    return costs

def get_plan_cost(plan, cost=0):
    if len(plan) > 1:
        cost += costs[tuple([plan[0], plan[1]])] + get_plan_cost(plan[1:], cost)
    else:
        return 0
    return cost

def generate_query_tree(depth, all_queries, qid=1):
    query_tree = {}

    if depth > 0:
        qid_l = 2 * qid
        all_queries.append(qid_l)
        query_tree[qid_l] = generate_query_tree(depth - 1, all_queries, qid_l)

        qid_r = 2 * qid + 1
        all_queries.append(qid_r)
        query_tree[qid_r] = generate_query_tree(depth - 1, all_queries, qid_r)

    # print depth, qid, query_tree
    return query_tree


def get_possibility_space(start_level, final_level, ref_levels, plans):
    possibility_space = []
    for plan_id in plans:
        for elem in ref_levels:
            if elem > final_level:
                break
            elif elem > start_level:
                possibility_space.append((plan_id, elem))
    return possibility_space


def check_transit(prev, elem, costs):
    # TODO Make this more reasonable
    if (tuple([prev, elem])) in costs:
        return True
    else:
        return False


def get_refinement_plan(start_level, final_level, query_id, ref_levels, query_2_plans, query_tree, query_2_cost,
                        query_2_final_plan, memoized_plans):
    # print "Function called for", query_id, final_level, subtree
    root = 0

    node_2_plan = {}
    node_2_all_plans = {}
    plan_2_cost = {}
    explore_further = {}
    # Enumerate the possibility space given the final level
    possibility_space = get_possibility_space(start_level, final_level, ref_levels, query_2_plans[query_id])
    subtree = query_tree[query_id]
    costs = query_2_cost[query_id]
    levels = range(root, len(possibility_space) + 1)
    plans = query_2_plans[query_id]

    for curr_level in levels:

        if curr_level == 0:
            explore_further[curr_level] = {(plans[0], root): 0}
            node_2_all_plans[curr_level] = {}
            node_2_all_plans[curr_level][(plans[0], 0)] = [(plans[0], 0)]

        next_level = curr_level + 1
        if curr_level in explore_further:
            # print curr_level, explore_further
            explore_further[next_level] = {}
            for prev_plan_id, prev in explore_further[curr_level]:
                for plan_id, elem in possibility_space:
                    is_transit_allowed = False
                    if ((prev_plan_id, plan_id), (prev, elem)) in costs:
                        is_transit_allowed = True
                    # print curr_level, (prev_plan_id, plan_id), (prev,elem), is_transit_allowed
                    if is_transit_allowed:
                        # print curr_level, prev, elem, is_transit_allowed
                        candidate_plan_cost = 0
                        if len(subtree.keys()) > 0:
                            # Explore the refinement plan for each child tree of this query
                            for qid in subtree:
                                if len(query_2_plans[qid]) > 0:
                                    if qid not in memoized_plans:
                                        memoized_plans[qid] = {}
                                    if elem not in memoized_plans[qid]:
                                        fp, cst = get_refinement_plan(prev, elem, qid, ref_levels, query_2_plans,
                                                                      subtree, query_2_cost, query_2_final_plan,
                                                                      memoized_plans)
                                        memoized_plans[qid][(prev, elem)] = (fp, cst)
                                    else:
                                        # We don't need to explore again the subtree for same refinement level
                                        (fp, cst) = memoized_plans[qid][(prev, elem)]

                                    # Add the cost of refining the subtree to this refinement plan's cost
                                    candidate_plan_cost += cst
                                    # print qid, fp, cst

                        prev_plan = node_2_all_plans[curr_level][(prev_plan_id, prev)]
                        if tuple(prev_plan) in plan_2_cost:
                            prev_plan_cost = plan_2_cost[tuple(prev_plan)]
                        else:
                            prev_plan_cost = get_plan_cost(tuple(prev_plan))

                        cand_plan = prev_plan + [(plan_id, elem)]
                        candidate_plan_cost += costs[((prev_plan_id, plan_id), (prev, elem))] + prev_plan_cost
                        if (plan_id, elem) not in node_2_plan:
                            node_2_plan[(plan_id, elem)] = cand_plan
                            explore_further[next_level][(plan_id, elem)] = 0
                        else:

                            curr_cost = plan_2_cost[tuple(node_2_plan[(plan_id, elem)])]
                            new_cost = candidate_plan_cost
                            # print "For Query", query_id, final_level
                            # print "Current Plan:", node_2_plan[(plan_id, elem)]," Cost:", plan_2_cost[tuple(node_2_plan[(plan_id, elem)])]
                            # print "New Plan:", curr_plan, " Cost:", curr_plan_cost
                            if new_cost < curr_cost:
                                # We need to update the plan for this node
                                # print "Updating Plan for Node", elem
                                node_2_plan[(plan_id, elem)] = cand_plan
                                explore_further[next_level][(plan_id, elem)] = 0

                        if next_level not in node_2_all_plans:
                            node_2_all_plans[next_level] = {}
                        node_2_all_plans[next_level][(plan_id, elem)] = cand_plan

                        # print curr_plan, curr_plan_cost, node_2_plan
                        # print tuple(curr_plan)
                        plan_2_cost[tuple(cand_plan)] = candidate_plan_cost
    # print node_2_plan
    min_cost = sys.maxint
    final_plan = []
    for (plan, elem) in node_2_plan:
        # print final_level, elem, elem == final_level
        if elem == final_level:
            candidate_plan = node_2_plan[(plan, elem)]
            cost = plan_2_cost[tuple(candidate_plan)]
            # print "Final Candidate Plans", candidate_plan, cost
            if cost < min_cost:
                final_plan = candidate_plan
                min_cost = cost

    # print "Final plan", final_plan, " cost", min_cost
    if query_id not in query_2_final_plan:
        query_2_final_plan[query_id] = {}
    query_2_final_plan[query_id][final_level] = (final_plan, min_cost)

    # print query_id, final_level, final_plan, min_cost
    return (final_plan, min_cost)


def get_refplan_dijkstra():
    pass


if __name__ == '__main__':
    # print node_2_plan
    memorized_plans = {}
    # Tuning parameters
    query_tree_depth = 0
    max_plans = 1
    ref_levels = range(0, 33, 8)

    a = ref_levels
    plans = range(1, 4)

    query_tree = {}
    all_queries = [1]

    # Binary tree representing query tree
    query_tree[1] = generate_query_tree(query_tree_depth, all_queries)

    all_queries.sort()
    # print all_queries
    # print query_tree

    # query_tree = {1:{2:{}, 3:{}}}
    query_2_cost = {}
    query_2_plans = {}
    query_2_final_plan = {}
    for query_id in all_queries:
        if query_id not in query_2_cost:
            query_2_cost[query_id] = {}
        # randomly select number of plans, i.e. number of paths in the partition tree
        n_plans = random.randint(1, max_plans)
        query_2_plans[query_id] = range(1, n_plans + 1)
        if query_id == 3:
            n_plans = 0
            query_2_plans[query_id] = []

        for p1 in range(1, n_plans + 1):
            for p2 in range(1, n_plans + 1):
                # For each path combination for each query we generate cost using the cost function above.
                tmp = generate_costs(ref_levels)
                for transit in tmp:
                    query_2_cost[query_id][(p1, p2), transit] = tmp[transit]

    # print query_2_plans
    # print query_2_cost
    # print query_2_cost.keys()
    start = time.time()

    for query_id in query_tree:
        # We start with the finest refinement level, as expressed in the original query
        final_plan, cost = get_refinement_plan(ref_levels[0], ref_levels[-1], query_id, ref_levels, query_2_plans,
                                               query_tree, query_2_cost, query_2_final_plan, memorized_plans)

        # Verify that the refinement search is not a complicated backtracking
        # problem. Instead, it cab be mapped as a simple shortest path problem.
        # TODO: update the get_refinement_plan() function to make it simpler
        G = nx.DiGraph()
        src_node = str('src')
        G.add_node(src_node)
        sink_node = str('sink')
        G.add_node(sink_node)
        query_id = 1

        for ref_level in range(1, len(ref_levels) + 1):
            for plan_id in query_2_plans[query_id]:
                for dimension in ref_levels[1:]:
                    node_name = str((ref_level, plan_id, dimension))
                    G.add_node(node_name)
                    print "Added node", node_name

        for ref_level in range(1, len(ref_levels)):
            for ((prev_plan, curr_plan), (prev_dim, curr_dim)) in query_2_cost[query_id]:
                if prev_dim != 0 and curr_dim != 0:
                    src = str((ref_level, prev_plan, prev_dim))
                    dst = str((ref_level + 1, curr_plan, curr_dim))
                    cost = query_2_cost[query_id][((prev_plan, curr_plan), (prev_dim, curr_dim))]
                    G.add_edge(src, dst, cost=cost)
                    print "Added edge", src, dst, cost

        ref_level = 1
        for plan_id in query_2_plans[query_id]:
            for dimension in ref_levels[1:]:
                dst = str((ref_level, plan_id, dimension))
                cost = query_2_cost[query_id][((1, plan_id), (0, dimension))]
                G.add_edge(src_node, dst, cost=cost)
                print "Added edge", src_node, dst, cost

        for ref_level in range(1, len(ref_levels) + 1):
            for plan_id in query_2_plans[query_id]:
                dimension = ref_levels[-1]
                src = str((ref_level, plan_id, dimension))
                G.add_edge(src, sink_node, cost=10)
                print "Added edge", src, sink_node, 0

        print(nx.shortest_path(G, source=src_node, target=sink_node, weight='cost'))

    print query_2_final_plan
    print "Took", time.time() - start, "seconds"
