#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import copy
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
        self.func = ()

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        if 'values' in map_dict:
            self.values = map_dict['values']
        if "func" in map_dict:
            self.func = map_dict['func']

        #print(self.keys, self.values)
        self.fields = tuple(list(self.keys) + list(self.values))

    def __repr__(self):
        return '.Map(keys='+str(self.keys)+', values='+str(self.values)+', func='+str(self.func)+')'



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

    def __repr__(self):
        return '.Reduce(func='+self.func+', values='+','.join([x for x in self.values])+')'


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
        return '.Join(query='+self.query.__repr__()+')'


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

    def __repr__(self):
        return '.Filter(keys='+str(self.keys)+', values = '+str(self.values)+', comp='+str(self.comp)+' mask ='+str(self.mask)+')'


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

    def __repr__(self):
        out = 'In'
        for operator in self.operators:
            out += operator.__repr__()
        return out

    def get_refinement_plan(self):
        print("Inside get_refinement_plan %%%%%%%%%%%"+ str(self.isInput))
        if self.isInput == True:
            # TODO: automate generation of the refinement levels and reduction keys
            concise_query = self.get_concise_query()
            #return 0
            refinement_levels = [16, 32]
            reduction_key = 'dIP'
            prev_level = 0

            for refinement_level in refinement_levels:
                refined_query = PacketStream()
                refined_query.map(append_type=1, keys = (reduction_key,), func = ("mask",refinement_level))
                if prev_level > 0:
                    refined_query.refinement_filter_id = 0
                    refined_query.filter(append_type = 1,
                                         keys = (prev_map_key,),
                                         mask = (prev_mask,))

                for operator in concise_query.operators:
                    #print operator
                    if operator.name == 'Filter':
                        refined_query.filter(keys = operator.keys,
                                             values = operator.values,
                                             comp = operator.comp)
                    elif operator.name == "Map":
                        refined_query.map(keys = operator.keys, values = operator.values)
                    elif operator.name == "Reduce":
                        refined_query.reduce(values = operator.values,
                                             func = operator.func)

                    elif operator.name == "Distinct":
                        refined_query.distinct()

                    elif operator.name == "Join":
                        operator.query.get_refinement_plan()
                        refined_query.join(query=operator.query.refined_queries[-1])

                refined_query.isInput = False

                #print "Refined Query for level "+str(refinement_level)
                #print refined_query

                self.refined_queries.append(refined_query)
                prev_level = refinement_level
                for key in concise_query.basic_headers:
                    if key == reduction_key:
                        prev_map_key = key
                        prev_mask = refinement_level

        else:
            raise NotImplementedError

    def get_concise_query(self):
        unique_keys = {}
        for operator in self.operators:
            for k in operator.keys:
                unique_keys[k] = 0

        concise_query = PacketStream()
        concise_query.basic_headers = unique_keys.keys()
        print "Basic headers for concise query", concise_query.basic_headers
        for operator in self.operators:
            #print operator
            if operator.name == 'Filter':
                concise_query.filter(keys = operator.keys,
                                     values = operator.values,
                                     comp = operator.comp)
            elif operator.name == "Map":
                #print "Concise query:: Map.keys", operator.keys
                concise_query.map(keys = operator.keys, values = operator.values)
            elif operator.name == "Reduce":
                concise_query.reduce(values = operator.values,
                                     func = operator.func)

            elif operator.name == "Distinct":
                concise_query.distinct()

            elif operator.name == "Join":
                concise_query.join(query=operator.query.get_concise_query())

        return concise_query


    def get_partitioning_plan(self, part):
        if self.isInput != True:
            dp_query = PacketStream(isInput = False)
            sp_query = PacketStream(isInput = False)
            dp_query.basic_headers = self.basic_headers
            sp_query.basic_headers = self.basic_headers
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
                p4_query = p4.QueryPipeline(qid).map_init(keys=dp_query.basic_headers)
                for operator in dp_query.operators:
                    if operator.name == 'Reduce':
                        p4_query = p4_query.reduce(keys = operator.prev_fields)
                    elif operator.name == 'Map':

                        p4_query = p4_query.map(keys = operator.keys,
                                                values = operator.values,
                                                func = operator.func
                                                )

                    elif operator.name == 'Filter':
                        p4_query = p4_query.filter(keys = operator.keys,
                                                   values = operator.values,
                                                   mask = operator.mask,
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
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        self.keys = keys
        if 'values' in map_dict:
            values = map_dict['values']
            self.values = values

        if append_type == 0:
            operator = Map(prev_fields = self.get_prev_fields(), *args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Map(prev_fields = self.basic_headers, *args, **kwargs)
            self.operators = [operator]+self.operators

        return self

    def reduce(self, *args, **kwargs):
        operator = Reduce(prev_fields = self.get_prev_fields(), *args, **kwargs)
        map_dict = dict(*args, **kwargs)
        values = map_dict['values']
        self.values = values
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        operator = Distinct(prev_fields = self.get_prev_fields(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, append_type = 0, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        self.keys = keys

        if append_type == 0:
            operator = Filter(prev_fields = self.get_prev_fields(),*args, **kwargs)
            self.operators.append(operator)
        else:
            operator = Filter(prev_fields = self.basic_headers, *args, **kwargs)
            self.operators = [operator] + self.operators

        return self

    def join(self, *args, **kwargs):
        operator = Join(*args, **kwargs)
        self.operators.append(operator)
        return self


if __name__ == "__main__":
    q1 = PacketStream(1).map(keys = ("dIP",), func = ("mask", 16))
    print q1