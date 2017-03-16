#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from integration import *

from sonata.dataplane_driver.query_object import QueryObject as DP_QO
from sonata.streaming_driver.query_object import PacketStream as SP_QO

# TODO fix this mess
def get_query_2_plans(flattened_queries):
    query_2_plans = {}
    print flattened_queries
    for query in flattened_queries:

        # query = flattened_queries[query_id]
        n_operators = len(query.operators)
        # We do not support join operations explicitly in
        # the data plane, so we are only concerned with the flattened queries.
        dp_query = sonata_2_dp_query(query)

        # TODO:: Call the real socket based function -- dummy used right now
        # partitions = runtime.send_to_dp_driver('is_supported', dp_query)
        partitions = send_to_dp_driver('is_supported', dp_query)
        partitioning_plans = []
        for partition in partitions:
            partitioning_plans.append((partition, n_operators - partition))
        # TODO: get rid of this hardcoding
        partitioning_plans = ['00', '01', '11']
        query_2_plans[query.qid] = partitioning_plans
    print "Partitioning Plans", query_2_plans

    return query_2_plans


def requires_payload_processing(query):
    parse_payload = False
    for operator in query.operators:
        if 'payload' in operator.keys:
            parse_payload = False

    return parse_payload


def get_dataplane_query(query, qid, partition_plan):
    # number of operators in the data plane
    n_operators_dp = int(partition_plan[0])
    dp_query = None
    if n_operators_dp > 0:
        # create a dp query object
        dp_query = DP_QO(qid)
        border_operator = query.operators[n_operators_dp - 1]
        if border_operator.name == "Reduce":
            # We need to ensure that we also execute the next filter operator in the data plane
            n_operators_dp += 1

        for operator in query.operators[:n_operators_dp]:
            # passing the operators as-is based on discussions with Rudy
            dp_query.operators.append(operator)
            #copy_sonata_operators_to_dp_query(dp_query, operator)
        dp_query.parse_payload = requires_payload_processing(query)

    return dp_query


def get_streaming_query(query, qid, partition_plan):
    # number of operators in the data plane
    n_operators_dp = int(partition_plan[0])
    n_operators_sp = int(partition_plan[1])
    if n_operators_sp > 0:
        # create a dp query object
        sp_query = SP_QO(qid)
        if n_operators_dp > 0:
            # update the basic headers
            # Add 'k' field to filter out garbled message received by the stream processor
            sp_query.basic_headers = ['k', 'qid'] + list(query.operators[n_operators_dp - 1].keys)
            border_operator = query.operators[n_operators_dp - 1]
            if border_operator.name == "Reduce":
                # We need to duplicate reduce operator in the data plane
                n_operators_dp -= 1

        # Filter step is added to map incoming packet streams from multiple dataflow pipelines
        # to their respective pipelines in the stream processor
        sp_query = sp_query.filter_init(qid=qid, keys=sp_query.basic_headers)

        # Update the remainder operators
        for operator in query.operators[n_operators_dp:]:
            copy_sonata_operators_to_sp_query(sp_query, operator)
        sp_query.parse_payload = requires_payload_processing(query)

        return sp_query


def copy_sonata_operators_to_sp_query(query, optr):
    if optr.name == 'Filter':
        query.filter(filter_keys=optr.filter_keys,
                     filter_vals=optr.filter_vals,
                     func=optr.func)
    elif optr.name == "Map":
        query.map(keys=optr.keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=optr.keys,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=optr.keys)


def filter_payload(keys):
    return filter(lambda x: x != 'payload', keys)


def copy_sonata_operators_to_dp_query(query, optr):
    keys = filter_payload(optr.keys)
    if optr.name == 'Filter':
        # TODO: get rid of this hardcoding
        if optr.func[0] != 'geq':
            query.filter(keys=keys,
                         filter_keys=optr.filter_keys,
                         func=optr.func,
                         src=optr.src)
    elif optr.name == "Map":
        query.map(keys=keys,
                  map_keys=optr.map_keys,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys)

    elif optr.name == "Distinct":
        query.distinct(keys=keys)
