#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from sonata.query_engine.sonata_queries import *

def get_refinement_keys(query):
    red_keys = set([])
    if query.left_child is not None:
        red_keys_left = get_refinement_keys(query.left_child)
        red_keys_right = get_refinement_keys(query.right_child)
        # print "left keys", red_keys_left, query.qid
        # print "right keys", red_keys_right, query.qid
        # TODO: make sure that we better handle the case when first reduce operator has both sIP and dIP as reduction keys
        if len(red_keys_right) > 0:
            red_keys = set(red_keys_left).intersection(red_keys_right)
        else:
            red_keys = set(red_keys_left)

        for operator in query.operators:
            if operator.name in ['Distinct', 'Reduce']:
                red_keys = red_keys.intersection(set(operator.keys))
                # print query.qid, operator.name, red_keys

        red_keys = red_keys.intersection(query.refinement_headers)

    else:
        # print "Reached leaf node", query.qid
        red_keys = set(query.basic_headers)
        for operator in query.operators:
            # Extract reduction keys from first reduce/distinct operator
            if operator.name in ['Distinct', 'Reduce']:
                red_keys = red_keys.intersection(set(operator.keys))

    # print "Reduction Key Search", query.qid, red_keys
    return red_keys


def generate_composed_spark_queries(reduction_key, basic_headers, query_tree, qid_2_query, composed_queries={}):
    # print query_tree
    root_qid = query_tree.keys()[0]
    # print "##", root_qid, query_tree.keys(), qid_2_query
    if root_qid in qid_2_query:
        root_query_sonata = qid_2_query[root_qid]
        root_query_spark = spark.PacketStream(root_qid)
        root_query_spark.basic_headers = basic_headers
    else:
        root_query_sonata = PacketStream(root_qid)
        root_query_spark = spark.PacketStream(root_qid)
        root_query_spark.basic_headers = basic_headers

    # print "%%", root_qid, root_query_sonata

    if query_tree[root_qid] != {}:
        children = query_tree[root_qid].keys()
        children.sort()
        left_qid = children[0]
        right_qid = children[1]
        left_query = generate_composed_spark_queries(reduction_key, basic_headers,
                                                     {left_qid: query_tree[root_qid][left_qid]},
                                                     qid_2_query, composed_queries)

        right_query = generate_composed_spark_queries(reduction_key, basic_headers,
                                                      {right_qid: query_tree[root_qid][right_qid]},
                                                      qid_2_query, composed_queries)

        # print "Left", left_qid, left_query

        # print "Right", right_qid, right_query
        for operator in root_query_sonata.operators:
            if operator.name == 'Map' and len(operator.func) > 0 and operator.func[0] == 'mask':
                copy_sonata_operators_to_spark(right_query, operator)

        composed_query = right_query.join(q=left_query, join_key=reduction_key, in_stream='In.')
        # This is important else the composed query will take the qid of the right child itself
        composed_query.qid = root_qid
        for operator in root_query_sonata.operators:
            if not (operator.name == 'Map' and len(operator.func) > 0 and operator.func[0] == 'mask'):
                copy_sonata_operators_to_spark(composed_query, operator)

        composed_queries[root_qid] = copy.deepcopy(composed_query)
    else:
        # print "Adding for", root_qid, root_query_sonata, root_query_sonata.qid
        for operator in root_query_sonata.operators:
            copy_sonata_operators_to_spark(root_query_spark, operator)

        # print "##Updating key", root_qid
        composed_queries[root_qid] = copy.deepcopy(root_query_spark)
        composed_query = root_query_spark

    # print "returning for ", root_qid, composed_queries

    return composed_query


def generate_composed_query(query_tree, qid_2_query):
    # print query_tree
    root_qid = query_tree.keys()[0]
    # print "##", root_qid, query_tree.keys(), qid_2_query
    if root_qid in qid_2_query:
        root_query = qid_2_query[root_qid]
    else:
        root_query = PacketStream(root_qid)

    # print "%%", root_qid, root_query

    if query_tree[root_qid] != {}:
        children = query_tree[root_qid].keys()
        children.sort()

        left_qid = children[0]
        right_qid = children[1]

        left_query = generate_composed_query({left_qid: query_tree[root_qid][left_qid]}, qid_2_query)
        right_query = generate_composed_query({right_qid: query_tree[root_qid][right_qid]}, qid_2_query)

        left_query_keys = left_query.keys
        # right_query = right_query.map(keys=left_query_keys, values=tuple(basic_headers))
        """
        print "Qid", root_qid
        print "Root Query", root_query
        print "Right Query", right_query
        print "Left Query", left_query
        """
        composed_query = right_query.join(new_qid=root_qid, query=left_query)
        for operator in root_query.operators:
            copy_operators(composed_query, operator)
    else:
        composed_query = root_query

    return composed_query


def generate_query_tree(ctr, all_queries, depth):
    """
    Generate Query Tree
    arguments:
    @ctr: query id for the query
    @all_queries: list of all queries in the tree
    @depth: depth of the query tree to be generated

    """
    query_tree = {}
    if depth > 0:
        if ctr > len(all_queries) / 2:
            return query_tree
        qid_l = all_queries[2 * ctr - 1]
        query_tree[qid_l] = generate_query_tree(ctr + 1, all_queries, depth - 1)
        qid_r = all_queries[2 * ctr]
        query_tree[qid_r] = {}
    return query_tree


def get_left_children(query_tree, out):
    """
    return all the left children for query_tree
    """
    qt = query_tree
    for parent in qt:
        # print parent, qt
        if len(qt[parent].keys()) > 0:
            children = qt[parent].keys()
            children.sort()
            # print "Sorted Children", children
            out.append(children[0])
            get_left_children({children[0]: qt[parent][children[0]]}, out)
        else:
            break


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