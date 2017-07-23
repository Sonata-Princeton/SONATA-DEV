#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

# from integration import *

from sonata.dataplane_driver.query_object import QueryObject as DP_QO
from sonata.streaming_driver.query_object import PacketStream as SP_QO
from sonata.query_engine.utils import copy_operators
from sonata.core.utils import requires_payload_processing, copy_sonata_operators_to_sp_query,\
    get_flattened_sub_queries, get_payload_fields, flatten_streaming_field_names
from sonata.query_engine.sonata_queries import PacketStream
from sonata.system_config import BASIC_HEADERS
from integration import sonata_2_dp_query


def get_dataplane_query(query, qid, partition_plan):
    # number of operators in the data plane
    n_operators_dp = int(partition_plan)
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
        dp_query.payload_fields = get_payload_fields(query)
        print "Payload Fields", dp_query.payload_fields

    return dp_query


def get_streaming_query(query, qid, partition_plan):
    # number of operators in the data plane
    n_operators_dp = int(partition_plan)
    n_operators_sp = int(len(query.operators))-n_operators_dp
    if n_operators_sp > 0:
        # create a sp query object
        sp_query = SP_QO(qid)
        if n_operators_dp > 0:
            # update the basic headers
            # Add 'k' field to filter out garbled message received by the stream processor
            sp_query.basic_headers = list(query.operators[n_operators_dp-1].keys) + list(query.operators[n_operators_dp-1].values)

            sp_query.basic_headers = flatten_streaming_field_names(sp_query.basic_headers)

            border_operator = query.operators[n_operators_dp-1]
            if border_operator.name == "Reduce":
                # We need to duplicate reduce operator in the data plane
                n_operators_dp -= 1


        # Filter step is added to map incoming packet streams from multiple dataflow pipelines
        # to their respective pipelines in the stream processor
        # sp_query = sp_query.filter_init(qid=qid, keys=sp_query.basic_headers)
        dp_operator = query.operators[n_operators_dp-1]
        if hasattr(dp_operator,"map_values"):
            sp_query.map(keys=flatten_streaming_field_names(dp_operator.keys),
                         values=flatten_streaming_field_names(dp_operator.map_values))
        else:
            sp_query.map(keys=flatten_streaming_field_names(dp_operator.keys),
                         values=list())

        # Update the remainder operators
        for operator in query.operators[n_operators_dp:]:
            copy_sonata_operators_to_sp_query(sp_query, operator)

        sp_query.parse_payload = requires_payload_processing(query)

        return sp_query



class Partition(object):
    intermediate_learning_queries = {}
    filter_mappings = {}

    def __init__(self, query, target, ref_level=32):
        self.query = query
        self.target = target
        self.ref_level = ref_level

    def generate_partitioned_queries_learning(self):
        sonata_query = self.query
        partition_plans_learning = self.get_partition_plans_learning(sonata_query)
        # print partition_plans_learning
        intermediate_learning_queries = {}
        prev_qid = 0
        filter_mappings = {}
        filters_marked = {}
        for max_operators in partition_plans_learning:
            qid = 1000*sonata_query.qid+max_operators
            tmp_query = (PacketStream(sonata_query.qid))
            tmp_query.basic_headers = BASIC_HEADERS
            ctr = 0
            filter_ctr = 0
            prev_operator = None
            for operator in sonata_query.operators:
                can_increment = True
                if operator.name != 'Join':
                    if ctr < max_operators:
                        copy_operators(tmp_query, operator)
                        prev_operator = operator
                    else:
                        break
                    if operator.name == 'Filter':
                        filter_ctr += 1
                        if (qid, self.ref_level, filter_ctr) not in filters_marked:
                            filters_marked[(qid, self.ref_level, filter_ctr,)] = sonata_query.qid
                            filter_mappings[(prev_qid, qid, self.ref_level)] = (
                            sonata_query.qid, filter_ctr, operator.func[1])
                else:
                    prev_operator = operator
                    copy_operators(tmp_query, operator)

                if operator.name == 'Map':
                    if hasattr(operator, 'func') and len(operator.func) > 0:
                        if operator.func[0] == 'mask':
                            can_increment = False
                if can_increment:
                    ctr += 1


            intermediate_learning_queries[qid] = tmp_query
            prev_qid = qid

        self.intermediate_learning_queries = intermediate_learning_queries
        self.filter_mappings = filter_mappings

    def get_query_2_plans(self):
        query_2_plans = {}
        for q in get_flattened_sub_queries(self.query):
            n_operators = len(q.operators)
            partitioning_plans = self.get_partition_plans(q)
            # TODO: get rid of this hardcoding
            # partitioning_plans = ['00', '01', '11']
            query_2_plans[q.qid] = partitioning_plans
        print "Partitioning Plans", query_2_plans

        return query_2_plans

    def get_partition_plans(self, dp_query):
        # receives dp_query object.
        total_operators = len(dp_query.operators)
        partition_plans = [0]
        ctr = 1
        for operator in dp_query.operators:
            can_increment = True
            #print operator, partition_plans
            if operator.name in self.target.supported_operators.keys():
                if hasattr(operator, 'func') and len(operator.func) > 0:
                    if operator.func[0] in self.target.supported_operators[operator.name]:
                        if operator.name in self.target.costly_operators:
                            partition_plans.append(ctr)
                    else:
                        break
                else:
                    if operator.name in self.target.costly_operators:
                        partition_plans.append(ctr)
            else:
                break
            if operator.name == 'Map':
                if hasattr(operator, 'func') and len(operator.func) > 0:
                    if operator.func[0] == 'mask':
                        can_increment = False
            if can_increment:
                ctr += 1

        return partition_plans

    def get_partition_plans_learning(self, query):
        # receives dp_query object.
        total_operators = len(query.operators)
        partition_plans_learning = []
        ctr = 1
        for operator in query.operators:
            can_increment = True
            if operator.name in self.target.supported_operators.keys():
                if hasattr(operator, 'func') and len(operator.func) > 0:
                    if operator.func[0] in self.target.supported_operators[operator.name]:
                        if operator.name in self.target.learning_operators:
                            partition_plans_learning.append(ctr)
                    else:
                        break
                else:
                    if operator.name in self.target.learning_operators:
                        partition_plans_learning.append(ctr)
            else:
                break

            if operator.name == 'Map':
                if hasattr(operator, 'func') and len(operator.func) > 0:
                    if operator.func[0] == 'mask':
                        can_increment = False

            if can_increment:
                ctr += 1
            #print operator.name, partition_plans_learning
        partition_plans_learning.append(len(query.operators))
        return partition_plans_learning
