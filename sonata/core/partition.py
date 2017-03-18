#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

#from integration import *

from sonata.dataplane_driver.query_object import QueryObject as DP_QO
from sonata.streaming_driver.query_object import PacketStream as SP_QO
from sonata.query_engine.utils import copy_operators
from sonata.core.utils import requires_payload_processing, copy_sonata_operators_to_sp_query, get_flattened_sub_queries
from sonata.query_engine.sonata_queries import PacketStream
from sonata.system_config import BASIC_HEADERS
from integration import sonata_2_dp_query


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
            # copy_sonata_operators_to_dp_query(dp_query, operator)
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


class Partition(object):
    intermediate_learning_queries = {}
    filter_mappings = {}

    def __init__(self, query, target, ref_level = 32):
        self.query = query
        self.target = target
        self.ref_level = ref_level

    def generate_partitioned_queries_learning(self):
        sonata_query = self.query
        number_intermediate_learning_queries = len(
            filter(lambda s: s in self.target.learning_operators, [x.name for x in self.query.operators]))
        intermediate_learning_queries = {}
        prev_qid = 0
        filter_mappings = {}
        filters_marked = {}
        for max_operators in range(1, 1 + number_intermediate_learning_queries):
            qid = (1000 * sonata_query.qid) + max_operators
            tmp_query = (PacketStream(sonata_query.qid))
            tmp_query.basic_headers = BASIC_HEADERS
            ctr = 0
            filter_ctr = 0
            prev_operator = None
            for operator in sonata_query.operators:
                if operator.name != 'Join':
                    if ctr < max_operators:
                        copy_operators(tmp_query, operator)
                        prev_operator = operator
                    else:
                        break
                    if operator.name in self.target.learning_operators:
                        ctr += 1
                    if operator.name == 'Filter':
                        filter_ctr += 1
                        if (qid, self.ref_level, filter_ctr) not in filters_marked:
                            filters_marked[(qid, self.ref_level, filter_ctr, )] = sonata_query.qid
                            filter_mappings[(prev_qid, qid, self.ref_level)] = (sonata_query.qid, filter_ctr, operator.func[1])
                else:
                    prev_operator = operator
                    copy_operators(tmp_query, operator)

            intermediate_learning_queries[qid] = tmp_query
            prev_qid = qid

        self.intermediate_learning_queries = intermediate_learning_queries
        self.filter_mappings = filter_mappings

    def get_query_2_plans(self):
        query_2_plans = {}
        for q in get_flattened_sub_queries(self.query):
            n_operators = len(q.operators)
            dp_query = sonata_2_dp_query(q)
            partitioning_plans = self.get_partition_plans(dp_query)
            # TODO: get rid of this hardcoding
            #partitioning_plans = ['00', '01', '11']
            query_2_plans[q.qid] = partitioning_plans
        print "Partitioning Plans", query_2_plans

        return query_2_plans

    def get_partition_plans(self, dp_query):
        # receives dp_query object.
        total_operators = len(dp_query.operators)
        partition_plans = [(0, total_operators)]
        ctr = 1
        for operator in dp_query.operators:
            if operator.name in self.target.supported_operators.keys():
                if hasattr(operator, 'func') and len(operator.func) > 0:
                    if operator.func[0] in self.target.supported_operators[operator.name]:
                        if operator.name in self.target.costly_operators:
                            partition_plans.append((ctr, total_operators - ctr))
                    else:
                        break
            else:
                break

        return partition_plans
