#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
import copy

#import query_engine.spark_queries as spark

from sonata.query_engine.sonata_queries import *


def get_original_wo_mask(lstOfFields):
    fields = []

    for field in lstOfFields:
        if '/' in field:
            fields.append(field.split('/')[0])
        else:
            fields.append(field)

    return fields


def generate_composed_spark_queries(reduction_key, basic_headers, query_tree, qid_2_query, composed_queries = {}):
    #print query_tree
    root_qid = query_tree.keys()[0]
    #print "##", root_qid, query_tree.keys(), qid_2_query
    if root_qid in qid_2_query:
        root_query_sonata = qid_2_query[root_qid]
        root_query_spark = spark.PacketStream(root_qid)
        root_query_spark.basic_headers = basic_headers
    else:
        root_query_sonata = PacketStream(root_qid)
        root_query_spark = spark.PacketStream(root_qid)
        root_query_spark.basic_headers = basic_headers

    #print "%%", root_qid, root_query_sonata

    if query_tree[root_qid] != {}:
        children = query_tree[root_qid].keys()
        children.sort()
        left_qid = children[0]
        right_qid = children[1]
        left_query = generate_composed_spark_queries(reduction_key, basic_headers,
                                                     {left_qid:query_tree[root_qid][left_qid]},
                                                     qid_2_query, composed_queries)

        right_query = generate_composed_spark_queries(reduction_key, basic_headers,
                                                      {right_qid:query_tree[root_qid][right_qid]},
                                                      qid_2_query, composed_queries)

        #print "Left", left_qid, left_query

        #print "Right", right_qid, right_query
        for operator in root_query_sonata.operators:
            if operator.name == 'Map' and len(operator.func) > 0 and operator.func[0] == 'mask':
                copy_sonata_operators_to_spark(right_query, operator)

        composed_query = right_query.join(q=left_query, join_key = reduction_key, in_stream = 'In.')
        # This is important else the composed query will take the qid of the right child itself
        composed_query.qid = root_qid
        for operator in root_query_sonata.operators:
            if not (operator.name == 'Map' and len(operator.func) > 0 and operator.func[0] == 'mask'):
                copy_sonata_operators_to_spark(composed_query, operator)

        composed_queries[root_qid] = copy.deepcopy(composed_query)
    else:
        #print "Adding for", root_qid, root_query_sonata, root_query_sonata.qid
        for operator in root_query_sonata.operators:
            copy_sonata_operators_to_spark(root_query_spark, operator)

        #print "##Updating key", root_qid
        composed_queries[root_qid] = copy.deepcopy(root_query_spark)
        composed_query = root_query_spark

    #print "returning for ", root_qid, composed_queries

    return composed_query


def update_query_tree(root, qt, rl, out):
    #print root, qt
    out[10000*root+rl] = {}
    if len(qt[root]) > 0:
        children = qt[root].keys()
        children.sort()

        lc = children[0]
        #print lc, {lc:qt[root][lc]}
        update_query_tree(lc, {lc:qt[root][lc]}, rl, out[10000*root+rl])
        rc = children[1]
        #print rc, {rc:qt[root][rc]}
        update_query_tree(rc, {rc:qt[root][rc]}, rl, out[10000*root+rl])
    return out


def copy_operators(query, optr):
    if optr.name == 'Filter':
        query.filter(filter_keys=optr.filter_keys,
                     filter_vals=optr.filter_vals,
                     func=optr.func,
                     src=optr.src)
    elif optr.name == "Map":
        query.map(keys=optr.keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=optr.keys,
                     values=optr.values,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=optr.keys,
                       values=optr.values)


def copy_sonata_operators_to_spark(query, optr):
    #print "Adding spark operator", optr.name
    prev_keys = get_original_wo_mask(optr.prev_keys)
    keys = get_original_wo_mask(optr.keys)
    if optr.name == 'Filter':
        query.filter(filter_keys=optr.filter_keys,
                     filter_vals=optr.filter_vals,
                     func=optr.func)
    elif optr.name == "Map":
        query.map(keys=keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=keys)

def copy_spark_operators_to_spark(query, optr):
    #print "Adding spark operator", optr.name
    prev_keys = get_original_wo_mask(optr.prev_keys)
    keys = get_original_wo_mask(optr.keys)
    if optr.name == 'Filter':
        query.filter(filter_keys=optr.filter_keys,
                     filter_vals=optr.filter_vals,
                     func=optr.func)
    elif optr.name == "Map":
        query.map(keys=keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=keys)

    elif optr.name == 'Join':
        #print "Before Joining", optr.join_query
        optr.in_stream = 'self.training_data.'
        new_join_query = spark.PacketStream(optr.join_query.qid)
        new_join_query.basic_headers = query.basic_headers
        for new_optr in optr.join_query.operators:
            copy_spark_operators_to_spark(new_join_query, new_optr)
        #print "After Updating the Join Query", new_join_query
        query.join(q=new_join_query, join_key = optr.join_key, in_stream = optr.in_stream)


def initialize_spark_query(p4_query, spark_query, qid):
    #print "Initializing Spark Query Object"
    if len(p4_query.operators) > 0:
        hdrs = list(p4_query.operators[-1].out_headers)
    else:
        raise NotImplementedError
    if p4_query.parse_payload: hdrs += ['payload']
    #print "Headers", hdrs
    spark_query.basic_headers = ['k'] + hdrs
    spark_query = spark_query.filter_init(qid=qid, keys=spark_query.basic_headers)
    return False, spark_query


def filter_payload(keys):
    return filter(lambda x: x!= 'payload', keys)


def copy_sonata_operators_to_p4(query, optr):
    #print "Adding P4 operator", optr.name
    keys = filter_payload(optr.keys)
    if optr.name == 'Filter':
        # TODO: get rid of this hardcoding
        if optr.func[0] != 'geq':
            query.filter(keys=keys,
                         filter_keys=optr.filter_keys,
                         func=optr.func,
                         src=optr.src)
    elif optr.name == "Map":
        query.map(keys = keys,
                  map_keys=optr.map_keys,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys)

    elif optr.name == "Distinct":
        query.distinct(keys=keys)