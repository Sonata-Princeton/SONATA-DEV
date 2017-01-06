#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import copy
import math
import p4_queries as p4
import spark_queries as spark
import logging
import backtrack as bt

logging.getLogger("sonata_queries")

pstream_qid = 1


def get_original_wo_mask(lstOfFields):
    fields = []

    for field in lstOfFields:
        if '/' in field:
            fields.append(field.split('/')[0])
        else:
            fields.append(field)

    return fields


class Query(object):
    """
    Abstract Query Class
    """
    basic_headers = ["sIP", "sPort", "dIP", "dPort", "nBytes",
                     "proto", "sMac", "dMac", "payload"]

    def __init__(self, *args, **kwargs):
        self.fields = []
        self.keys = []
        self.values = []
        self.expr = ''
        self.name = ''

    def eval(self):
        """
        evaluate this policy
        :param ?
        :type pkt: ?
        :rtype: ?
        """
        return self.expr


class Map(Query):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        self.name = 'Map'
        map_dict = dict(*args, **kwargs)
        if 'prev_fields' in map_dict:
            self.prev_fields = map_dict['prev_fields']

        self.keys = ()
        self.values = ()
        self.func = ()

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        if 'values' in map_dict:
            self.values = map_dict['values']
        if "func" in map_dict:
            self.func = map_dict['func']

        # print(self.keys, self.values)
        self.fields = tuple(list(self.keys) + list(self.values))

    def __repr__(self):
        return '.Map(keys=' + str(self.keys) + ', values=' + str(self.values) + ', func=' + str(self.func) + ')'


class Reduce(Query):
    def __init__(self, *args, **kwargs):
        super(Reduce, self).__init__(*args, **kwargs)
        self.name = 'Reduce'
        map_dict = dict(*args, **kwargs)
        #print map_dict

        self.keys = map_dict['keys']
        self.prev_fields = map_dict['prev_fields']
        self.values = map_dict['values']
        self.func = map_dict['func']
        self.fields = tuple(list(self.prev_fields[:-1]) + list(self.values))
        # self.fields = tuple(set(self.fields).difference(set("1")))

    def __repr__(self):
        return '.Reduce(func=' + self.func + ', values=' + ','.join([x for x in self.values]) + ')'


class Distinct(Query):
    def __init__(self, *args, **kwargs):
        super(Distinct, self).__init__(*args, **kwargs)
        self.name = 'Distinct'
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.fields = self.prev_fields

    def __repr__(self):
        return '.Distinct()'


class Join(Query):
    def __init__(self, *args, **kwargs):
        super(Join, self).__init__(*args, **kwargs)
        self.name = 'Join'
        map_dict = dict(*args, **kwargs)
        self.query = map_dict['query']

    def __repr__(self):
        return '.Join(query=' + self.query.__repr__() + ')'


class Filter(Query):
    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)
        self.name = 'Filter'
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.fields = self.prev_fields
        self.keys = map_dict['keys']
        if 'values' in map_dict:
            self.values = map_dict['values']
        else:
            self.values = ()
        if 'comp' in map_dict:
            self.comp = map_dict['comp']
        else:
            self.comp = 'eq'
        self.mask = ()
        if 'mask' in map_dict:
            self.mask = map_dict['mask']

        self.src = 0
        if 'src' in map_dict:
            self.src = map_dict['src']

    def __repr__(self):
        return '.Filter(keys=' + str(self.keys) + ', values = ' + str(self.values) + ', comp=' + str(
            self.comp) + ' mask =' + str(self.mask) + ' src = '+str(self.src)+')'


class PacketStream(Query):
    def __init__(self, id=0, training_data_fname='', isInput=True):
        # type: (object, object, object, object) -> object
        # super(PacketStream, self).__init__(*args, **kwargs)

        self.qid = id
        self.name = 'PacketStream'

        self.fields = tuple(self.basic_headers)
        self.keys = tuple([self.basic_headers[0]])
        self.values = tuple(self.basic_headers[1:])
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

    def __repr__(self):
        out = 'In'
        if self.left_child is not None:
            for operator in self.left_child.operators:
                out += operator.__repr__()
            out += '\n\t.Join('
            for operator in self.right_child.operators:
                out += operator.__repr__()
            out += ')\n\t'

        for operator in self.operators:
            out += operator.__repr__()

        return out

    def map(self, append_type=0, *args, **kwargs):
        # type: (object, object, object) -> object
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        self.keys = keys
        if 'values' in map_dict:
            values = map_dict['values']
            self.values = values

        if append_type == 0:
            operator = Map(prev_fields=self.get_prev_fields(), *args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Map(prev_fields=self.basic_headers, *args, **kwargs)
            self.operators = [operator] + self.operators

        return self

    def reduce(self, *args, **kwargs):
        operator = Reduce(prev_fields=self.get_prev_fields(), *args, **kwargs)
        map_dict = dict(*args, **kwargs)
        values = map_dict['values']
        self.values = values
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        # type: (object, object) -> object
        operator = Distinct(prev_fields=self.get_prev_fields(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, append_type=0, *args, **kwargs):
        """
        :param append_type:
        :param args:
        :param kwargs:
        :return:
        """
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        self.keys = keys

        if append_type == 0:
            operator = Filter(prev_fields=self.get_prev_fields(), *args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Filter(prev_fields=self.basic_headers, *args, **kwargs)
            self.operators = [operator] + self.operators

        return self

    def join(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        right_query = map_dict['query']
        new_qid = map_dict['new_qid']
        new_query = PacketStream(new_qid)
        new_query.left_child = self
        new_query.right_child = right_query
        return new_query


    def get_concise_query(self):
        unique_keys = {}
        for operator in self.operators:
            for k in operator.keys:
                unique_keys[k] = 0

        concise_query = PacketStream()
        concise_query.basic_headers = unique_keys.keys()
        #print "Basic headers for concise query", concise_query.basic_headers
        for operator in self.operators:
            # print operator
            if operator.name == 'Filter':
                concise_query.filter(keys=operator.keys,
                                     values=operator.values,
                                     comp=operator.comp)
            elif operator.name == "Map":
                # print "Concise query:: Map.keys", operator.keys
                concise_query.map(keys=operator.keys, values=operator.values)
            elif operator.name == "Reduce":
                concise_query.reduce(keys = operator.keys,
                                     values=operator.values,
                                     func=operator.func)

            elif operator.name == "Distinct":
                concise_query.distinct()

            elif operator.name == "Join":
                concise_query.join(query=operator.query.get_concise_query())

        return concise_query

    def get_partitioning_plan(self, part):
        if not self.isInput:
            dp_query = PacketStream(isInput=False)
            sp_query = PacketStream(isInput=False)
            dp_query.basic_headers = self.basic_headers
            sp_query.basic_headers = self.basic_headers
            partition_plan = {0: dp_query, 1: sp_query}
            for operator in self.operators[:part]:
                new_operator = copy.deepcopy(operator)
                dp_query.operators.append(new_operator)

            for operator in self.operators[part - 1:]:
                new_operator = copy.deepcopy(operator)
                sp_query.operators.append(new_operator)
            self.partition_plans.append(partition_plan)
        else:
            raise NotImplementedError

    def get_query_cost(self):
        if not self.isInput:
            return 0
        else:
            raise NotImplementedError

    def generate_dp_query(self, qid):
        if not self.isInput:
            if self.partition_plan_final is not None:
                dp_query = self.partition_plan_final[0]
                dp_query.refinement_filter_id = self.refinement_filter_id
                p4_query = p4.QueryPipeline(qid).map_init(keys=dp_query.basic_headers)
                for operator in dp_query.operators:
                    if operator.name == 'Reduce':
                        p4_query = p4_query.reduce(keys=operator.prev_fields)
                    elif operator.name == 'Map':
                        p4_query = p4_query.map(keys=operator.keys,
                                                values=operator.values,
                                                func=operator.func
                                                )

                    elif operator.name == 'Filter':
                        p4_query = p4_query.filter(keys=operator.keys,
                                                   values=operator.values,
                                                   mask=operator.mask,
                                                   comp=operator.comp)
                    elif operator.name == 'Distinct':
                        p4_query = p4_query.distinct(keys=operator.prev_fields)
                self.dp_query = p4_query
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    def generate_sp_query(self, qid):
        if not self.isInput:
            if self.partition_plan_final is not None:
                sp_query = self.partition_plan_final[1]
                spark_query = spark.PacketStream(qid).filter(prev_fields="p", expr="p[1] == '" + str(qid) + "'").map(
                    prev_fields=("p",), keys=("p[2:]",))
                for operator in sp_query.operators:
                    if operator.name == "Map":
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        keys = get_original_wo_mask(operator.keys)
                        spark_query = spark_query.map(prev_fields=prev_fields,
                                                      keys=keys, values=operator.values)

                    if operator.name == "Reduce":
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.reduce(prev_fields=prev_fields,
                                                         func=operator.func,
                                                         values=operator.values)

                    if operator.name == "Distinct":
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.distinct(prev_fields=prev_fields)

                    if operator.name == "Filter":
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.filter(prev_fields=prev_fields,
                                                         expr=operator.expr)

                self.sp_query = spark_query
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    def compile_dp_query(self):
        # compile the data plane query
        if self.dp_query is not None:
            if self.dp_compile_mode == 'init':
                self.dp_query.compile_pipeline()
            else:
                self.dp_query.compile_delta()
        else:
            raise NotImplementedError

    def compile_sp_query(self):
        # compile the stream processor query
        if self.sp_query is not None:
            if self.sp_compile_mode == 'init':
                self.sp_query.compile_pipeline()
            else:
                self.sp_query.compile_delta()
        else:
            raise NotImplementedError

    def get_prev_fields(self):
        if len(self.operators) > 0:
            prev_fields = self.operators[-1].fields
        else:
            prev_fields = self.basic_headers
        return prev_fields


    def get_query_tree(self):
        self.query_tree = {self.qid: {}}
        if self.right_child is not None:
            self.query_tree[self.qid][self.right_child.qid] = self.right_child.get_query_tree()[self.right_child.qid]
            self.query_tree[self.qid][self.left_child.qid] = self.left_child.get_query_tree()[self.left_child.qid]
        return self.query_tree

    def get_all_queries(self):
        if self.right_child is not None:
            self.all_queries.update(self.right_child.get_all_queries())
            self.all_queries.update(self.left_child.get_all_queries())
        return self.all_queries

    def get_partition_plans(self):
        query_2_plans = {}
        for query_id in self.all_queries:
            query = self.all_queries[query_id]
            # We will count how many operators (that matter) can either be executed in DP or SP
            n_operators = 0
            for operator in query.operators:
                if operator.name in ['Distinct', 'Reduce']:
                    # Only distinct and reduce matter when making query partitioning decisions
                    n_operators += 1
            if query.right_child is not None:
                # And off course we care about whether join operator is executed in DP or SP
                n_operators += 1
            # TODO: apply constraints to further make the number of possible plans realistic
            if n_operators > 1:
                plans = range(int(math.pow(2, n_operators)-1))
            elif n_operators == 1:
                plans = range(2)
            else:
                plans = []
            query_2_plans[query_id] = plans
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
                    tmp = bt.generate_costs(ref_levels)
                    for transit in tmp:
                        query_2_cost[query_id][(p1, p2), transit] = tmp[transit]
        self.query_2_cost = query_2_cost
        return query_2_cost

    def get_refinement_plan(self, ref_levels):
        query_2_final_plan = {}
        memorized_plans = {}
        for query_id in self.query_tree:
            # We start with the finest refinement level, as expressed in the original query
            bt.get_refinement_plan(ref_levels[0], ref_levels[-1], query_id, ref_levels, self.query_2_plans, self.query_tree,
                                   self.query_2_cost, query_2_final_plan, memorized_plans)

        self.query_2_final_plan = query_2_final_plan
        return query_2_final_plan

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
        orig_2_refined = {}
        refined_2_orig = {}
        for orig_queryId in self.query_2_refinement_levels:
            ref_plan = self.query_2_refinement_levels[orig_queryId].keys()
            ref_plan.sort()
            ctr = 1
            print orig_queryId, ref_plan
            for ref_level in ref_plan:
                print ref_level
                refined_queryId = 10000*orig_queryId+ctr
                ctr += 1
                orig_2_refined[(orig_queryId, ref_level)] = refined_queryId
                refined_2_orig[refined_queryId] = (orig_queryId, ref_level)

        self.orig_2_refined = orig_2_refined
        self.refined_2_orig = refined_2_orig
        return (orig_2_refined, refined_2_orig)

    def generate_query_in_mapping(self, fp, query_2_final_plan, query_in_mapping = {}, query_input = [], is_left = False):
        query_id = self.qid
        #print "Exploring", query_id, "input", query_input
        prev_ref_level = 0
        last_level = 0

        if query_id in query_2_final_plan:
            ref_plan, cost = query_2_final_plan[query_id][fp]
            ref_plans_to_explore = ref_plan[1:]
            if is_left:
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
                    print "Adding", elem, "for", query_id, init_ref_level, query_input
                    # We only expect a single input in this case, maybe change the tuple to elem later
                    query_in_mapping[(query_id, init_ref_level)].append(elem)

                for part_plan, ref_level in ref_plans_to_explore:
                    query_input = []
                    print "Generating Query Mapping for", query_id, ref_level, query_input
                    if (query_id, ref_level) not in query_in_mapping:
                        query_in_mapping[(query_id, ref_level)] = []

                    if prev_ref_level > 0:
                        query_input.append((query_id, prev_ref_level))
                        if self.left_child is None:
                            query_in_mapping[(query_id, ref_level)].append((query_id, prev_ref_level))

                    if self.left_child is not None:
                        # treat left child differently...they are special kids ;)
                        tmp = self.left_child.generate_query_in_mapping(ref_level, query_2_final_plan, query_in_mapping,
                                                                     query_input = query_input, is_left = True)
                        if tmp != ():
                            query_in_mapping[(query_id, ref_level)].append(tmp)

                        tmp = self.right_child.generate_query_in_mapping(ref_level, query_2_final_plan, query_in_mapping,
                                                                      query_input = query_input)
                        if tmp != ():
                            query_in_mapping[(query_id, ref_level)].append(tmp)

                    print "Mapping for", query_id, ref_level, "is", query_in_mapping[(query_id, ref_level)], query_input
                    # Update these variables for next iteration
                    prev_ref_level = ref_level
                    last_level = ref_level


        self.query_in_mapping = query_in_mapping

        if last_level > 0:
            return tuple([query_id, last_level])
        else:
            return ()

    def get_query_2_refinement_levels(self, fp, query_2_final_plan, query_2_refinement_levels = {}):
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
        #print query_2_refinement_levels
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
                #print "Adding refined query for", queryId, ref_level
                original_query = self.all_queries[queryId]
                new_qid = original_query.qid*10000+q_ctr
                q_ctr += 1
                concise_query = original_query.get_concise_query()
                refined_query = PacketStream(new_qid)
                refined_query.basic_headers = concise_query.basic_headers
                #print self.query_in_mapping
                if (queryId, ref_level) in self.query_in_mapping:
                    for (orig_qid_src, mask) in self.query_in_mapping[(queryId, ref_level)]:
                        refined_qid_src = self.orig_2_refined[(orig_qid_src, mask)]
                        refined_query.filter(append_type=1, src = refined_qid_src, keys=(red_key,), mask=(mask,))

                refined_query.map(keys=(red_key,), func=("mask", ref_level))
                if original_query.left_child is not None:
                    concise_left = original_query.left_child.get_concise_query()
                    # TODO: get rid of this redundancy
                    for operator in concise_left.operators:
                        if operator.name == 'Filter':
                            refined_query.filter(keys=operator.keys, values=operator.values, comp=operator.comp)
                        elif operator.name == "Map":
                            refined_query.map(keys=operator.keys, values=operator.values)
                        elif operator.name == "Reduce":
                            refined_query.reduce(keys=operator.keys, values=operator.values, func=operator.func)
                        elif operator.name == "Distinct":
                            refined_query.distinct()

                for operator in concise_query.operators:
                    if operator.name == 'Filter':
                        refined_query.filter(keys=operator.keys, values=operator.values, comp=operator.comp)
                    elif operator.name == "Map":
                        refined_query.map(keys=operator.keys, values=operator.values)
                    elif operator.name == "Reduce":
                        refined_query.reduce(keys=operator.keys, values=operator.values, func=operator.func)
                    elif operator.name == "Distinct":
                        refined_query.distinct()

                refined_query.isInput = False
                #print "Added refined query for", queryId, ref_level
                refined_queries[queryId][ref_level] = refined_query
                refined_query_2_original[refined_query.qid] = (queryId, ref_level)

        self.refined_queries = refined_queries
        self.refined_query_2_original = refined_query_2_original
        return refined_queries

    def generate_partitioned_queries(self):
        for (queryId, ref_level) in self.query_in_mapping.keys():
            plan = self.query_2_refinement_levels[queryId][ref_level]
            refined_query = self.refined_queries[queryId][ref_level]
            p4_basic_headers = filter(lambda x: x != "payload", refined_query.basic_headers)
            p4_query = p4.QueryPipeline(refined_query.qid).map_init(keys=p4_basic_headers)
            p4_query.parse_payload = False

            spark_query = (spark.PacketStream(refined_query.qid))

            print queryId, ref_level, plan
            # For now we will hardcode to push first reduce operator in the data plane
            print "Original Refined Query before partitioning:", refined_query
            in_dataplane = 0
            border_reduce = None
            max_dp_operators = 2
            init_spark = True
            for operator in refined_query.operators:
                if "payload" in operator.keys or "payload" in operator.values:
                    in_dataplane = max_dp_operators
                    p4_query.parse_payload = True

                if in_dataplane < max_dp_operators:
                    #print "Intermediate Operators:", refined_query.qid, operator.name
                    if operator.name == 'Reduce':
                        in_dataplane += 1
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        if "payload" not in operator.keys:
                            p4_query = p4_query.reduce(keys=operator.keys)
                            if in_dataplane == max_dp_operators:
                                border_reduce = p4_query.operators[-1]

                            # duplicate implementation of reduce operators at the border
                            if in_dataplane == max_dp_operators:
                                border_reduce = p4_query.operators[-1]

                                if init_spark == True:
                                    hdrs = list(p4_query.operators[-1].out_headers)
                                    if p4_query.parse_payload: hdrs += ['payload']
                                    spark_query = (spark_query.filter(keys= ['k']+hdrs,
                                                                      prev_fields=['k']+hdrs,
                                                                      expr="qid=='" + str(refined_query.qid) + "'")
                                                   .map(prev_fields=("p",), keys=("p[2:]",)))
                                    init_spark = False


                        spark_query = spark_query.reduce(prev_fields=prev_fields,
                                                             func=operator.func,
                                                             values=operator.values)
                    elif operator.name == 'Map':
                        print "Adding map operation", operator
                        p4_query = p4_query.map(keys=operator.keys,
                                                values=operator.values,
                                                func=operator.func
                                                )

                    elif operator.name == 'Filter':
                        # check if previous operator was reduce
                        if len(p4_query.operators) > 0:
                            prev_operator = p4_query.operators[-1]
                            if prev_operator.name == "Reduce":
                                # update the threshold for the previous Reduce operator
                                prev_operator.thresh = operator.values[0]
                        else:
                            p4_query = p4_query.filter(keys=operator.keys,
                                                       values=operator.values,
                                                       mask=operator.mask,
                                                       comp=operator.comp,
                                                       src = operator.src)
                    elif operator.name == 'Distinct':
                        p4_query = p4_query.distinct(keys=operator.prev_fields)
                        in_dataplane += 1
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        # duplicate implementation of reduce operators at the border
                        print "Test in_dataplane val for distinct", in_dataplane
                        if in_dataplane == max_dp_operators:

                            if init_spark == True:
                                hdrs = list(p4_query.operators[-1].out_headers)
                                if p4_query.parse_payload: hdrs += ['payload']

                                spark_query = (spark_query.filter(keys= ['k']+hdrs,
                                                                  prev_fields=['k']+hdrs,
                                                                  expr="qid=='" + str(refined_query.qid) + "'")
                                               .map(prev_fields=("p",), keys=("p[2:]",)))
                                init_spark = False


                        spark_query = spark_query.distinct(prev_fields=prev_fields)

                else:
                    if init_spark == True:
                        hdrs = list(p4_query.operators[-1].out_headers)
                        if p4_query.parse_payload: hdrs += ['payload']
                        spark_query = (spark_query.filter(keys= ['k']+hdrs,
                                                          prev_fields=['k']+hdrs,
                                                          expr="qid=='" + str(refined_query.qid) + "'")
                                       .map(prev_fields=("p",), keys=("p[2:]",)))
                        init_spark = False


                    if operator.name == "Map":
                        if len(spark_query.operators) == 2:
                            # This is the first operation for this Spark query
                            prev_fields = refined_query.basic_headers
                            keys = get_original_wo_mask(operator.keys)
                            spark_query = spark_query.map(prev_fields=prev_fields,
                                                      keys=keys, values=operator.values)
                        elif len(spark_query.operators) > 2:
                            prev_fields = get_original_wo_mask(operator.prev_fields)
                            prev_keys = spark_query.operators[-1].keys
                            prev_values = spark_query.operators[-1].values
                            keys = get_original_wo_mask(operator.keys)
                            print "In loop >2", keys, operator.values, prev_keys, prev_values
                            spark_query = spark_query.map(prev_fields=prev_fields,
                                                          prev_keys = prev_keys,
                                                          prev_values = prev_values,
                                                          keys=keys, values=operator.values)



                    if operator.name == "Reduce":
                        if len(spark_query.operators) == 2:
                            # This is the first operation for this Spark query
                            prev_fields = refined_query.basic_headers
                        else:
                            prev_fields = get_original_wo_mask(operator.prev_fields)

                        spark_query = spark_query.reduce(prev_fields=prev_fields,
                                                         func=operator.func,
                                                         values=operator.values)

                    if operator.name == "Distinct":
                        if len(spark_query.operators) == 2:
                            # This is the first operation for this Spark query
                            prev_fields = refined_query.basic_headers
                        else:
                            prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.distinct(prev_fields=prev_fields)

                    if operator.name == "Filter":
                        if border_reduce is not None:
                            border_reduce.thresh = operator.values[0]
                            print "Updated threshold", border_reduce.thresh, " for", border_reduce.name

                        if len(spark_query.operators) == 2:
                            # This is the first operation for this Spark query
                            prev_fields = refined_query.basic_headers
                        else:
                            prev_fields = get_original_wo_mask(operator.prev_fields)
                        tmp = ''
                        # TODO: make this more generic.....puke puke
                        for fld in prev_fields:
                            if fld not in operator.keys:
                                if operator.comp == 'eq':
                                    tmp += '('+str(fld)+'=='+str(operator.values[0])+')'
                                elif operator.comp == 'geq':
                                    tmp += '('+str(fld)+'>='+str(operator.values[0])+')'
                                elif operator.comp == 'leq':
                                    tmp += '('+str(fld)+'<='+str(operator.values[0])+')'

                        expr = tmp

                        spark_query = spark_query.filter(keys=operator.keys, prev_fields=prev_fields,
                                                         expr=expr)

            print "After Partitioning, P4:", p4_query.expr
            print "After Partitioning, Spark:", spark_query.expr
            self.qid_2_dp_queries[refined_query.qid] = p4_query
            self.qid_2_sp_queries[refined_query.qid] = spark_query
            refined_query.dp_query = p4_query
            refined_query.sp_query = spark_query
        return 0


if __name__ == "__main__":
    # Basic test setup for IR and QP implementations
    q0 = PacketStream(0)
    q1 = PacketStream(1).map(keys=("dIP",), func=("mask", 16)).distinct()
    q2 = (PacketStream(2).map(keys=('dIP',), values=tuple([x for x in q0.basic_headers])).distinct())
    q3 = q2.join(new_qid=3, query=q1).map(keys=("dIP",), func=("mask", 16)).distinct()

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
    #q3.generate_partitioned_queries()
    print q3.refined_queries
    #print q3.refined_queries
    #print q3.query_2_plans