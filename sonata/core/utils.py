#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)


def get_refinement_keys(query):
    red_keys = set([])
    if query.left_child is not None:
        red_keys_left = get_refinement_keys(query.left_child)
        red_keys_right = get_refinement_keys(query.right_child)
        #print "left keys", red_keys_left, query.qid
        #print "right keys", red_keys_right, query.qid
        # TODO: make sure that we better handle the case when first reduce operator has both sIP and dIP as reduction keys
        if len(red_keys_right) > 0:
            red_keys = set(red_keys_left).intersection(red_keys_right)
        else:
            red_keys = set(red_keys_left)

        for operator in query.operators:
            if operator.name in ['Distinct', 'Reduce']:
                red_keys = red_keys.intersection(set(operator.keys))
                #print query.qid, operator.name, red_keys

        red_keys = red_keys.intersection(query.refinement_headers)

    else:
        #print "Reached leaf node", query.qid
        red_keys = set(query.basic_headers)
        for operator in query.operators:
            # Extract reduction keys from first reduce/distinct operator
            if operator.name in ['Distinct', 'Reduce']:
                red_keys = red_keys.intersection(set(operator.keys))

    #print "Reduction Key Search", query.qid, red_keys
    return red_keys

def get_query_tree(query):
    query_tree = {query.qid: {}}
    if query.right_child is not None:
        query_tree[query.qid][query.left_child.qid] = get_query_tree(query.left_child)[query.left_child.qid]
        query_tree[query.qid][query.right_child.qid] = get_query_tree(query.right_child)[query.right_child.qid]

    return query_tree


def get_all_queries(query):
    all_queries = []
    all_queries.append(query)
    if query.right_child is not None:
        all_queries.extend(get_all_queries(query.left_child))
        all_queries.extend(get_all_queries(query.right_child))

    return all_queries

def get_qid_2_query(query):
    qid_2_query = {}
    qid_2_query[query.qid] = query
    if query.right_child is not None:
        qid_2_query.update(get_qid_2_query(query.left_child))
        qid_2_query.update(get_qid_2_query(query.right_child))

    return qid_2_query

def get_flattened_sub_queries(query):
    flattened_queries = get_all_queries(query)
    return flattened_queries