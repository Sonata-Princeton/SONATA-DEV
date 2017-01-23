#!/usr/bin/python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import random
import sys
import time
import pickle
import networkx as nx

from query_engine.query_generator import *
from query_engine.sonata_queries import *
from data.plotlib import *

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
    low = 1000+1
    high = 2000
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

def get_plan_cost(costs, plan, cost=0):
    #print "Get Plan Cost func. called", plan
    if len(plan) > 1:
        cost += costs[tuple([plan[0], plan[1]])] + get_plan_cost(costs, plan[1:], cost)
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
                        query_2_final_plan, memoized_plans, mapped_plan):

    root = start_level

    node_2_plan = {}
    node_2_all_plans = {}
    plan_2_cost = {}
    explore_further = {}
    if query_id not in mapped_plan:
        mapped_plan[query_id] = {}
    # Enumerate the possibility space given the final level
    possibility_space = get_possibility_space(start_level, final_level, ref_levels, query_2_plans[query_id])
    subtree = query_tree[query_id]
    costs = query_2_cost[query_id]
    levels = range(0, len(possibility_space) + 1)
    plans = query_2_plans[query_id]

    #print "Function called for", query_id
    #print "Start level", start_level, "final level", final_level
    #print "Possibility Space", possibility_space, levels
    #print costs

    for curr_level in levels:
        if curr_level == 0:
            if root == 0:
                explore_further[curr_level] = {(plans[0], root): 0}
                node_2_all_plans[curr_level] = {}
                node_2_all_plans[curr_level][(plans[0], root)] = [(plans[0], root)]
            elif root > 0:
                explore_further[curr_level] = {}
                node_2_all_plans[curr_level] = {}
                for plan in plans:
                    explore_further[curr_level][(plan, root)] = 0
                    node_2_all_plans[curr_level][(plan, root)] = [(plan, root)]


        #print "Explore Further", explore_further
        next_level = curr_level + 1
        if curr_level in explore_further:
            #print curr_level, explore_further[curr_level]
            explore_further[next_level] = {}
            for prev_plan_id, prev_iter_level in explore_further[curr_level]:
                for plan_id, curr_iter_level in possibility_space:
                    is_transit_allowed = False
                    if ((prev_plan_id, plan_id), (prev_iter_level, curr_iter_level)) in costs:
                        is_transit_allowed = True
                    # print curr_level, (prev_plan_id, plan_id), (prev,elem), is_transit_allowed
                    if is_transit_allowed:
                        # print curr_level, prev, elem, is_transit_allowed
                        if (prev_iter_level, curr_iter_level) not in mapped_plan[query_id]:
                            mapped_plan[query_id][(prev_iter_level, curr_iter_level)] = {}
                        candidate_plan_cost = 0
                        if len(subtree.keys()) > 0:
                            # Explore the refinement plan for each child tree of this query
                            for qid in subtree:
                                if len(query_2_plans[qid]) > 0:
                                    if qid not in memoized_plans:
                                        memoized_plans[qid] = {}
                                    if curr_iter_level not in memoized_plans[qid]:
                                        fp, cst = get_refinement_plan(prev_iter_level, curr_iter_level, qid, ref_levels, query_2_plans,
                                                                      subtree, query_2_cost, query_2_final_plan,
                                                                      memoized_plans, mapped_plan)
                                        memoized_plans[qid][(prev_iter_level, curr_iter_level)] = (fp, cst)
                                    else:
                                        # We don't need to explore again the subtree for same refinement level
                                        (fp, cst) = memoized_plans[qid][(prev_iter_level, curr_iter_level)]


                                    # Add the cost of refining the subtree to this refinement plan's cost
                                    #print "Final plan for child", qid, "between", (prev_iter_level,curr_iter_level), "is",fp, cst
                                    candidate_plan_cost += cst
                                    # print qid, fp, cst
                                    mapped_plan[query_id][(prev_iter_level,curr_iter_level)][qid] = (fp,cst)

                        prev_plan = node_2_all_plans[curr_level][(prev_plan_id, prev_iter_level)]
                        if tuple(prev_plan) in plan_2_cost:
                            prev_plan_cost = plan_2_cost[tuple(prev_plan)]
                        else:
                            #print plan_2_cost
                            prev_plan_cost = get_plan_cost(costs, tuple(prev_plan))

                        cand_plan = prev_plan + [(plan_id, curr_iter_level)]
                        candidate_plan_cost += costs[((prev_plan_id, plan_id), (prev_iter_level, curr_iter_level))] + prev_plan_cost
                        if (plan_id, curr_iter_level) not in node_2_plan:
                            node_2_plan[(plan_id, curr_iter_level)] = cand_plan
                            explore_further[next_level][(plan_id, curr_iter_level)] = 0
                        else:

                            curr_cost = plan_2_cost[tuple(node_2_plan[(plan_id, curr_iter_level)])]
                            new_cost = candidate_plan_cost
                            #print "For Query", query_id, start_level, final_level

                            if new_cost < curr_cost:
                                # We need to update the plan for this node
                                #print "Current Plan:", node_2_plan[(plan_id, curr_iter_level)]," Cost:", curr_cost
                                #print "New Plan:", cand_plan, " Cost:", new_cost
                                #print "Updating Plan for Node", curr_iter_level
                                node_2_plan[(plan_id, curr_iter_level)] = cand_plan
                                explore_further[next_level][(plan_id, curr_iter_level)] = 0

                        if next_level not in node_2_all_plans:
                            node_2_all_plans[next_level] = {}
                        node_2_all_plans[next_level][(plan_id, curr_iter_level)] = cand_plan

                        # print curr_plan, curr_plan_cost, node_2_plan
                        # print tuple(curr_plan)
                        plan_2_cost[tuple(cand_plan)] = candidate_plan_cost
    #print node_2_plan
    min_cost = sys.maxint
    final_plan = []
    for (plan, curr_iter_level) in node_2_plan:
        #print final_level, elem, elem == final_level
        if curr_iter_level == final_level:
            candidate_plan = node_2_plan[(plan, curr_iter_level)]
            cost = plan_2_cost[tuple(candidate_plan)]
            #print "Final Candidate Plans", candidate_plan, cost
            if cost < min_cost:
                final_plan = candidate_plan
                min_cost = cost

    #print "Final plan", query_id, (start_level, final_level), final_plan, " cost", min_cost
    if query_id not in query_2_final_plan:
        query_2_final_plan[query_id] = {}
    query_2_final_plan[query_id][(start_level,final_level)] = (final_plan, min_cost)

    # print query_id, final_level, final_plan, min_cost
    return (final_plan, min_cost)


def generate_query_in_mapping(start_level, final_level, query_2_final_plan, qid, query_tree):
    out = []
    #print "Exploring", qid, start_level, final_level,  "input", out, query_tree

    if qid in query_2_final_plan:
        #print qid
        ref_plans, cost = query_2_final_plan[qid][(start_level, final_level)]
        ref_plans_to_explore = ref_plans[1:]
        if start_level == 0 and len(ref_plans_to_explore) > 1:
            x = ref_plans[0]
            y = ref_plans[1]
            children = query_tree[qid].keys()
            children.sort()
            if len(children) > 0:
                left_child = children[0]

                subtree = {left_child: query_tree[qid][left_child]}
                left_out = generate_query_in_mapping(x[1], y[1], query_2_final_plan, left_child, subtree)
                out = left_out + out

        if len(ref_plans_to_explore) > 1:
            refs = zip(ref_plans_to_explore, ref_plans_to_explore[1:])
            x_prev = ref_plans[0]
            for (x, y) in refs:
                out.append((qid,(x[0],(x_prev[1],x[1]))))
                children = query_tree[qid].keys()
                children.sort()
                if len(children) > 0:
                    left_child = children[0]
                    subtree = {left_child: query_tree[qid][left_child]}
                    left_out = generate_query_in_mapping(x[1], y[1], query_2_final_plan, left_child, subtree)
                    out += left_out
                out.append((qid,(y[0],(x[1],y[1]))))
                x_prev = x
        else:
            children = query_tree[qid].keys()
            children.sort()
            x = ref_plans[0]
            y = ref_plans[1]
            if len(children) > 0:
                left_child = children[0]
                subtree = {left_child: query_tree[qid][left_child]}
                left_out = generate_query_in_mapping(x[1], y[1], query_2_final_plan, left_child, subtree)
                out += left_out
            out.append((qid,(y[0],(x[1],y[1]))))

    return out




def get_refplan_dijkstra():
    pass

def normalize_qcost(qcost):
    normalized_qcost = {}
    Nmax = 0
    Bmax = 0
    # Learn the max B and N values across all queries
    for qid,data_out in qcost.iteritems():
        for (_, data_in) in data_out.iteritems():
            for ts,(b,n) in data_in.iteritems():
                if b > Bmax:
                    Bmax = b
                if n > Nmax:
                    Nmax = n

    # Normalize the b, n costs wrt Nmax and Bmax
    for qid in qcost:
        normalized_qcost[qid] = {}
        for (plan,transit) in qcost[qid]:
            normalized_qcost[qid][(plan,transit)] = {}
            for ts in qcost[qid][(plan, transit)]:
                (b,n) = qcost[qid][(plan, transit)][ts]
                normalized_qcost[qid][(plan,transit)][ts] = (float(b)/Bmax, float(n)/Nmax)

    return normalized_qcost

def get_ts_from_qcost(qcost):
    timestamps = {}
    for qid in qcost:
        for (plan,transit) in qcost[qid]:
            for ts in qcost[qid][(plan, transit)]:
                timestamps[ts] = 0
    return timestamps.keys()


def process_cost_data(fname_qg, fname_rq, fname_qcost, case):

    ref_levels = range(0, 33, 8)
    finest_plan = ref_levels[-1]
    alphas = [0, 0.0001, 0.001, 0.01, 0.05, 0.1, 0.2, 0.25, 0.3, .4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 0.99]
    alphas = [0.1]
    with open(fname_qg, 'r') as f:
        query_generator = pickle.load(f)
        queries = query_generator.composed_queries.values()

        with open(fname_rq, 'r') as f:
            refined_queries = pickle.load(f)
            print refined_queries
            query_cost = {}
            for qid in refined_queries:
                fname = fname_qcost+'/q_cost_1min_'+str(qid)+'.pickle'
                with open(fname, 'r') as f:
                    query_cost[qid] = pickle.load(f)
            if case == 4:
                fname = fname_qcost+'/q_worst_cost_CASE4_1min.pickle'
                with open(fname, 'r') as f:
                    query_worst_cost = pickle.load(f)
                    tmp = {}
                    for qid in query_worst_cost:
                        tmp[qid] = dict((x[0],x[1]) for x in query_worst_cost[qid])
                    query_worst_cost = tmp


            #qcost_normalized = normalize_qcost(query_cost)
            qcost_normalized = query_cost

            total_timestamps = get_ts_from_qcost(query_cost)

        training_timestamps = total_timestamps[:10]
        test_timestamps = total_timestamps[11:]


        final_plan_sequences = {}

        # First learn the refinement and partitioning plan for each query, and alpha given training data
        for query in queries[:]:
            final_plan_sequences[query.qid] = {}
            for alpha in alphas:
                query.alpha = alpha
                query.training_timestamps = training_timestamps
                query.qcost = qcost_normalized
                query.get_query_tree()
                query.get_all_queries()
                query.get_partition_plans()
                query.get_cost(ref_levels)
                query.get_refinement_plan(ref_levels)

                query.query_in_mapping = {}
                final_level = ref_levels[-1]
                final_plan_sequence = rs.generate_query_in_mapping(ref_levels[0], final_level, query.query_2_final_plan, query.qid,
                                                   query.query_tree)

                final_plan_sequences[query.qid][alpha] = final_plan_sequence
        #return 0,0
        if case in [1, 2, 3]:

            output = {}
            # Now estimate the performance gains
            for ts in test_timestamps[1:]:
                for query in queries[:]:
                    # estimate Nmax, and Bmax
                    if query.qid not in output:
                        output[query.qid] = {}


                    query.get_all_queries()
                    all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
                    N_max = 0
                    B_max = 0
                    for q in all_queries:
                        plans = query.query_2_plans[q]
                        assert (query_cost[query.qid][(plans[-1],(0,8))][ts] == query_cost[query.qid][(plans[-1],(0,32))][ts])
                        N_max += query_cost[q][(plans[-1],(0,32))][ts][1]
                        B_max += query_cost[q][(plans[0],(0,32))][ts][0]


                    print "For query", query.qid, query.keys, "time", ts, "Nmax", N_max, "Bmax", B_max
                    for alpha in alphas:
                        if alpha not in output[query.qid]:
                            output[query.qid][alpha] = {}
                        final_plan_sequence = final_plan_sequences[query.qid][alpha]
                        ctr = 1
                        N = 0
                        B = 0
                        for (q_id, (part_plan,ref_transit)) in final_plan_sequence:
                            #print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)].values()[0]
                            N += query_cost[q_id][(part_plan,ref_transit)][ts][1]
                            B += query_cost[q_id][(part_plan,ref_transit)][ts][0]
                            ctr += 1

                        print ts, "N", N, N_max, "Gain", float(N)/N_max, alpha
                        print ts, "B", B, B_max, "Gain", float(B)/B_max, alpha
                        output[query.qid][alpha][ts] = ((N,N_max), (B,B_max))

        else:
            print "Analysing data for Case 4"
            output = {}
            # Now estimate the performance gains
            for ts in test_timestamps[1:]:
                for query in queries[:]:
                    # estimate Nmax, and Bmax
                    if query.qid not in output:
                        output[query.qid] = {}


                    query.get_all_queries()
                    all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
                    all_queries.sort(reverse=True)
                    N_max = 0
                    B_max = 0
                    for q in all_queries:
                        plans = query.query_2_plans[q]
                        #assert (query_cost[query.qid][(plans[-1],(0,8))][ts] == query_cost[query.qid][(plans[-1],(0,32))][ts])
                        N_max += query_cost[all_queries[0]][(plans[-1],(0,32))][ts][1]
                        #B_max += query_cost[q][(plans[0],(0,32))][ts][0]
                        #print query_worst_cost
                        if ts in query_worst_cost[q]:
                            B_max += query_worst_cost[q][ts]
                            print "Worst Buckets", q, query_worst_cost[q][ts]


                    print "For query", query.qid, query.keys, "time", ts, "Nmax", N_max, "Bmax", B_max
                    for alpha in alphas:
                        if alpha not in output[query.qid]:
                            output[query.qid][alpha] = {}
                        final_plan_sequence = final_plan_sequences[query.qid][alpha]
                        ctr = 1
                        N = 0
                        B = 0
                        for (q_id, (part_plan,ref_transit)) in final_plan_sequence:
                            #print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)].values()[0]
                            N += query_cost[q_id][(part_plan,ref_transit)][ts][1]
                            B += query_cost[q_id][(part_plan,ref_transit)][ts][0]
                            ctr += 1

                        print ts, "N", N, N_max, "Gain", float(N)/N_max, alpha
                        print ts, "B", B, B_max, "Gain", float(B)/B_max, alpha
                        output[query.qid][alpha][ts] = ((N,N_max), (B,B_max))

        return output, final_plan_sequences


def get_static_plan_costs(alphas, ref_levels, queries, query_cost, query_worst_cost, test_timestamps):
    static_plan_sequences_sp = {} # (q_id, (part_plan, ref_transit))
    static_plan_sequences_dp = {} # (q_id, (part_plan, ref_transit))
    for query in queries:
        static_plan_sequences_sp[query.qid] = []
        static_plan_sequences_dp[query.qid] = []
        query.get_all_queries()
        all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
        all_queries.sort(reverse=True)
        print query.qid, query.query_2_plans.keys()
        prev_level = 0
        #ref_levels = [0,8,32]
        for ref_level in ref_levels[1:]:
            for q in all_queries:
                print ref_level, q
                plans = query.query_2_plans[q]

                static_plan_sequences_sp[query.qid].append((q,(plans[-1],(prev_level, ref_level))))
                static_plan_sequences_dp[query.qid].append((q,(plans[0],(prev_level, ref_level))))
            prev_level = ref_level

    print static_plan_sequences_dp, static_plan_sequences_sp
    output_static_dp = {}
    output_static_sp = {}
    # Now estimate the performance gains
    for ts in test_timestamps[:]:
        for query in queries[:]:
            # estimate Nmax, and Bmax
            if query.qid not in output_static_dp:
                output_static_dp[query.qid] = {}
                output_static_sp[query.qid] = {}

            query.get_all_queries()
            all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
            all_queries.sort(reverse=True)
            N_max = 0
            B_max = 0
            for q in all_queries:
                plans = query.query_2_plans[q]
                #assert (query_cost[query.qid][(plans[-1],(0,8))][ts] == query_cost[query.qid][(plans[-1],(0,32))][ts])
                N_max += query_cost[all_queries[0]][(plans[-1],(0,32))][ts][1]
                #B_max += query_cost[q][(plans[0],(0,32))][ts][0]
                #print query_worst_cost
                if ts in query_worst_cost[q]:
                    B_max += query_worst_cost[q][ts]
                print "Worst Buckets", q, query_worst_cost[q][ts]


            print "For query", query.qid, query.keys, "time", ts, "Nmax", N_max, "Bmax", B_max
            for alpha in alphas:
                if alpha not in output_static_dp[query.qid]:
                    output_static_dp[query.qid][alpha] = {}
                    output_static_sp[query.qid][alpha] = {}
                final_plan_sequence_dp = static_plan_sequences_dp[query.qid]
                final_plan_sequence_sp = static_plan_sequences_sp[query.qid]

                ctr = 1
                N = 0
                B = 0
                for (q_id, (part_plan,ref_transit)) in final_plan_sequence_dp:
                    print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)][ts]
                    N += query_cost[q_id][(part_plan,ref_transit)][ts][1]
                    B += query_cost[q_id][(part_plan,ref_transit)][ts][0]
                    ctr += 1

                print ts, "N", N, N_max, "Gain", float(N)/N_max, alpha
                print ts, "B", B, B_max, "Gain", float(B)/B_max, alpha
                output_static_dp[query.qid][alpha][ts] = ((N,N_max), (B,B_max), ctr-1)

                N = 0
                B = 0
                ctr = 1
                for (q_id, (part_plan,ref_transit)) in final_plan_sequence_sp:
                    print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)][ts]
                    N += query_cost[q_id][(part_plan,ref_transit)][ts][1]
                    B += query_cost[q_id][(part_plan,ref_transit)][ts][0]
                    ctr += 1

                print ts, "N", N, N_max, "Gain", float(N)/N_max, alpha
                print ts, "B", B, B_max, "Gain", float(B)/B_max, alpha
                output_static_sp[query.qid][alpha][ts] = ((N,N_max), (B,B_max), ctr-1)


                #break

    return output_static_dp, output_static_sp


def get_packets_for_alpha(query, alpha,ts, qcost, ref_levels):
    final_plan_sequences = {}
    query.alpha = alpha
    query.training_timestamps = [ts]
    query.qcost = qcost
    query.get_query_tree()
    query.get_all_queries()
    query.get_partition_plans()
    query.get_cost(ref_levels)
    query.get_refinement_plan(ref_levels)

    query.query_in_mapping = {}
    final_level = ref_levels[-1]
    final_plan_sequence = rs.generate_query_in_mapping(ref_levels[0], final_level, query.query_2_final_plan, query.qid,
                                                       query.query_tree)

    N = 0
    B = 0
    ctr = 1
    for (q_id, (part_plan,ref_transit)) in final_plan_sequence:
        #print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)][ts]
        N += qcost[q_id][(part_plan,ref_transit)][ts][1]
        B += qcost[q_id][(part_plan,ref_transit)][ts][0]
    return N

def get_buckets_for_alpha(query, alpha,ts, qcost, ref_levels):
    final_plan_sequences = {}
    query.alpha = alpha
    query.training_timestamps = [ts]
    query.qcost = qcost
    query.get_query_tree()
    query.get_all_queries()
    query.get_partition_plans()
    query.get_cost(ref_levels)
    query.get_refinement_plan(ref_levels)

    query.query_in_mapping = {}
    final_level = ref_levels[-1]
    final_plan_sequence = rs.generate_query_in_mapping(ref_levels[0], final_level, query.query_2_final_plan, query.qid,
                                                       query.query_tree)

    N = 0
    B = 0
    ctr = 1
    for (q_id, (part_plan,ref_transit)) in final_plan_sequence:
        #print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)][ts]
        N += qcost[q_id][(part_plan,ref_transit)][ts][1]
        B += qcost[q_id][(part_plan,ref_transit)][ts][0]
    return B

def get_alpha_for_packets(nmax, query, ts, query_cost, ref_levels, alpha_start = 0.0,
                          alpha_end = 1.0, alpha_mid = 0.5):

    N_start = get_packets_for_alpha(query, alpha_start, ts, query_cost, ref_levels)
    N_end = get_packets_for_alpha(query, alpha_end, ts, query_cost, ref_levels)
    N_mid = get_packets_for_alpha(query, alpha_mid, ts, query_cost, ref_levels)
    print "for ", nmax, alpha_start, N_start, alpha_mid, N_mid, alpha_end, N_end

    if (abs(alpha_start-alpha_mid)<0.001) and (abs(alpha_end-alpha_mid)<0.001):
        return alpha_start
    elif nmax == N_start:
        print "Returning", alpha_start
        return alpha_start
    elif nmax == N_mid:
        return alpha_mid
    elif nmax == N_end:
        return alpha_end
    elif N_start == N_mid and not (nmax > N_mid and nmax < N_end):
        return alpha_start
    elif N_mid == N_end and not (nmax > N_start and nmax < N_mid):
        return alpha_mid
    elif nmax > N_start and nmax < N_mid:
        alpha_end = alpha_mid
        alpha_mid = 0.5*(alpha_mid+alpha_start)
        return get_alpha_for_packets(nmax, query, ts, query_cost, ref_levels, alpha_start, alpha_end, alpha_mid)
    elif nmax > N_mid and nmax < N_end:
        alpha_start = alpha_mid
        alpha_mid = 0.5*(alpha_mid+alpha_end)
        return get_alpha_for_packets(nmax, query, ts, query_cost, ref_levels, alpha_start, alpha_end, alpha_mid)
    elif nmax < N_start:
        return 0.0
    elif nmax > N_end:
        return 1.0

def learn_alpha_for_packets(queries, training_timestamps, query_cost, ref_levels):
    learned_nfrac_2_alpha = {}
    N_range = [0, 0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 1.0]

    for query in queries:
        learned_nfrac_2_alpha[query.qid] = {}
        query.get_all_queries()
        all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
        all_queries.sort(reverse=True)

        for ts in training_timestamps:
            learned_nfrac_2_alpha[query.qid][ts] = {}
            N_max = 0
            for q in all_queries:
                plans = query.query_2_plans[q]
                #assert (query_cost[query.qid][(plans[-1],(0,8))][ts] == query_cost[query.qid][(plans[-1],(0,32))][ts])
                N_max += query_cost[all_queries[0]][(plans[-1],(0,32))][ts][1]

            print "Nmax", N_max

            for n_frac in N_range:
                nmax = N_max*n_frac
                print "Searching for", nmax
                alpha = get_alpha_for_packets(nmax, query, ts, query_cost, ref_levels)
                learned_nfrac_2_alpha[query.qid][ts][n_frac] = alpha
                print "Completed for", n_frac, query.qid, ts, " learnt", alpha

    with open('data/case_0_learned_nfrac_2_alpha.pickle','w') as f:
        pickle.dump(learned_nfrac_2_alpha,f)

    return learned_nfrac_2_alpha


def get_alpha_for_buckets(bmax, query, ts, query_cost, ref_levels,
                          alpha_start = 0.0, alpha_end = 1.0, alpha_mid = 0.5):
    B_start = get_buckets_for_alpha(query, alpha_start, ts, query_cost, ref_levels)
    B_end = get_buckets_for_alpha(query, alpha_end, ts, query_cost, ref_levels)
    B_mid = get_buckets_for_alpha(query, alpha_mid, ts, query_cost, ref_levels)
    print "for ", bmax, alpha_start, B_start, alpha_mid, B_mid, alpha_end, B_end

    if (round(alpha_start,3) == round(alpha_mid,3)) and (round(alpha_mid,3) == round(alpha_end,3)):
        return alpha_start
    if bmax == B_start:
        print "Returning", alpha_start
        return alpha_start
    elif bmax == B_mid:
        return alpha_mid
    elif bmax == B_end:
        return alpha_end
    elif B_start == B_mid and not (bmax > B_mid and bmax < B_end):
        return alpha_start
    elif B_mid == B_end and not (bmax > B_start and bmax < B_mid):
        return alpha_mid
    elif bmax > B_start and bmax < B_mid:
        alpha_end = alpha_mid
        alpha_mid = 0.5*(alpha_mid+alpha_start)
        return get_alpha_for_buckets(bmax, query, ts, query_cost, ref_levels, alpha_start, alpha_end, alpha_mid)
    elif bmax > B_mid and bmax < B_end:
        alpha_start = alpha_mid
        alpha_mid = 0.5*(alpha_mid+alpha_end)
        return get_alpha_for_buckets(bmax, query, ts, query_cost, ref_levels, alpha_start, alpha_end, alpha_mid)
    else:
        return 0


def learn_alpha_for_buckets(queries, training_timestamps, query_cost, ref_levels, query_worst_cost):
    learned_bfrac_2_alpha = {}
    B_range = [0, 0.01, 0.1, 0.25, 0.5, 0.75, 1.0]

    for query in queries:
        learned_bfrac_2_alpha[query.qid] = {}
        query.get_all_queries()
        all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
        all_queries.sort(reverse=True)

        for ts in training_timestamps:
            learned_bfrac_2_alpha[query.qid][ts] = {}
            B_max = 0
            for q in all_queries:
                plans = query.query_2_plans[q]
                #assert (query_cost[query.qid][(plans[-1],(0,8))][ts] == query_cost[query.qid][(plans[-1],(0,32))][ts])
                if ts in query_worst_cost[q]:
                    B_max += query_worst_cost[q][ts]

            print "B_max", B_max

            for b_frac in B_range:
                bmax = B_max*b_frac
                print "Searching for", bmax
                alpha = get_alpha_for_buckets(bmax, query, ts, query_cost, ref_levels)
                learned_bfrac_2_alpha[query.qid][ts][b_frac] = alpha
                print "Completed for", b_frac, query.qid, ts, " learnt", alpha

    with open('data/case_0_learned_bfrac_2_alpha.pickle','w') as f:
        pickle.dump(learned_bfrac_2_alpha,f)

    return learned_bfrac_2_alpha


def get_cost_savings(fname_qg, fname_rq, fname_qcost):
    ref_levels = range(0, 33, 4)
    finest_plan = ref_levels[-1]
    #alphas = [0, 0.0001, 0.001, 0.01, 0.05, 0.1, 0.2, 0.25, 0.3, .4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 0.99]
    alphas = [0.01, 0.1, 0.25, 0.5, 0.75]
    #alphas = [0.5]
    with open(fname_qg, 'r') as f:
        query_generator = pickle.load(f)
        queries = query_generator.composed_queries.values()

        with open(fname_rq, 'r') as f:
            refined_queries = pickle.load(f)
            #print refined_queries[22][32]
            #return 0
            query_cost = {}
            for qid in refined_queries:
                fname = fname_qcost+'/q_cost_1min_'+str(qid)+'.pickle'
                with open(fname, 'r') as f:
                    query_cost[qid] = pickle.load(f)

            fname = fname_qcost+'/q_worst_cost_CASE0_1min.pickle'
            with open(fname, 'r') as f:
                query_worst_cost = pickle.load(f)
                tmp = {}
                for qid in query_worst_cost:
                    tmp[qid] = dict((x[0],x[1]) for x in query_worst_cost[qid])
                query_worst_cost = tmp


            #qcost_normalized = normalize_qcost(query_cost)
            qcost_normalized = query_cost

            total_timestamps = get_ts_from_qcost(query_cost)

        training_timestamps = total_timestamps[:10]
        test_timestamps = total_timestamps[11:]

        final_plan_sequences = {}

        # First learn the refinement and partitioning plan for each query, and alpha given training data
        for query in queries[:]:
            final_plan_sequences[query.qid] = {}
            for alpha in alphas:
                query.alpha = alpha
                query.training_timestamps = training_timestamps
                query.qcost = qcost_normalized
                query.get_query_tree()
                query.get_all_queries()
                query.get_partition_plans()
                query.get_cost(ref_levels)
                query.get_refinement_plan(ref_levels)

                query.query_in_mapping = {}
                final_level = ref_levels[-1]
                final_plan_sequence = rs.generate_query_in_mapping(ref_levels[0], final_level, query.query_2_final_plan, query.qid,
                                                                   query.query_tree)

                final_plan_sequences[query.qid][alpha] = final_plan_sequence
            #print query, refined_queries[query.qid]

            #break
        """
        learned_nfrac_2_alpha = learn_alpha_for_packets(queries, training_timestamps, query_cost, ref_levels)
        print learned_nfrac_2_alpha
        return 0,0, 0,0

        learned_bfrac_2_alpha = learn_alpha_for_buckets(queries, training_timestamps, query_cost, ref_levels, query_worst_cost)
        print learned_bfrac_2_alpha
        return 0,0, 0,0
        """

        output_static_dp, output_static_sp = get_static_plan_costs(alphas, ref_levels, queries, query_cost,
                                                                   query_worst_cost, test_timestamps)

        output = {}
        # Now estimate the performance gains
        for ts in test_timestamps[1:]:
            for query in queries[:]:
                # estimate Nmax, and Bmax
                if query.qid not in output:
                    output[query.qid] = {}

                query.get_all_queries()
                all_queries = filter(lambda x: len(query.query_2_plans[x]) > 0, query.query_2_plans.keys())
                all_queries.sort(reverse=True)
                N_max = 0
                B_max = 0
                for q in all_queries:
                    plans = query.query_2_plans[q]
                    #assert (query_cost[query.qid][(plans[-1],(0,8))][ts] == query_cost[query.qid][(plans[-1],(0,32))][ts])
                    N_max += query_cost[all_queries[0]][(plans[-1],(0,32))][ts][1]
                    #B_max += query_cost[q][(plans[0],(0,32))][ts][0]
                    #print query_worst_cost
                    if ts in query_worst_cost[q]:
                        B_max += query_worst_cost[q][ts]

                    print "Worst Buckets", q, query_worst_cost[q][ts]

                print "For query", query.qid, query.keys, "time", ts, "Nmax", N_max, "Bmax", B_max
                for alpha in alphas:
                    if alpha not in output[query.qid]:
                        output[query.qid][alpha] = {}
                    final_plan_sequence = final_plan_sequences[query.qid][alpha]
                    ctr = 1
                    N = 0
                    B = 0
                    for (q_id, (part_plan,ref_transit)) in final_plan_sequence:
                        print "for level", ctr, "query", q_id, " has part plan",part_plan, " and ref plan", ref_transit, "cost", query_cost[q_id][(part_plan,ref_transit)][ts]
                        N += query_cost[q_id][(part_plan,ref_transit)][ts][1]
                        B += query_cost[q_id][(part_plan,ref_transit)][ts][0]
                        ctr += 1

                    print ts, "N", N, N_max, "Gain", float(N)/N_max, alpha
                    print ts, "B", B, B_max, "Gain", float(B)/B_max, alpha
                    output[query.qid][alpha][ts] = ((N,N_max), (B,B_max), ctr-1)

                #break

    return output, final_plan_sequences, output_static_dp, output_static_sp



def case_0_analysis():
    fname_qg = 'data/use_case_0_100_all_data/query_generator_object_case0_100.pickle'
    fname_rq = 'data/use_case_0_100_all_data/refined_queries_queries_case0_1min_100_1min_aws.pickle'
    fname_qcost = 'data/use_case_0_100_all_data/query_cost_queries_case0_1min_100_aws'

    # Get Cost Saving Result
    output, final_plan_sequences, output_static_dp, output_static_sp = get_cost_savings(fname_qg, fname_rq, fname_qcost)

    with open('data/case_0_100_out_data.pickle','w') as f:
        pickle.dump(output,f)
    with open('data/case_0_100_final_plan_sequences.pickle','w') as f:
        pickle.dump(final_plan_sequences,f)
    with open('data/case_0_100_output_static_dp.pickle','w') as f:
        pickle.dump(output_static_dp,f)
    with open('data/case_0_100_output_static_sp.pickle','w') as f:
        pickle.dump(output_static_sp,f)


def analyse_qcost():
    cases = [4]
    for case in cases:
        if case == 1:
            fname_qg = 'aws_results/query_engine/use_cases_aws/query_generator_object_case1.pickle'
            fname_rq = 'aws_results/data/refined_queries_queries_case1_1min_aws.pickle'
            fname_qcost = 'aws_results/data/query_cost_queries_case1_aws'

            output, final_plan_sequences = process_cost_data(fname_qg, fname_rq, fname_qcost, case)

            with open('data/case_1_out_data.pickle','w') as f:
                pickle.dump(output,f)
            with open('data/case_1_final_plan_sequences.pickle','w') as f:
                pickle.dump(final_plan_sequences,f)

        elif case == 2:
            fname_qg = 'aws_results/query_engine/use_cases_aws/query_generator_object_case2.pickle'
            fname_rq = 'aws_results/data/refined_queries_queries_case2_1min_aws.pickle'
            fname_qcost = 'aws_results/data/query_cost_queries_case2_aws'

            output, final_plan_sequences = process_cost_data(fname_qg, fname_rq, fname_qcost, case)

            with open('data/case_2_out_data.pickle','w') as f:
                pickle.dump(output,f)
            with open('data/case_2_final_plan_sequences.pickle','w') as f:
                pickle.dump(final_plan_sequences,f)

        elif case == 3:
            fname_qg = 'aws_results/query_engine/use_cases_aws/query_generator_object_case3.pickle'
            fname_rq = 'aws_results/data/refined_queries_queries_case3_1min_aws.pickle'
            fname_qcost = 'aws_results/data/query_cost_queries_case3_aws'

            output, final_plan_sequences = process_cost_data(fname_qg, fname_rq, fname_qcost, case)

            with open('data/case_3_out_data.pickle','w') as f:
                pickle.dump(output,f)
            with open('data/case_3_final_plan_sequences.pickle','w') as f:
                pickle.dump(final_plan_sequences,f)

        elif case == 4:
            fname_qg = 'aws_results/query_engine/use_cases_aws/query_generator_object_case4.pickle'
            fname_rq = 'aws_results/data/refined_queries_queries_case4_1min_aws.pickle'
            fname_qcost = 'aws_results/data/query_cost_queries_case4_aws'

            output, final_plan_sequences = process_cost_data(fname_qg, fname_rq, fname_qcost, case)

            with open('data/case_4_5_out_data.pickle','w') as f:
                pickle.dump(output,f)
            with open('data/case_4_5_final_plan_sequences.pickle','w') as f:
                pickle.dump(final_plan_sequences,f)


if __name__ == '__main__':

    #analyse_qcost()
    case_0_analysis()

    """
    # print node_2_plan
    memorized_plans = {}
    mapped_plan = {}
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
    for qid in all_queries:
        if qid not in query_2_cost:
            query_2_cost[qid] = {}
        # randomly select number of plans, i.e. number of paths in the partition tree
        n_plans = random.randint(1, max_plans)
        query_2_plans[qid] = range(1, n_plans + 1)
        if qid == 3:
            n_plans = 0
            query_2_plans[qid] = []

        for p1 in range(1, n_plans + 1):
            for p2 in range(1, n_plans + 1):
                # For each path combination for each query we generate cost using the cost function above.
                tmp = generate_costs(p1,p2,ref_levels)
                for transit in tmp:
                    query_2_cost[qid][(p1, p2), transit] = tmp[transit]

    # print query_2_plans
    # print query_2_cost
    # print query_2_cost.keys()
    start = time.time()



    for qid in query_tree:
        # We start with the finest refinement level, as expressed in the original query

        final_plan, cost = get_refinement_plan(ref_levels[0], ref_levels[-1], qid, ref_levels, query_2_plans,
                                               query_tree, query_2_cost, query_2_final_plan, memorized_plans, mapped_plan)

    #print "Mapped Plan", mapped_plan


    print query_2_final_plan
    print "Took", time.time() - start, "seconds"



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
    """