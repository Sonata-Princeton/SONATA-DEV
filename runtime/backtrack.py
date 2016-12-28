#!/usr/binput/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import random
import time
import sys

def swap(input, ind1, ind2):
    tmp = input[ind2]
    input[ind2] = input[ind1]
    input[ind1] = tmp
    return input

def permutation(input, start, end ):
    if (start == end ):
        print input
    else:
        for i in range(start , end + 1):

            swap(input, start , i )
            permutation(input , start + 1 , end )
            swap(input, start , i)

def get_all_possible_transits(a):
    transits = []
    ind = 1
    for elem1 in a:
        for elem2 in a[ind:]:
            transits.append((elem1, elem2))
        ind += 1
    return transits

def generate_costs(a):
    costs = {}
    low = 1000
    high = 2000
    ind1 = 1
    for elem1 in a:
        low = int(low/ind1)
        high = int(high/ind1)
        ind2 = 1
        for elem2 in a[ind1:]:
            low = low*ind2
            high = high*ind2
            #print (elem1, elem2), low, high
            costs[(elem1, elem2)] = random.randint(low, high)
            ind2 += 1
        ind1 += 1
        low = 1000
        high = 2000
    #print costs
    return costs


def get_plan_cost(plan, cost=0):
    if len(plan) > 1:
        cost += costs[tuple([plan[0],plan[1]])]+get_plan_cost(plan[1:],cost)
    else:
        return 0
    return cost

def check_transit(prev, elem, costs):
    # TODO Make this more reasonable
    if (tuple([prev,elem])) in costs:
        return True
    else:
        return False




def get_refinement_plan(final_level, a, costs, plans, query_id, subtree, query_2_final_plan, ref_levels):
    #print "Function called for", query_id, final_level, subtree
    root = 0
    level = 0
    levels = range(0,len(a)+1)
    plans = {}
    node_2_plan = {}
    node_2_all_plans = {}
    plan_2_cost = {}
    explore_further = {}

    for curr_level in levels:

        if curr_level == 0:
            explore_further[curr_level] = {(1,0):0}
            node_2_all_plans[curr_level] = {}
            node_2_all_plans[curr_level][(1,0)] = [(1,0)]


        next_level = curr_level+1
        if curr_level in explore_further:
            #print curr_level, explore_further
            explore_further[next_level] = {}
            for prev_plan_id, prev in explore_further[curr_level]:
                for plan_id, elem in a:
                    is_transit_allowed = False
                    if ((prev_plan_id, plan_id), (prev,elem)) in costs:
                        is_transit_allowed = True
                    #print curr_level, (prev_plan_id, plan_id), (prev,elem), is_transit_allowed
                    if is_transit_allowed:
                        #print curr_level, prev, elem, is_transit_allowed
                        curr_plan_cost = 0
                        if len(subtree.keys()) > 0:
                            for qid in subtree:
                                c = {}
                                st = subtree[qid]
                                ps = []
                                fl = elem
                                if qid not in memoized_plans:
                                    memoized_plans[qid] = {}
                                if elem not in memoized_plans[qid]:


                                    for p1 in query_2_plans[qid]:
                                        for p2 in query_2_plans[qid]:
                                            for transit in query_2_cost[qid][(p1,p2)]:
                                                c[((p1,p2), transit)] = query_2_cost[qid][(p1,p2)][transit]
                                    #print c
                                    for pid in query_2_plans[qid]:
                                        for e in ref_levels:
                                            if e > fl:
                                                break
                                            else:
                                                ps.append((pid, e))

                                    fp, cst = get_refinement_plan(fl, ps, c, query_2_plans[qid], qid, st, query_2_final_plan, ref_levels)
                                    memoized_plans[qid][elem] = (fp, cst)
                                else:
                                    (fp, cst) = memoized_plans[qid][elem]

                                curr_plan_cost += cst
                                #print qid, fp, cst

                        prev_plan = node_2_all_plans[curr_level][(prev_plan_id, prev)]
                        if tuple(prev_plan) in plan_2_cost:
                            prev_plan_cost = plan_2_cost[tuple(prev_plan)]
                        else:
                            prev_plan_cost = get_plan_cost(tuple(prev_plan))

                        curr_plan = prev_plan+[(plan_id, elem)]
                        curr_plan_cost += costs[((prev_plan_id, plan_id), (prev,elem))]+prev_plan_cost
                        if (plan_id, elem) not in node_2_plan:
                            node_2_plan[(plan_id, elem)] = curr_plan
                            explore_further[next_level][(plan_id, elem)] = 0
                        else:
                            curr_cost = plan_2_cost[tuple(node_2_plan[(plan_id, elem)])]
                            new_cost = curr_plan_cost
                            #print "For Query", query_id, final_level
                            #print "Current Plan:", node_2_plan[(plan_id, elem)]," Cost:", plan_2_cost[tuple(node_2_plan[(plan_id, elem)])]
                            #print "New Plan:", curr_plan, " Cost:", curr_plan_cost
                            if new_cost < curr_cost:
                                #print "Updating Plan for Node", elem
                                node_2_plan[(plan_id, elem)] = curr_plan
                                explore_further[next_level][(plan_id, elem)] = 0

                        if next_level not in node_2_all_plans:
                            node_2_all_plans[next_level] = {}
                        node_2_all_plans[next_level][(plan_id, elem)] = curr_plan


                        #print curr_plan, curr_plan_cost, node_2_plan
                        #print tuple(curr_plan)
                        plan_2_cost[tuple(curr_plan)] = curr_plan_cost
    #print node_2_plan
    min_cost = sys.maxint
    final_plan = []
    for (plan, elem) in node_2_plan:
        #print final_level, elem, elem == final_level
        if elem == final_level:
            candidate_plan = node_2_plan[(plan, elem)]
            cost = plan_2_cost[tuple(candidate_plan)]
            #print "Final Candidate Plans", candidate_plan, cost
            if cost < min_cost:
                final_plan = candidate_plan
                min_cost = cost

    #print "Final plan", final_plan, " cost", min_cost
    if query_id not in query_2_final_plan:
        query_2_final_plan[query_id] = {}
    query_2_final_plan[query_id][final_level] = (final_plan, min_cost)

    print query_id, final_level, final_plan, min_cost
    return (final_plan,min_cost)


def generate_query_tree(depth, all_queries, qid = 1):
    query_tree = {}

    if depth > 0:
        qid_l = 2*qid
        all_queries.append(qid_l)
        query_tree[qid_l] = generate_query_tree(depth-1, all_queries, qid_l)

        qid_r = 2*qid+1
        all_queries.append(qid_r)
        query_tree[qid_r] = generate_query_tree(depth-1, all_queries, qid_r)

    #print depth, qid, query_tree
    return query_tree




if __name__ == '__main__':
    #print node_2_plan
    memoized_plans = {}
    # Tuning parameters
    query_tree_depth = 1
    max_plans = 3
    ref_levels = range(0,101,50)


    a = ref_levels
    plans = range(1,4)


    query_tree = {}
    all_queries = [1]

    query_tree[1] = generate_query_tree(query_tree_depth, all_queries)
    all_queries.sort()
    #print all_queries
    print query_tree

    #query_tree = {1:{2:{}, 3:{}}}
    query_2_cost = {}
    query_2_plans = {}
    query_2_final_plan = {}
    for query_id in all_queries:
        if query_id not in query_2_cost:
            query_2_cost[query_id] = {}
        n_plans = random.randint(1, max_plans)
        query_2_plans[query_id] = range(1,n_plans+1)

        for p1 in range(1,n_plans+1):
            for p2 in range(1,n_plans+1):
                query_2_cost[query_id][(p1,p2)] = generate_costs(a)

    print query_2_plans
    #print query_2_cost.keys()
    start = time.time()
    for query_id in query_tree:
        costs = {}
        subtree = query_tree[query_id]
        possibility_space = []
        final_level = a[-1]
        for plan_id in query_2_cost[query_id]:
            for transit in query_2_cost[query_id][plan_id]:
                costs[(plan_id, transit)] = query_2_cost[query_id][plan_id][transit]

        for plan_id in query_2_plans[query_id]:
            for elem in a:
                if elem > final_level:
                    break
                else:
                    possibility_space.append((plan_id, elem))

        final_plan, cost = get_refinement_plan(final_level, possibility_space, costs, query_2_plans[query_id], query_id, subtree, query_2_final_plan, ref_levels)

        break
    print "Took", time.time()-start, "seconds"
