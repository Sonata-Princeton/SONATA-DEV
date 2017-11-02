#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from sonata.query_engine.sonata_queries import *
import sonata.streaming_driver.query_object as spark
from sonata.core.training.utils import *
import numpy as np


def requires_payload_processing(query, sonata_fields):
    parse_payload = False
    for operator in query.operators[1:]:
        if len(set(sonata_fields.all_payload_fields.keys()).intersection(set(operator.keys))) > 0:
            parse_payload = True

    return parse_payload


def filtering_in_payload(query):
    filter_payload = False
    filter_payload_str = ''

    for operator in query.operators:
        if operator.name == 'Filter':
            if len(set(['payload', ]).intersection(set(operator.filter_vals))) > 0:
                filter_payload = True
                filter_payload_str = operator.func[1]

    return filter_payload, filter_payload_str


def get_payload_fields(query, sonata_fields):
    payload_fields = set()
    for operator in query.operators[1:]:
        payload_fields = payload_fields.union(
            set(sonata_fields.all_payload_fields.keys()).intersection(set(operator.keys)))

    return list(payload_fields)


def filter_payload_fields_append_to_end(fields, sonata_fields):
    payload_fields = set()

    payload_fields = payload_fields.union(set(sonata_fields.all_payload_fields.keys()).intersection(set(fields)))
    other = [x for x in fields if x not in payload_fields]
    other.extend(list(payload_fields))
    return other


def flatten_streaming_field_names(fields):
    flattened_fields = [field.replace(".", "_") for field in fields]

    return flattened_fields


def generated_source_path(dir_path, create_directory):
    import os
    import shutil
    generated_src_path = dir_path + create_directory
    if os.path.isdir(generated_src_path):
        # clean the directory
        shutil.rmtree(generated_src_path)

    # Now create a new directory
    os.makedirs(generated_src_path)

    return generated_src_path


def copy_sonata_operators_to_sp_query(query, optr, sonata_fields):
    if optr.name == 'Filter':
        query.filter(filter_keys=flatten_streaming_field_names(
            filter_payload_fields_append_to_end(optr.filter_keys, sonata_fields)),
                     filter_vals=flatten_streaming_field_names(
                         filter_payload_fields_append_to_end(optr.filter_vals, sonata_fields)),
                     func=optr.func)
    elif optr.name == "Map":
        query.map(keys=flatten_streaming_field_names(filter_payload_fields_append_to_end(optr.keys, sonata_fields)),
                  values=flatten_streaming_field_names(filter_payload_fields_append_to_end(optr.values, sonata_fields)),
                  map_keys=flatten_streaming_field_names(
                      filter_payload_fields_append_to_end(optr.map_keys, sonata_fields)),
                  map_values=flatten_streaming_field_names(
                      filter_payload_fields_append_to_end(optr.map_values, sonata_fields)),
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=flatten_streaming_field_names(filter_payload_fields_append_to_end(optr.keys, sonata_fields)),
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(
            keys=flatten_streaming_field_names(filter_payload_fields_append_to_end(optr.keys, sonata_fields)))


def filter_payload(keys):
    return filter(lambda x: x != 'payload', keys)


def get_refinement_keys(query, refinement_keys_set):
    per_query_refinement = {}

    red_keys = set([])
    if query.left_child is not None:

        red_keys_left, _ = get_refinement_keys(query.left_child, refinement_keys_set)
        # print "left keys", red_keys_left, query.qid
        red_keys_right, _ = get_refinement_keys(query.right_child, refinement_keys_set)
        # print "right keys", red_keys_right, query.qid

        per_query_refinement[query.left_child.qid] = red_keys_left
        per_query_refinement[query.right_child.qid] = red_keys_right

        red_keys = set(red_keys_left)

        for operator in query.operators:
            if operator.name in ['Distinct', 'Reduce']:
                red_keys = red_keys.intersection(set(operator.keys))

        per_query_refinement[query.qid] = red_keys
        red_keys = red_keys.intersection(refinement_keys_set)

    else:
        red_keys = set(query.basic_headers)
        for operator in query.operators:
            # Extract reduction keys from first reduce/distinct operator
            if operator.name in ['Distinct', 'Reduce']:
                red_keys = red_keys.intersection(set(operator.keys))

    red_keys = red_keys.intersection(refinement_keys_set)

    return red_keys, per_query_refinement


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
