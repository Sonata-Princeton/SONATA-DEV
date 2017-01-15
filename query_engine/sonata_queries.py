#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import math

from query_engine.sonata_operators.distinct import Distinct
from query_engine.sonata_operators.map import Map
from query_engine.sonata_operators.query import Query
from query_engine.sonata_operators.reduce import Reduce

import query_engine.p4_queries as p4
import query_engine.plans_search as rs
import query_engine.spark_queries as spark
from query_engine.sonata_operators.filter import Filter
from query_engine.utils import *

pstream_qid = 1

class PacketStream(Query):
    def __init__(self, id=0, training_data_fname='', isInput=True):

        self.qid = id
        self.name = 'PacketStream'

        self.fields = tuple(self.basic_headers)
        self.keys = tuple(self.basic_headers)
        self.values = ()
        self.fields = self.keys + self.values
        self.training_data_fname = training_data_fname
        self.operators = []
        # Is this the original input query from the operator
        self.isInput = isInput

        self.left_child = None
        self.right_child = None

        self.refined_queries = {}
        self.partition_plans = []
        self.partition_plan_final = None
        self.dp_query = None
        self.sp_query = None
        self.dp_compile_mode = 'init'
        self.sp_compile_mode = 'init'
        self.expr = ''
        self.refinement_filter_id = 0

        self.qid_2_dp_queries = {}
        self.qid_2_sp_queries = {}

        # Attributes related to refinement tree
        self.query_tree = {}
        self.query_2_plans = {}
        self.all_queries = {}
        self.query_2_cost = {}
        self.query_2_final_plan = {}
        self.query_2_refinement_levels = {}
        self.query_in_mapping = {}
        self.query_out_mapping = {}
        self.query_2_refinement_levels = {}
        self.refined_query_2_original = {}
        self.all_queries[self.qid] = self

        # Object representing the output of the query
        self.output = None

        self.reduction_key = ''

    def __repr__(self):
        out = ''
        if self.left_child is not None:
            out += self.right_child.__repr__()
            out += '.Join(qid=' + str(self.qid) + ', q_left='
            out += "" + self.left_child.__repr__()
            out += ')\n'
        else:
            out += 'In'

        for operator in self.operators:
            out += operator.__repr__() + "\n\t"

        return out

    def map(self, append_type=0, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        if 'values' in map_dict:
            self.values = map_dict['values']

        if append_type == 0:
            operator = Map(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(),
                           *args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Map(prev_keys=self.basic_headers, prev_values=(),
                           *args, **kwargs)
            self.operators = [operator] + self.operators

        return self

    def reduce(self, *args, **kwargs):
        operator = Reduce(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(),
                          *args, **kwargs)
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        operator = Distinct(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(),
                            *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, append_type=0, *args, **kwargs):
        """
        :param append_type:
        :param args:
        :param kwargs:
        :return:
        """
        if append_type == 0:
            operator = Filter(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(),
                              *args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Filter(prev_keys=self.basic_headers, prev_values=(),
                              *args, **kwargs)
            self.operators = [operator] + self.operators

        return self

    def join(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        left_query = map_dict['query']
        new_qid = map_dict['new_qid']
        new_query = PacketStream(new_qid)
        new_query.right_child = self
        new_query.left_child = left_query

        return new_query

    def get_concise_query(self):
        unique_keys = {}
        for operator in self.operators:
            if operator.name in ["Distinct", "Map", "Reduce"]:
                for k in operator.keys:
                    if k not in ["count"]:
                        unique_keys[k] = 0
            elif operator.name in ["Filter"]:
                for k in operator.filter_keys:
                    if k not in ["count"]:
                        unique_keys[k] = 0

        #print "Concise Query: ", self.qid, unique_keys.keys()
        concise_query = PacketStream()
        concise_query.basic_headers = unique_keys.keys()
        for operator in self.operators:
            copy_operators(concise_query, operator)
        return concise_query

    def get_prev_keys(self):
        if len(self.operators) > 0:
            prev_keys = self.operators[-1].keys
        else:
            prev_keys = self.basic_headers
        return prev_keys

    def get_prev_values(self):
        if len(self.operators) > 0:
            prev_values = self.operators[-1].values
        else:
            prev_values = ()
        return prev_values

    def get_query_tree(self):
        self.query_tree = {self.qid: {}}
        # print "Root:", self
        if self.right_child is not None:
            # print "Left:", self.left_child
            # print "Right", self.right_child
            self.query_tree[self.qid][self.left_child.qid] = self.left_child.get_query_tree()[self.left_child.qid]
            self.query_tree[self.qid][self.right_child.qid] = self.right_child.get_query_tree()[self.right_child.qid]
        return self.query_tree

    def get_all_queries(self):
        if self.right_child is not None:
            self.all_queries.update(self.left_child.get_all_queries())
            self.all_queries.update(self.right_child.get_all_queries())

            # print "[get_all_queries]:", self.all_queries
        return self.all_queries

    def get_partition_plans(self):
        def get_bin(x, n):
            return format(x, 'b').zfill(n)

        query_2_plans = {}
        for query_id in self.all_queries:
            query = self.all_queries[query_id]
            #print "Exploring partitioning plans for", query.qid
            red_operators = []
            # We will count how many operators (that matter) can either be executed in DP or SP
            n_operators = 0
            for operator in query.operators:
                if operator.name in ['Distinct', 'Reduce']:
                    # Only distinct and reduce matter when making query partitioning decisions
                    n_operators += 1
                    red_operators.append(operator.name)
            # TODO: Explore how we can make decisions regarding offloading of join operation
            #print "Reduction Operators", red_operators
            # TODO: apply constraints to further make the number of possible plans realistic
            if n_operators > 1:
                plans = range(int(math.pow(2, n_operators)))
            elif n_operators == 1:
                plans = range(2)
            else:
                plans = []
            refined_plans = []

            for plan in plans:
                plan_b = get_bin(plan, len(red_operators))
                is_allowed = True
                has_one = False
                ctr = 0
                for elem in plan_b:
                    if elem == '1':
                        has_one = True
                    if elem == '0' and has_one:
                        is_allowed = False
                    ctr += 1

                #print "Plan", plan, plan_b, is_allowed
                if is_allowed:
                    refined_plans.append(plan_b)
            #print plans, refined_plans
            query_2_plans[query_id] = refined_plans
            # query_2_plans[query_id] = plans
        self.query_2_plans = query_2_plans
        return query_2_plans

    def get_cost(self, ref_levels):
        query_2_cost = {}
        for query_id in self.all_queries:
            query_2_cost[query_id] = {}
            plans = self.query_2_plans[query_id]
            for p1 in plans:
                for p2 in plans:
                    # For each path combination for each query we generate cost using the cost function above.
                    # TODO: replace this with cost model based on training data
                    tmp = rs.generate_costs(p1, p2, ref_levels)
                    for transit in tmp:
                        query_2_cost[query_id][(p1, p2), transit] = tmp[transit]
        self.query_2_cost = query_2_cost
        #print "Cost", self.query_2_cost
        return query_2_cost

    def get_refinement_plan(self, ref_levels):
        query_2_final_plan = {}
        memorized_plans = {}
        for query_id in self.query_tree:
            # We start with the finest refinement level, as expressed in the original query
            rs.get_refinement_plan(ref_levels[0], ref_levels[-1], query_id, ref_levels, self.query_2_plans,
                                   self.query_tree,
                                   self.query_2_cost, query_2_final_plan, memorized_plans)

        self.query_2_final_plan = query_2_final_plan
        return query_2_final_plan

    def get_reduction_key(self):
        red_keys = set([])
        if self.left_child is not None:
            red_keys_left = self.left_child.get_reduction_key()
            red_keys_right = self.right_child.get_reduction_key()
            #print "left keys", red_keys_left, self.qid
            #print "right keys", red_keys_right, self.qid
            # TODO: make sure that we better handle the case when first reduce operator has both sIP and dIP as reduction keys
            if len(red_keys_right) > 0:
                red_keys = set(red_keys_left).intersection(red_keys_right)
            else:
                red_keys = set(red_keys_left)

            for operator in self.operators:
                if operator.name in ['Distinct', 'Reduce']:
                    red_keys = red_keys.intersection(set(operator.keys))
                    #print self.qid, operator.name, red_keys

            red_keys = red_keys.intersection(self.refinement_headers)

        else:
            #print "Reached leaf node", self.qid
            red_keys = set(self.basic_headers)
            for operator in self.operators:
                # Extract reduction keys from first reduce/distinct operator
                if operator.name in ['Distinct', 'Reduce']:
                    red_keys = red_keys.intersection(set(operator.keys))
                    #print self.qid, operator.name, red_keys
                    #break

        #print "Reduction Key Search", self.qid, red_keys
        return red_keys

    def generate_query_out_mapping(self):
        query_out_mapping = {}
        for (qid, ref_level) in self.query_in_mapping:
            for elem in self.query_in_mapping[(qid, ref_level)]:
                if elem not in query_out_mapping:
                    query_out_mapping[elem] = []
                query_out_mapping[elem].append((qid, ref_level))

        self.query_out_mapping = query_out_mapping
        return query_out_mapping

    def get_orig_refined_mapping(self):
        # for each sub query, we generate mapping for each refinement level
        orig_2_refined = {}
        refined_2_orig = {}
        for orig_queryId in self.query_2_refinement_levels:
            ref_plan = self.query_2_refinement_levels[orig_queryId].keys()
            ref_plan.sort()
            ctr = 1
            for ref_level in ref_plan:
                refined_queryId = 10000 * orig_queryId + ref_level
                ctr += 1
                orig_2_refined[(orig_queryId, ref_level)] = refined_queryId
                refined_2_orig[refined_queryId] = (orig_queryId, ref_level)

        self.orig_2_refined = orig_2_refined
        self.refined_2_orig = refined_2_orig
        return (orig_2_refined, refined_2_orig)

    def generate_query_in_mapping(self, fp, query_2_final_plan, query_in_mapping={}, query_input=[], is_right=False):
        query_id = self.qid
        #print "Exploring", query_id, "input", query_input
        prev_ref_level = 0
        last_level = 0

        if query_id in query_2_final_plan:
            ref_plan, cost = query_2_final_plan[query_id][fp]
            ref_plans_to_explore = ref_plan[1:]
            if is_right:
                # We will join the left child query with the parent query for their finest level of refinement, thus
                # explore one less refinement level for it
                if len(ref_plans_to_explore) > 1:
                    ref_plans_to_explore = ref_plans_to_explore[:-1]
                else:
                    ref_plans_to_explore = []

            if len(ref_plans_to_explore) > 0:
                # first refinement level for child queries might also take input from the output of parent query for
                # their previous refinement level
                init_ref_level = ref_plans_to_explore[0][1]
                if (query_id, init_ref_level) not in query_in_mapping:
                    query_in_mapping[(query_id, init_ref_level)] = []

                for elem in query_input:
                    #print "Adding", elem, "for", query_id, init_ref_level, query_input
                    # We only expect a single input in this case, maybe change the tuple to elem later
                    query_in_mapping[(query_id, init_ref_level)].append(elem)

                for part_plan, ref_level in ref_plans_to_explore:
                    query_input = []
                    #print "Generating Query Mapping for", query_id, ref_level, query_input
                    if (query_id, ref_level) not in query_in_mapping:
                        query_in_mapping[(query_id, ref_level)] = []

                    if prev_ref_level > 0:
                        query_input.append((query_id, prev_ref_level))
                        if self.right_child is None:
                            query_in_mapping[(query_id, ref_level)].append((query_id, prev_ref_level))

                    if self.right_child is not None:
                        # treat right child differently...they are special kids ;)
                        tmp = self.right_child.generate_query_in_mapping(ref_level, query_2_final_plan, query_in_mapping,
                                                                         query_input=query_input, is_right=True)
                        if tmp != ():
                            query_in_mapping[(query_id, ref_level)].append(tmp)

                        tmp = self.left_child.generate_query_in_mapping(ref_level, query_2_final_plan,
                                                                         query_in_mapping,
                                                                         query_input=query_input)
                        if tmp != ():
                            query_in_mapping[(query_id, ref_level)].append(tmp)

                    #print "Mapping for", query_id, ref_level, "is", query_in_mapping[(query_id, ref_level)], query_input
                    # Update these variables for next iteration
                    prev_ref_level = ref_level
                    last_level = ref_level

        self.query_in_mapping = query_in_mapping

        if last_level > 0:
            return tuple([query_id, last_level])
        else:
            return ()

    def get_query_2_refinement_levels(self, fp, query_2_final_plan, query_2_refinement_levels={}):
        for queryId in self.query_tree:
            if queryId not in query_2_refinement_levels:
                query_2_refinement_levels[queryId] = {}

            if queryId in query_2_final_plan:
                ref_plan, cost = query_2_final_plan[queryId][fp]
                for part_plan, ref_level in ref_plan[1:]:
                    query_2_refinement_levels[queryId][ref_level] = part_plan

                    if self.left_child is not None:
                        self.left_child.get_query_2_refinement_levels(ref_level, query_2_final_plan,
                                                                      query_2_refinement_levels)
                        self.right_child.get_query_2_refinement_levels(ref_level, query_2_final_plan,
                                                                       query_2_refinement_levels)
        # print query_2_refinement_levels
        self.query_2_refinement_levels = query_2_refinement_levels
        return query_2_refinement_levels

    def generate_refined_queries(self, red_key):
        """
        :param red_key:
        :return: refined_queries:
        """
        refined_queries = {}
        refined_query_2_original = {}
        for queryId in self.query_2_refinement_levels:
            refined_queries[queryId] = {}
            q_ctr = 1
            for ref_level in self.query_2_refinement_levels[queryId]:
                # print "Adding refined query for", queryId, ref_level
                #print self.all_queries
                original_query = self.all_queries[queryId]
                new_qid = original_query.qid * 10000 + ref_level
                q_ctr += 1
                refined_query = PacketStream(new_qid)

                concise_query = original_query.get_concise_query()
                if original_query.right_child is not None:
                    concise_right = original_query.right_child.get_concise_query()
                    concise_left = original_query.left_child.get_concise_query()
                    refined_query.basic_headers = list(set(concise_query.basic_headers)
                                                       .union(set(concise_right.basic_headers)))
                else:
                    refined_query.basic_headers = concise_query.basic_headers
                #print "Basic headers for ", queryId, refined_query.basic_headers

                # print self.query_in_mapping
                if (queryId, ref_level) in self.query_in_mapping:
                    for (orig_qid_src, mask) in self.query_in_mapping[(queryId, ref_level)]:
                        refined_qid_src = self.orig_2_refined[(orig_qid_src, mask)]
                        refined_query.filter(append_type=1, src=refined_qid_src, filter_keys=(red_key,),
                                             func=('mask',mask,))

                refined_query.map(map_keys=(red_key,), func=("mask", ref_level))
                if original_query.right_child is not None:
                    #print "Left Child", concise_left.keys, concise_left.operators[-1].keys
                    #print "Right Child", concise_right.operators[-1].keys, concise_right.operators[-1].values
                    #refined_query.map(keys=list(set(concise_left.operators[-1].keys)
                    #                        .union(set(concise_right.operators[-1].keys))
                    #                        .union(set(concise_right.operators[-1].values))))
                    # TODO: get rid of this redundancy
                    for operator in concise_right.operators:
                        copy_operators(refined_query, operator)

                for operator in concise_query.operators:
                    copy_operators(refined_query, operator)

                refined_query.isInput = False
                # print "Added refined query for", queryId, ref_level
                refined_queries[queryId][ref_level] = refined_query
                refined_query_2_original[refined_query.qid] = (queryId, ref_level)

        self.refined_queries = refined_queries
        self.refined_query_2_original = refined_query_2_original
        return refined_queries

    def generate_partitioned_queries(self):

        """
        Generates P4 query and Sonata query object for each refined query.
        :return:
        """

        def set_partition_with_payload_processing(p4_query, operator):
            #print "Partition set with payload processing for", operator.name
            p4_query.parse_payload = True
            return max_dp_operators


        for (queryId, ref_level) in self.query_in_mapping.keys():
            # partitioning plan is a bit string. For example for a query with partitioning
            # plan `001` means that it will add the first two reduce operators to
            # the P4 query and the last one to the Spark query
            # It is easy to apply the logic of partitioning the reduce operatos, however, we
            # want to make sure that even if there are no reduce operators in the
            # data plane, we execute basic filtering and map operations in the data plane,
            # We are using the data plane to parse the incoming packet stream to packet
            # tuples (qid, ...) that can be processed by the stream processor, thus we need to
            # make sure that each query has its basic map/filter function in the data plane.

            partitioning_plan = self.query_2_refinement_levels[queryId][ref_level]
            # `max_dp_operators` is the number of reduction operators to be added to the P4 query
            max_dp_operators = 0
            for elem in str(partitioning_plan):
                if elem == '0':
                    max_dp_operators += 1
                else:
                    break

            refined_query = self.refined_queries[queryId][ref_level]

            # Even if the query has payload field in packet tuple, we exclude that from
            # our P4 query object as we can't parse it in the data plane
            p4_basic_headers = filter(lambda x: x != "payload", refined_query.basic_headers)
            #print "p4_basic_headers", p4_basic_headers, refined_query.basic_headers

            # Initialize P4 query
            p4_query = p4.QueryPipeline(refined_query.qid).map_init(keys=p4_basic_headers)
            p4_query.parse_payload = False

            # Initialize Spark Query
            spark_query = (spark.PacketStream(refined_query.qid))

            print queryId, ref_level, partitioning_plan, max_dp_operators
            print "Original Refined Query before partitioning:\n", refined_query
            # number of reduce operators delegated so far
            in_dataplane = 0
            # our implementation requires duplicating the last (border) reduce
            # operator in P4 query to Spark query, the reason is that ours is not
            # just reduce, it is reduce and filter, so after the count exceeds
            # the threshold, it emits all the packet tuples with count 1.
            # Thus we require duplicating the reduce operator.
            border_reduce = None
            # In future, we should not require this map operation that needs to
            # be applied before the border reduce operator.
            border_map = None

            # To ensure that we initialize the spark query only once
            init_spark = True

            for operator in refined_query.operators:
                if in_dataplane < max_dp_operators:
                    #print "Making partitioning decision for", operator, in_dataplane, p4_query.parse_payload
                    if not p4_query.parse_payload:
                        # Check whether we can support these operators in the data plane, and if
                        # we need to parse packet payload in the stream processor
                        if operator.name in ['Filter']:
                            if "payload" in operator.filter_keys or "payload" in operator.filter_vals:
                                in_dataplane = set_partition_with_payload_processing(p4_query, operator)
                        elif operator.name in ['Map']:
                            if len(operator.map_keys) == 0:
                                if "payload" in operator.keys or "payload" in operator.values:
                                    in_dataplane = set_partition_with_payload_processing(p4_query, operator)
                            else:
                                if "payload" in operator.map_keys or "payload" in operator.map_values:
                                    in_dataplane = set_partition_with_payload_processing(p4_query, operator)
                        else:
                            if "payload" in operator.keys or "payload" in operator.values:
                                in_dataplane = set_partition_with_payload_processing(p4_query, operator)

                    if operator.name == 'Reduce':
                        in_dataplane += 1
                        copy_sonata_operators_to_p4(p4_query, operator)
                        #print "R1 - P4", in_dataplane, max_dp_operators

                        # duplicate implementation of reduce operators at the border
                        if in_dataplane == max_dp_operators:
                            border_reduce = p4_query.operators[-1]
                            #print "Adding border reduce to Spark", border_reduce

                            if init_spark:
                                init_spark, spark_query = initialize_spark_query(p4_query,
                                                                                 spark_query,
                                                                                 refined_query.qid)
                            # Add the map operator before this border reduce operator to select the right reduction keys
                            if border_map is not None:
                                border_map.func = ()
                                copy_sonata_operators_to_spark(spark_query, border_map)
                            copy_sonata_operators_to_spark(spark_query, operator)

                    elif operator.name == 'Map':
                        if len(operator.func) > 0 and operator.func[0] == 'mask':
                            copy_sonata_operators_to_p4(p4_query, operator)
                        else:
                            # TODO: think of a better logic to identify the border map operator
                            border_map = operator

                    elif operator.name == 'Filter':
                        # check if previous operator was reduce
                        if len(operator.func) > 0 and operator.func[1] == 'geq':
                            if len(p4_query.operators) > 0 and p4_query.operators[-1].name == "Reduce":
                                prev_operator = p4_query.operators[-1]
                                # update the threshold for the previous Reduce operator
                                # TODO: assumes func is `geq`, implement others
                                prev_operator.thresh = operator.func[1]
                        else:
                            copy_sonata_operators_to_p4(p4_query, operator)

                    elif operator.name == 'Distinct':
                        in_dataplane += 1
                        copy_sonata_operators_to_p4(p4_query, operator)

                else:
                    if init_spark:
                        init_spark, spark_query = initialize_spark_query(p4_query,
                                                                         spark_query,
                                                                         refined_query.qid)
                    #print "Adding", operator
                    if operator.name == "Filter":
                        #print "Filter", operator.func, border_reduce
                        if len(operator.func) > 0 and operator.func[0] == 'geq' and border_reduce is not None:
                            border_reduce.thresh = operator.func[1]
                            #print "Updated threshold", border_reduce.thresh, " for", border_reduce.name
                            copy_sonata_operators_to_spark(spark_query, operator)
                        elif len(operator.func) > 0 and operator.func[0] == 'mask':
                            copy_sonata_operators_to_p4(p4_query, operator)
                        elif len(operator.func) > 0 and operator.func[0] == 'eq' and 'payload' not in operator.filter_keys:
                            copy_sonata_operators_to_p4(p4_query, operator)
                        else:
                            copy_sonata_operators_to_spark(spark_query, operator)

                    elif operator.name == "Map":
                        if len(operator.func) > 0 and operator.func[0] == 'mask':
                            copy_sonata_operators_to_p4(p4_query, operator)
                        else:
                            copy_sonata_operators_to_spark(spark_query, operator)
                    else:
                        copy_sonata_operators_to_spark(spark_query, operator)

            print "After Partitioning, P4:\n", p4_query
            print "After Partitioning, Spark:\n", spark_query
            self.qid_2_dp_queries[refined_query.qid] = p4_query
            self.qid_2_sp_queries[refined_query.qid] = spark_query
            refined_query.dp_query = p4_query
            refined_query.sp_query = spark_query
        return 0


if __name__ == "__main__":
    # Basic test setup for IR and QP implementations
    q0 = PacketStream(0)
    q1 = PacketStream(1).map(keys=("dIP",), func=("mask", 16)).distinct(keys=("dIP",))
    q2 = (PacketStream(2).map(keys=('dIP',), values=tuple([x for x in q0.basic_headers])).distinct(keys=('dIP',)))
    q3 = q2.join(new_qid=3, query=q1).map(keys=("dIP",), func=("mask", 16)).distinct(keys=("dIP",))

    q3.get_query_tree()
    q3.get_all_queries()
    q3.get_partition_plans()

    # TODO: get rid of this hardcoding
    reduction_key = 'dIP'
    ref_levels = range(0, 33, 4)
    finest_plan = ref_levels[-1]

    q3.get_cost(ref_levels)
    q3.get_refinement_plan(ref_levels)
    print q3.query_2_final_plan
    q3.generate_query_in_mapping(finest_plan, q3.query_2_final_plan)
    print "query_in_mapping:", q3.query_in_mapping
    print "query_out_mapping:", q3.generate_query_out_mapping()

    print q3.get_query_2_refinement_levels(finest_plan, q3.query_2_final_plan)
    print q3.get_orig_refined_mapping()
    q3.generate_refined_queries(reduction_key)
    # q3.generate_partitioned_queries()
    print q3.refined_queries
    # print q3.refined_queries
    # print q3.query_2_plans
