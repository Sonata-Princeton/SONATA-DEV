#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import json, time
import copy
from multiprocessing.connection import Client
import p4_queries as p4
import spark_queries as spark

class Query(object):
    """
    Abstract Query Class
    """
    basic_headers = ["ts", "te","sIP", "sPort","dIP", "dPort", "nBytes",
                          "proto", "sMac", "dMac"]
                          
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

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
            """
            if (set(self.keys).issubset(set(self.prev_fields))) == False:
                print self.keys, self.prev_fields
                print "Not OK"
                raise NotImplementedError
            """

        if 'values' in map_dict:
            self.values = map_dict['values']
        #print(self.keys, self.values)
        self.fields = self.keys + self.values


class Reduce(Query):
    def __init__(self, *args, **kwargs):
        super(Reduce, self).__init__(*args, **kwargs)
        self.name = 'Reduce'
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.values = map_dict['values']
        self.func = map_dict['func']
        self.fields = self.prev_fields[:-1] + self.values
        #self.fields = tuple(set(self.fields).difference(set("1")))


class Distinct(Query):
    def __init__(self, *args, **kwargs):
        super(Distinct, self).__init__(*args, **kwargs)
        self.name = 'Distinct'
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.fields = self.prev_fields


class Filter(Query):
    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)
        self.name = 'Filter'
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.fields = self.prev_fields
        self.expr = map_dict['expr']


class PacketStream(Query):
    def __init__(self, training_data_fname = '', isInput = True, *args, **kwargs):
        super(PacketStream, self).__init__(*args, **kwargs)
        self.name = 'PacketStream'

        self.fields = tuple(self.basic_headers)
        self.keys = tuple([self.basic_headers[0]])
        self.values = tuple(self.basic_headers[1:])
        self.fields = self.keys + self.values
        self.training_data_fname = training_data_fname
        self.operators = []
        # Is this the original input query from the operator
        self.isInput = isInput
        self.refined_queries = []
        self.partition_plans = []
        self.partition_plan_final = None
        self.dp_query = None
        self.sp_query = None
        self.dp_compile_mode = 'init'
        self.sp_compile_mode = 'init'

        # Object representing the output of the query
        self.output = None

    def get_refinement_plan(self):
        def generate_new_operator(operator, refinement_level, reduction_key):
            new_operator = copy.deepcopy(operator)
            new_keys = []
            for key in operator.keys:
                if key == reduction_key:
                    new_keys.append(key+'/'+str(refinement_level))
                else:
                    new_keys.append(key)
            new_fields = []
            for fld in operator.fields:
                if fld == reduction_key:
                    new_fields.append(fld+'/'+str(refinement_level))
                else:
                    new_fields.append(fld)

            new_prev_fields = []
            for fld in operator.prev_fields:
                if fld == reduction_key:
                    new_prev_fields.append(fld+'/'+str(refinement_level))
                else:
                    new_prev_fields.append(fld)

            new_operator.keys = new_keys
            new_operator.fields = new_fields
            new_operator.prev_fields = new_prev_fields
            return new_operator

        if self.isInput == True:
            # TODO: automate generation of the refinement levels and reduction keys
            refinement_levels = [16, 32]
            reduction_key = 'dIP'

            for refinement_level in refinement_levels:
                refined_query = PacketStream(isInput = False)
                map_keys = []
                for key in self.basic_headers:
                    if key == reduction_key:
                        map_keys.append(key+'/'+str(refinement_level))
                    else:
                        map_keys.append(key)

                refined_query.map(keys = tuple(map_keys))

                for operator in self.operators:
                    new_operator = generate_new_operator(operator,
                                    refinement_level, reduction_key)
                    refined_query.operators.append(new_operator)

                expr_sp = ''
                for operator in refined_query.operators:
                    expr_sp += '.'+operator.compile_sp()
                #print refinement_level, expr_sp[1:]
                self.refined_queries.append(refined_query)
        else:
            raise NotImplementedError

    def get_partitioning_plan(self, part):
        if self.isInput != True:
            dp_query = PacketStream(isInput = False)
            sp_query = PacketStream(isInput = False)
            partition_plan = {0:dp_query, 1:sp_query}
            for operator in self.operators[:part]:
                new_operator = copy.deepcopy(operator)
                dp_query.operators.append(new_operator)

            for operator in self.operators[part:]:
                new_operator = copy.deepcopy(operator)
                sp_query.operators.append(new_operator)
            self.partition_plans.append(partition_plan)
        else:
            raise NotImplementedError

    def get_query_cost(self):
        if self.isInput != True:
            return 0
        else:
            raise NotImplementedError

    def generate_dp_query(self):
        if self.isInput != True:
            if self.partition_plan_final != None:
                dp_query = self.partition_plan_final[0]
                p4_query = p4.PacketStream(1)
                for operator in dp_query.operators:
                    if operator.name == 'Reduce':
                        p4_query = p4_query.reduce(keys = operator.prev_fields)
                    elif operator.name == 'Distinct':
                        p4_query = p4_query.distinct(keys = operator.prev_fields)
                self.dp_query = p4_query
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    def generate_sp_query(self):
        if self.isInput != True:
            if self.partition_plan_final != None:
                sp_query = self.partition_plan_final[1]
                spark_query = spark.PacketStream()
                for operator in sp_query.operators:
                    new_operator = copy.deepcopy(operator)
                    spark_query.operators.append(new_operator)
                self.sp_query = spark_query
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    def compile_dp_query(self):
        # compile the data plane query
        if self.dp_query != None:
            if self.dp_compile_mode == 'init':
                self.dp_query.compile_pipeline()
            else:
                self.dp_query.compile_delta()
        else:
            raise NotImplementedError

    def compile_sp_query(self):
        # compile the stream processor query
        if self.sp_query != None:
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

    def map(self, *args, **kwargs):
        operator = Map(prev_fields = self.get_prev_fields(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def reduce(self, *args, **kwargs):
        operator = Reduce(prev_fields = self.get_prev_fields(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        operator = Distinct(prev_fields = self.get_prev_fields(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, *args, **kwargs):
        operator = Filter(prev_fields = self.get_prev_fields(),*args, **kwargs)
        self.operators.append(operator)
        return self

query = (PacketStream()
        .filter(expr = "proto == '17'")
        .map(keys = ("dIP", "sIP"))
        .distinct()
        .map(keys =("dIP",), values = ("1",))
        .reduce(func='sum', values=('count',))
        .filter(expr='count > 20')
        .map(keys=('dIP',))
        )

query.get_refinement_plan()
for refined_query in query.refined_queries:
    refined_query.get_partitioning_plan(4)
    refined_query.partition_plan_final = refined_query.partition_plans[0]
    refined_query.generate_dp_query()
    refined_query.generate_sp_query()
    refined_query.dp_query.compile_pipeline()
    print refined_query.dp_query.p4_control
    print refined_query.sp_query.compile()
