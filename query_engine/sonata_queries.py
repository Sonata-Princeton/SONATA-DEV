#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import json, time
import copy
from multiprocessing.connection import Client
import p4_queries as p4
import spark_queries as spark
import logging

logging.getLogger("sonata_queries")

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
    basic_headers = ["sIP", "sPort","dIP", "dPort", "nBytes",
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
        if 'values' in map_dict:
            self.values = map_dict['values']
        #print(self.keys, self.values)
        self.fields = tuple(list(self.keys) + list(self.values))


class Reduce(Query):
    def __init__(self, *args, **kwargs):
        super(Reduce, self).__init__(*args, **kwargs)
        self.name = 'Reduce'
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.values = map_dict['values']
        self.func = map_dict['func']
        self.fields = tuple(list(self.prev_fields[:-1]) + list(self.values))
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
        self.keys = map_dict['keys']
        if 'values' in map_dict:
            self.vals = map_dict['values']
        else:
            self.vals = ()
        if 'comp' in map_dict:
            self.comp = map_dict['comp']
        else:
            self.comp = 'eq'


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
        self.expr = ''
        self.refinement_filter_id = 0


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
        logging.info("Inside get_refinement_plan %%%%%%%%%%%"+ str(self.isInput))
        if self.isInput == True:
            # TODO: automate generation of the refinement levels and reduction keys
            refinement_levels = [16, 32]
            reduction_key = 'dIP'
            prev_level = 0

            for refinement_level in refinement_levels:
                refined_query = copy.deepcopy(self)
                refined_query.isInput = False
                map_keys = []
                for key in self.basic_headers:
                    if key == reduction_key:
                        map_keys.append(key+'/'+str(refinement_level))

                    else:
                        map_keys.append(key)

                refined_query.map(append_type=1, keys = tuple(map_keys))
                if prev_level > 0:
                    refined_query.refinement_filter_id = 0
                    refined_query.filter(append_type = 1, keys = tuple(prev_map_key))

                logging.info("Refined Query for level "+str(refinement_level))
                logging.info(refined_query.expr)
                self.refined_queries.append(refined_query)
                prev_level = refinement_level
                for key in self.basic_headers:
                    if key == reduction_key:
                        prev_map_key = (key+'/'+str(refinement_level),)

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

            for operator in self.operators[part-1:]:
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

    def generate_dp_query(self, qid):
        if self.isInput != True:
            if self.partition_plan_final != None:
                dp_query = self.partition_plan_final[0]
                dp_query.refinement_filter_id = self.refinement_filter_id
                p4_query = p4.QueryPipeline(qid)
                for operator in dp_query.operators:
                    if operator.name == 'Reduce':
                        p4_query = p4_query.reduce(keys = operator.prev_fields)
                    elif operator.name == 'Map':
                        p4_query = p4_query.map(keys = operator.keys,
                                                prev_fields = operator.prev_fields,
                                                values = operator.values
                                                )
                    elif operator.name == 'Filter':
                        p4_query = p4_query.filter(keys = operator.keys,
                                                   values = operator.vals,
                                                   comp = operator.comp)
                    elif operator.name == 'Distinct':
                        p4_query = p4_query.distinct(keys = operator.prev_fields)
                self.dp_query = p4_query
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    def generate_sp_query(self, qid):
        if self.isInput != True:
            if self.partition_plan_final != None:
                sp_query = self.partition_plan_final[1]
                spark_query = spark.PacketStream(qid).filter(prev_fields = ("p"), expr = "p[1] == '" + str(qid) + "'").map(prev_fields = ("p",), keys=("p[2:]",))
                for operator in sp_query.operators:
                    if(operator.name == "Map"):
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        keys = get_original_wo_mask(operator.keys)
                        spark_query = spark_query.map(prev_fields = prev_fields,
                                                      keys = keys, values = operator.values)

                    if(operator.name == "Reduce"):
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.reduce(prev_fields = prev_fields,
                                                      func = operator.func,
                                                      values = operator.values)

                    if(operator.name == "Distinct"):
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.distinct(prev_fields = prev_fields)


                    if(operator.name == "Filter"):
                        prev_fields = get_original_wo_mask(operator.prev_fields)
                        spark_query = spark_query.filter(prev_fields = prev_fields,
                                                         expr = operator.expr)

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

    def map(self, append_type = 0, *args, **kwargs):
        if append_type == 0:
            operator = Map(prev_fields = self.get_prev_fields(), *args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Map(prev_fields = self.basic_headers, *args, **kwargs)
            self.operators = [operator]+self.operators
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        values = tuple([])
        if 'values' in map_dict:
            values = map_dict['values']
        if append_type == 0:
            self.expr += '.Map('+','.join([x for x in keys])+')'
        else:
            self.expr = '.Map('+','.join([x for x in keys])+')'+self.expr

        return self

    def reduce(self, *args, **kwargs):
        operator = Reduce(prev_fields = self.get_prev_fields(), *args, **kwargs)
        map_dict = dict(*args, **kwargs)
        values = map_dict['values']
        func = map_dict['func']
        self.expr += '.Reduce('+func+','+','.join([x for x in values])+')'
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        self.expr += '.Distinct()'
        operator = Distinct(prev_fields = self.get_prev_fields(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, append_type = 0, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        if 'values' in map_dict:
            vals = map_dict['values']
        else:
            vals = ()
        if 'comp' in map_dict:
            comp = map_dict['comp']
        else:
            comp = 'eq'
        if append_type == 0:
            operator = Filter(prev_fields = self.get_prev_fields(),*args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Filter(prev_fields = self.basic_headers, *args, **kwargs)
            self.operators = [operator] + self.operators


        if append_type == 0:
            self.expr += '.Filter(keys='+str(keys)+', vals = '+str(vals)+', comp='+str(comp)+')'
        else:
            self.expr = '.Filter(keys='+str(keys)+', vals = '+str(vals)+', comp='+str(comp)+')'+self.expr
        return self

"""
query = (PacketStream()
        .filter(expr = "proto == '17'")
        .map(keys = ("dIP", "sIP"))
        .distinct()
        .map(keys =("dIP",), values = ("1",))
        .reduce(func='sum', values=('count',))
        .filter(expr='count > 20')
        .map(keys=('dIP',))
        )
"""
