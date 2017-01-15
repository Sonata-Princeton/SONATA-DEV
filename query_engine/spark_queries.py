#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import json, time
from multiprocessing.connection import Client
from netaddr import *

class SparkQuery(object):
    """
    Abstract SparkQuery Class
    """
    def __init__(self):
        self.fields = []
        self.keys = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
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
    name = "Map"
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.map_keys = []
        self.map_values = []
        self.expr = ''
        self.func = []
        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        else:
            self.keys = self.prev_keys

        if 'values' in map_dict:
            self.values = list(map_dict['values'])
        else:
            self.values = []

        if 'map_keys' in map_dict:
            self.map_keys = map_dict['map_keys']

        if 'map_values' in map_dict:
            self.map_values = map_dict['map_values']
            for elem in self.map_values:
                if elem not in self.values:
                    self.values.append(elem)

        if 'func' in map_dict:
            self.func = map_dict['func']

    def __repr__(self):
        #print "Map Keys: ",self.prev_keys, self.prev_values, self.keys, self.values
        #print self.map_keys, self.map_values
        expr = '.map(lambda (('
        # There is mapping required either for key or value
        expr += ','.join([str(elem) for elem in self.prev_keys])
        expr += '), ('
        expr += ','.join([str(elem) for elem in self.prev_values])
        expr += ')): (('
        for elem in self.keys:
            if elem not in self.map_keys:
                expr += elem+','
            else:
                if len(self.func) > 0:
                    if self.func[0] == 'mask':
                        expr += 'str(IPNetwork(str(str('+str(elem)+')+\"/'+str(self.func[1])+'\")).network)'+','
                    else:
                        # TODO generalize for more mapping functions
                        pass
        expr = expr[:-1]
        expr += ')'
        if len(self.values) > 0 and len(self.func) > 0:
            expr += ',('
            for elem in self.map_values:
                if self.func[0] == 'eq':
                    expr += str(self.func[1])+','
                else:
                    # TODO generalize for more mapping functions
                    pass
            expr = expr[:-1]
            expr += ')'
        elif len(self.values) > 0 and len(self.func) == 0:
            expr += ',('
            for elem in self.values:
                expr += elem+','
            expr = expr[:-1]
            expr += ')'
        expr += '))'
        return expr

    def compile(self):
        #print "Map Keys: ",str(self.prev_keys), str(self.prev_values),str(self.keys), str(self.values)
        expr = '.map(lambda (('
        expr += ','.join([str(elem) for elem in self.prev_keys])
        expr += ')'
        if len(self.prev_values) > 0:
            expr += ',('
            expr += ','.join([str(elem) for elem in self.prev_values])
            expr += ')'
        expr += '): (('
        for elem in self.keys:
            if elem not in self.map_keys:
                expr += elem+','
            else:
                if len(self.func) > 0:
                    if self.func[0] == 'mask':
                        expr += 'str(IPNetwork(str(str('+str(elem)+')+\"/'+str(self.func[1])+'\")).network)'+','
                    else:
                        # TODO generalize for more mapping functions
                        pass
        expr = expr[:-1]
        expr += ')'
        if len(self.values) > 0 and len(self.func) > 0:
            expr += ',('
            for elem in self.map_values:
                if self.func[0] == 'eq':
                    expr += str(self.func[1])+','
                else:
                    # TODO generalize for more mapping functions
                    pass
            expr = expr[:-1]
            expr += ')'
        elif len(self.values) > 0 and len(self.func) == 0:
            expr += ',('
            for elem in self.values:
                expr += elem+','
            expr = expr[:-1]
            expr += ')'
        expr += '))'

        #print "Map Query", expr

        return expr


class Reduce(SparkQuery):
    name = 'Reduce'
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.func = []
        self.expr = ''

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        else:
            self.keys = self.prev_keys

        if 'values' in map_dict:
            self.values = map_dict['values']
        else:
            self.values = self.prev_values

        if 'func' in map_dict:
            self.func = map_dict['func']

    def __repr__(self):
        out = ''
        if self.func[0] == 'sum':
            out = '.reduceByKey(keys='+str(self.keys)+', values='+str(self.values)+', func='+str(self.func)+')'
        else:
            # TODO generalize this later
            pass
        return out

    def compile(self):
        expr = ''
        #print "Reduce Keys: ",str(self.prev_keys), str(self.prev_values),str(self.keys), str(self.values)
        if self.func[0] == 'sum':
            expr += '.reduceByKey(lambda x,y: x+y)'
        return expr


class Distinct(SparkQuery):
    name = 'Distinct'
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.expr = ''

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        else:
            self.keys = self.prev_keys

        if 'values' in map_dict:
            self.values = map_dict['values']
        else:
            self.values = ()

    def __repr__(self):
        out = '.distinct(keys='+str(self.keys)+')'
        return out

    def compile(self):
        expr = '.distinct()'
        return expr


class FilterInit(SparkQuery):
    name = 'FilterInit'
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.qid = map_dict['qid']
        self.keys = map_dict['keys']
        self.name = "FilterInit"
        self.values = ()

    def __repr__(self):
        return '.filter(lambda p : (p[1]==str('+str(self.qid)+')))'

    def compile(self):
        expr = '.filter(lambda p : (p[1]==str('+str(self.qid)+')))'
        return expr


class Filter(SparkQuery):
    name = 'Filter'
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.filter_keys = []
        self.filter_vals = []
        self.func = []
        self.expr = ''

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        else:
            self.keys = self.prev_keys

        if 'values' in map_dict:
            self.values = map_dict['values']
        else:
            self.values = self.prev_values

        if 'func' in map_dict:
            self.func = map_dict['func']

        if 'filter_keys' in map_dict:
            self.filter_keys = map_dict['filter_keys']

        if 'filter_vals' in map_dict:
            self.filter_vals = map_dict['filter_vals']



    def __repr__(self):
        self.filter_expr = '('
        for fld in self.filter_keys:
            if self.func[0] == 'eq':
                self.filter_expr += str(fld) + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += str(fld) + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += str(fld) + '<=' + str(self.func[1]) + '&&'
        for fld in self.filter_vals:
            if self.func[0] == 'eq':
                self.filter_expr += str(fld) + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += 'float(' + str(fld) + ')' + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += str(fld) + '<=' + str(self.func[1]) + '&&'
        self.filter_expr = self.filter_expr[:-2]
        self.filter_expr += ')'
        out = '.filter(lambda (('+str(self.keys)+'), ('+str(self.values)+')): '+self.filter_expr+')'
        return out

    def compile(self):
        self.filter_expr = '('
        for fld in self.filter_keys:
            if self.func[0] == 'eq':
                self.filter_expr += str(fld) + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += str(fld) + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += str(fld) + '<=' + str(self.func[1]) + '&&'
        for fld in self.filter_vals:
            if self.func[0] == 'eq':
                self.filter_expr += str(fld) + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += 'float(' + str(fld) + ')' + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += str(fld) + '<=' + str(self.func[1]) + '&&'
        self.filter_expr = self.filter_expr[:-2]
        self.filter_expr += ')'
        #print "Filter Keys: " + str(self.values)
        # .filter(keys=('dIP',), func=('geq', '3'))
        expr = '.filter(lambda ('
        expr += '('+','.join([str(elem) for elem in self.keys])+')'
        if len(self.values) > 0:
            expr += ',('+','.join([str(elem) for elem in self.values])+')'
        expr += ')'
        expr += ': ('+self.filter_expr+'))'
        self.expr = expr
        return expr


class Join(object):
    name = 'Join'
    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.join_key = []
        self.join_query = None
        self.expr = ''
        self.in_stream = ''

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']

        self.keys = self.prev_keys
        self.values = self.prev_values

        if 'q' in map_dict:
            self.join_query = map_dict['q']

        if 'join_key' in map_dict:
            self.join_key = map_dict['join_key']

        if 'in_stream' in map_dict:
            self.in_stream = map_dict['in_stream']

    def __repr__(self):
        out = '.map(lambda ('+','.join([str(elem) for elem in self.prev_keys])+'): (('+','.join([str(elem) for elem in self.join_key]) + '),('+','.join([str(elem) for elem in self.prev_keys])+')))'
        out += '.join('+self.join_query.__repr__()+'.map(lambda s: (s,1)))'
        out += '.map(lambda s: s[1][0])'
        return out

    def compile(self):
        #print "Filter Keys: " + str(self.values)
        # .filter(keys=('dIP',), func=('geq', '3'))
        out = '.map(lambda ('+','.join([str(elem) for elem in self.prev_keys])+'): (('+','.join([str(elem) for elem in self.join_key]) + '),('+','.join([str(elem) for elem in self.prev_keys])+')))'
        out += '.join('+self.in_stream+self.join_query.compile()+'.map(lambda s: (s,1)))'
        out += '.map(lambda s: s[1][0])'
        return out

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