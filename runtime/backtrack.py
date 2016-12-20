#!/usr/binput/env python
#  Author:
#  Arpit Gupta (arpitg@cs.prinputceton.edu)

import random

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

def check_transit(prev, elem):
    # TODO Make this more reasonable
    if (tuple([prev,elem])) in costs:
        return True
    else:
        return False

def get_refinement_plan(costs):
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
            explore_further[curr_level] = {root:0}
            node_2_all_plans[curr_level] = {}
            node_2_all_plans[curr_level][root] = [root]
        #print curr_level, explore_further

        next_level = curr_level+1
        if curr_level in explore_further:
            explore_further[next_level] = {}
            for prev in explore_further[curr_level]:
                for elem in a:
                    is_transit_allowed = check_transit(prev, elem)
                    if is_transit_allowed:
                        #print curr_level, prev, elem, is_transit_allowed


                        prev_plan = node_2_all_plans[curr_level][prev]
                        if tuple(prev_plan) in plan_2_cost:
                            prev_plan_cost = plan_2_cost[tuple(prev_plan)]
                        else:
                            prev_plan_cost = get_plan_cost(tuple(prev_plan))

                        curr_plan = prev_plan+[elem]
                        curr_plan_cost = costs[(prev,elem)]+prev_plan_cost
                        if elem not in node_2_plan:
                            node_2_plan[elem] = curr_plan
                            explore_further[next_level][elem] = 0
                        else:
                            curr_cost = plan_2_cost[tuple(node_2_plan[elem])]
                            new_cost = curr_plan_cost

                            #print ("Current Plan:", node_2_plan[elem],
                            #        " Cost:", plan_2_cost[tuple(node_2_plan[elem])])
                            #print ("New Plan:", curr_plan, " Cost:", curr_plan_cost)
                            if new_cost < curr_cost:
                                #print "Updating Plan for Node", elem
                                node_2_plan[elem] = curr_plan
                                explore_further[next_level][elem] = 0

                        if next_level not in node_2_all_plans:
                            node_2_all_plans[next_level] = {}
                        node_2_all_plans[next_level][elem] = curr_plan


                        #print curr_plan, curr_plan_cost, node_2_plan
                        #print tuple(curr_plan)
                        plan_2_cost[tuple(curr_plan)] = curr_plan_cost

    print "Final Plan", node_2_plan[32], plan_2_cost[tuple(node_2_plan[32])]
    return (node_2_plan[32], plan_2_cost[tuple(node_2_plan[32])])

#print node_2_plan
a = range(0,36,8)
costs = generate_costs(a)
final_plan, cost = get_refinement_plan(costs)
