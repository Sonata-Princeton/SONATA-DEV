#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import json, time
from multiprocessing.connection import Client

class SparkQuery(object):
    """
    Abstract SparkQuery Class
    """
    def __init__(self):
        self.fields = []
        self.keys = []
        self.values = []
        self.expr = ''

    def eval(self):
        """
        evaluate this policy
        :param ?
        :type pkt: ?
        :rtype: ?
        """
        return self.expr

    def compile(self):
        """
        compile this policy for stream processor
        """
        return 0

class Map(SparkQuery):
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.keys = ()
        self.prev_keys = ()
        self.prev_values = ()
        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']
        self.values = ()
        if 'keys' in map_dict:
            self.keys = map_dict['keys']

        if 'values' in map_dict:
            self.values = map_dict['values']
        #print(self.keys, self.values)
        #self.fields = self.keys + self.values

    def compile(self):
        print self.keys, self.values, self.prev_keys, self.prev_values
        if len(self.values) != 0:
            if len(self.prev_keys) > 0 and len(self.prev_values) > 0:
                expr = ('map(lambda (('+','.join(str(x) for x in self.prev_keys)+
                        '), ('+','.join(str(x) for x in self.prev_values)+')): (('+','.join(str(x) for x in self.keys)+
                        '),('+','.join(str(x) for x in self.values)+')))')

            else:
                expr = ('map(lambda ('+','.join(str(x) for x in self.prev_fields)+
                        '): (('+','.join(str(x) for x in self.keys)+
                        '),('+','.join(str(x) for x in self.values)+')))')
        else:
            if len(self.prev_keys) > 0 and len(self.prev_values) > 0:
                expr = ('map(lambda (('+','.join(str(x) for x in self.prev_keys)+
                        '), ('+','.join(str(x) for x in self.prev_values)+')): (('+','.join(str(x) for x in self.keys)+')))')

            else:
                expr = ('map(lambda ('+','.join(str(x) for x in self.prev_fields)+
                        '): (('+','.join(str(x) for x in self.keys)+')))')
        print "Map Query", expr
        return expr

class Reduce(SparkQuery):
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.values = map_dict['values']
        self.func = map_dict['func']
        #self.fields = self.prev_fields[:-1] + self.values
        #self.fields = tuple(set(self.fields).difference(set("1")))

    def compile(self):
        expr = ''
        if self.func == 'sum':
            expr += 'reduceByKey(lambda x,y: x+y)'
        return expr

class Distinct(SparkQuery):
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.keys = self.prev_fields
        self.fields = self.prev_fields

    def compile(self):
        expr = 'distinct()'
        return expr

class Filter(SparkQuery):
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.prev_fields = map_dict['prev_fields']
        self.keys = map_dict['keys']
        self.values = filter(lambda x: x not in self.keys, self.prev_fields)
        self.expr = map_dict['expr']
        self.fields = self.prev_fields

    def compile(self):
        kys = ",".join(self.keys)
        vals = ",".join(self.values)
        if len(self.values) > 0:
            expr = ('filter(lambda (('+str(kys)+'), ('+str(vals)+')): '+self.expr+')')
        else:
            expr = ('filter(lambda ('+str(kys)+'): '+self.expr+')')

        return expr

class PacketStream(SparkQuery):
    def __init__(self, id):
        self.basic_headers = ["qid", "ts", "te","sIP", "sPort","dIP", "dPort", "nBytes",
                              "proto", "sMac", "dMac"]
        self.fields = tuple(self.basic_headers)
        self.keys = tuple([self.basic_headers[0]])
        self.values = tuple(self.basic_headers[1:])
        self.fields = self.keys + self.values
        self.operators = []
        self.expr = 'In'
        self.qid = id

    def compile(self):
        expr_sp = ''
        for operator in self.operators:
            #print type(operator), operator.compile()
            expr_sp += '.'+operator.compile()

        return expr_sp[1:]

    def get_prev_fields(self):
        if len(self.operators) > 0:
            prev_fields = self.operators[-1].fields
        else:
            prev_fields = self.fields
        return prev_fields

    def map(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        prev_fields = map_dict['prev_fields']
        keys = map_dict['keys']
        values = tuple([])
        if 'values' in map_dict:
            values = map_dict['values']

        self.expr += '\n\t.Map('+','.join([x for x in keys])+')'
        operator = Map(*args, **kwargs)
        self.operators.append(operator)
        return self

    def reduce(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        prev_fields = map_dict['prev_fields']
        func = map_dict['func']
        values = map_dict['values']
        self.expr += '\n\t.Reduce('+func+',values='+','.join([x for x in values])+',prev_fields='+','.join([x for x in prev_fields])+')'
        operator = Reduce(prev_fields = prev_fields,
                          func = func,
                          values = values)
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        self.expr += '\n\t.Distinct()'
        map_dict = dict(*args, **kwargs)
        prev_fields = map_dict['prev_fields']
        operator = Distinct(prev_fields = prev_fields)
        self.operators.append(operator)
        return self

    def filter(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        prev_fields = map_dict['prev_fields']
        keys = map_dict['keys']
        values = filter(lambda x: x not in keys, prev_fields)
        expr = map_dict['expr']
        self.expr += '\n\t.Filter(prev_fields=('+','.join([x for x in prev_fields])+'), expr=('+expr+'),keys=('+','.join([x for x in keys])+'))'
        operator = Filter(*args, **kwargs)
        self.operators.append(operator)
        return self
