#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from integration import *

def get_query_2_plans(flattened_queries, runtime):
    query_2_plans = {}
    print flattened_queries
    for query in flattened_queries:

        #query = flattened_queries[query_id]
        n_operators = len(query.operators)
        # We do not support join operations explicitly in
        # the data plane, so we are only concerned with the flattened queries.
        dp_query = sonata_2_dp_query(query)

        #TODO:: Call the real socket based function -- dummy used right now
        #partitions = runtime.send_to_dp_driver('is_supported', dp_query)
        partitions = send_to_dp_driver('is_supported', dp_query)
        partitioning_plans = []
        for partition in partitions:
            partitioning_plans.append((partition, n_operators-partition))
        query_2_plans[query.qid] = partitioning_plans

    return query_2_plans

# def generate_partitioned_queries():
#
#     """
#     Generates P4 query and Sonata query object for each refined query.
#     :return:
#     """
#
#     def set_partition_with_payload_processing(p4_query, operator):
#         #print "Partition set with payload processing for", operator.name
#         p4_query.parse_payload = True
#         return max_dp_operators
#
#
#     for (queryId, ref_level) in query_in_mapping.keys():
#         # partitioning plan is a bit string. For example for a query with partitioning
#         # plan `001` means that it will add the first two reduce operators to
#         # the P4 query and the last one to the Spark query
#         # It is easy to apply the logic of partitioning the reduce operatos, however, we
#         # want to make sure that even if there are no reduce operators in the
#         # data plane, we execute basic filtering and map operations in the data plane,
#         # We are using the data plane to parse the incoming packet stream to packet
#         # tuples (qid, ...) that can be processed by the stream processor, thus we need to
#         # make sure that each query has its basic map/filter function in the data plane.
#
#         partitioning_plan = query_2_refinement_levels[queryId][ref_level]
#         # `max_dp_operators` is the number of reduction operators to be added to the P4 query
#         max_dp_operators = 0
#         for elem in str(partitioning_plan):
#             if elem == '0':
#                 max_dp_operators += 1
#             else:
#                 break
#
#         refined_query = refined_queries[queryId][ref_level]
#
#         # Even if the query has payload field in packet tuple, we exclude that from
#         # our P4 query object as we can't parse it in the data plane
#         p4_basic_headers = filter(lambda x: x != "payload", refined_query.basic_headers)
#         #print "p4_basic_headers", p4_basic_headers, refined_query.basic_headers
#
#         # Initialize P4 query
#         p4_query = p4.QueryPipeline(refined_query.qid).map_init(keys=p4_basic_headers)
#         p4_query.parse_payload = False
#
#         # Initialize Spark Query
#         spark_query = (spark.PacketStream(refined_query.qid))
#
#         print queryId, ref_level, partitioning_plan, max_dp_operators
#         print "Original Refined Query before partitioning:\n", refined_query
#         # number of reduce operators delegated so far
#         in_dataplane = 0
#         # our implementation requires duplicating the last (border) reduce
#         # operator in P4 query to Spark query, the reason is that ours is not
#         # just reduce, it is reduce and filter, so after the count exceeds
#         # the threshold, it emits all the packet tuples with count 1.
#         # Thus we require duplicating the reduce operator.
#         border_reduce = None
#         # In future, we should not require this map operation that needs to
#         # be applied before the border reduce operator.
#         border_map = None
#
#         # To ensure that we initialize the spark query only once
#         init_spark = True
#
#         for operator in refined_query.operators:
#             if in_dataplane < max_dp_operators:
#                 #print "Making partitioning decision for", operator, in_dataplane, p4_query.parse_payload
#                 if not p4_query.parse_payload:
#                     # Check whether we can support these operators in the data plane, and if
#                     # we need to parse packet payload in the stream processor
#                     if operator.name in ['Filter']:
#                         if "payload" in operator.filter_keys or "payload" in operator.filter_vals:
#                             in_dataplane = set_partition_with_payload_processing(p4_query, operator)
#                     elif operator.name in ['Map']:
#                         if len(operator.map_keys) == 0:
#                             if "payload" in operator.keys or "payload" in operator.values:
#                                 in_dataplane = set_partition_with_payload_processing(p4_query, operator)
#                         else:
#                             if "payload" in operator.map_keys or "payload" in operator.map_values:
#                                 in_dataplane = set_partition_with_payload_processing(p4_query, operator)
#                     else:
#                         if "payload" in operator.keys or "payload" in operator.values:
#                             in_dataplane = set_partition_with_payload_processing(p4_query, operator)
#
#                 if operator.name == 'Reduce':
#                     in_dataplane += 1
#                     copy_sonata_operators_to_p4(p4_query, operator)
#                     #print "R1 - P4", in_dataplane, max_dp_operators
#
#                     # duplicate implementation of reduce operators at the border
#                     if in_dataplane == max_dp_operators:
#                         border_reduce = p4_query.operators[-1]
#                         #print "Adding border reduce to Spark", border_reduce
#
#                         if init_spark:
#                             init_spark, spark_query = initialize_spark_query(p4_query,
#                                                                              spark_query,
#                                                                              refined_query.qid)
#                         # Add the map operator before this border reduce operator to select the right reduction keys
#                         if border_map is not None:
#                             border_map.func = ()
#                             copy_sonata_operators_to_spark(spark_query, border_map)
#                         copy_sonata_operators_to_spark(spark_query, operator)
#
#                 elif operator.name == 'Map':
#                     if len(operator.func) > 0 and operator.func[0] == 'mask':
#                         copy_sonata_operators_to_p4(p4_query, operator)
#                     else:
#                         # TODO: think of a better logic to identify the border map operator
#                         border_map = operator
#
#                 elif operator.name == 'Filter':
#                     # check if previous operator was reduce
#                     if len(operator.func) > 0 and operator.func[1] == 'geq':
#                         if len(p4_query.operators) > 0 and p4_query.operators[-1].name == "Reduce":
#                             prev_operator = p4_query.operators[-1]
#                             # update the threshold for the previous Reduce operator
#                             # TODO: assumes func is `geq`, implement others
#                             prev_operator.thresh = operator.func[1]
#                     else:
#                         copy_sonata_operators_to_p4(p4_query, operator)
#
#                 elif operator.name == 'Distinct':
#                     in_dataplane += 1
#                     copy_sonata_operators_to_p4(p4_query, operator)
#
#             else:
#                 if init_spark:
#                     init_spark, spark_query = initialize_spark_query(p4_query,
#                                                                      spark_query,
#                                                                      refined_query.qid)
#                 #print "Adding", operator
#                 if operator.name == "Filter":
#                     #print "Filter", operator.func, border_reduce
#                     if len(operator.func) > 0 and operator.func[0] == 'geq' and border_reduce is not None:
#                         border_reduce.thresh = operator.func[1]
#                         #print "Updated threshold", border_reduce.thresh, " for", border_reduce.name
#                         copy_sonata_operators_to_spark(spark_query, operator)
#                     elif len(operator.func) > 0 and operator.func[0] == 'mask':
#                         copy_sonata_operators_to_p4(p4_query, operator)
#                     elif len(operator.func) > 0 and operator.func[0] == 'eq' and 'payload' not in operator.filter_keys:
#                         copy_sonata_operators_to_p4(p4_query, operator)
#                     else:
#                         copy_sonata_operators_to_spark(spark_query, operator)
#
#                 elif operator.name == "Map":
#                     if len(operator.func) > 0 and operator.func[0] == 'mask':
#                         copy_sonata_operators_to_p4(p4_query, operator)
#                     else:
#                         copy_sonata_operators_to_spark(spark_query, operator)
#                 else:
#                     copy_sonata_operators_to_spark(spark_query, operator)
#
#         print "After Partitioning, P4:\n", p4_query
#         print "After Partitioning, Spark:\n", spark_query
#         qid_2_dp_queries[refined_query.qid] = p4_query
#         qid_2_sp_queries[refined_query.qid] = spark_query
#         refined_query.dp_query = p4_query
#         refined_query.sp_query = spark_query
#     return 0
#
