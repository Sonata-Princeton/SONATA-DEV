#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from netaddr import *

from sonata.system_config import TARGET_SP, BASIC_HEADERS

if TARGET_SP == 'SPARK':
    from spark_queries import *


class PacketStream(StreamingQuery):
    basic_headers = ["qid"]+BASIC_HEADERS

    def __init__(self, id):
        self.fields = tuple(self.basic_headers)
        self.keys = tuple([self.basic_headers[0]])
        self.values = tuple(self.basic_headers[1:])
        self.fields = self.keys + self.values
        self.operators = []
        self.expr = 'In'
        self.qid = id

    def __repr__(self):
        out = 'In\n'
        for operator in self.operators:
            out += ''+operator.__repr__()+'\n'
        return out

    def compile(self):
        expr_sp = ''
        for operator in self.operators:
            expr_sp += ''+operator.compile()

        return expr_sp[1:]

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

    def map(self, *args, **kwargs):
        operator = Map(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def reduce(self, *args, **kwargs):
        operator = Reduce(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        operator = Distinct(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, *args, **kwargs):
        operator = Filter(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(), *args, **kwargs)
        self.operators.append(operator)
        return self

    def filter_init(self,*args, **kwargs):
        operator = FilterInit(*args, **kwargs)
        self.operators.append(operator)
        return self

    def join(self, *args, **kwargs):
        operator = Join(prev_keys=self.get_prev_keys(), prev_values=self.get_prev_values(), *args, **kwargs)
        self.operators.append(operator)
        return self