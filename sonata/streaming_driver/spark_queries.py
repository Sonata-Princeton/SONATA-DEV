#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import json, time
from multiprocessing.connection import Client
from netaddr import *

class StreamingQuery(object):
    """
    Abstract StreamingQuery Class
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


class Map(StreamingQuery):
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
                # expr += elem +','
                if self.func[0] in ['eq', 'set']:
                    expr += str(self.func[1])+','
                elif self.func[0] == 'div':
                    expr += '/'.join([str(elem) for elem in self.prev_values])
                    expr += ','
                elif self.func[0] == 'diff':
                    expr += '-'.join([str(elem) for elem in self.prev_values])
                    expr += ','
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
                        print "WEIRD"
                        # TODO generalize for more mapping functions
                        pass
        expr = expr[:-1]
        expr += ')'
        if len(self.values) > 0 and len(self.func) > 0:
            expr += ',('
            for elem in self.map_values:
                if self.func[0] in ['eq', 'set']:
                    expr += str(self.func[1])+','
                elif self.func[0] == 'div':
                    assert len(self.prev_values) == 2
                    expr += 'float(str('+self.prev_values[0]+'))' + '/' + 'float(str('+self.prev_values[1]+'))'
                    # expr += '/'.join([str(elem) for elem in self.prev_values])
                    expr += ','
                elif self.func[0] == 'diff':
                    assert len(self.prev_values) == 2
                    expr += 'float(str('+self.prev_values[0]+'))' + '-' + 'float(str('+self.prev_values[1]+'))'
                    # expr += '/'.join([str(elem) for elem in self.prev_values])
                    expr += ','
                else:
                    # TODO generalize for more mapping functions
                    pass
            expr = expr[:-1]
            expr += ')'
        elif len(self.values) > 0 and len(self.func) == 0:
            expr += ',('
            for elem in self.values:
                expr += 'float(' + elem + '),'
            expr = expr[:-1]
            expr += ')'
        expr += '))'

        
        #print "Map Query", expr

        return expr


class Reduce(StreamingQuery):
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


class Distinct(StreamingQuery):
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


class FilterInit(StreamingQuery):
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


class Filter(StreamingQuery):
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
                self.filter_expr += 'float(' + str(fld) + ')' + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += str(fld) + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += str(fld) + '<=' + str(self.func[1]) + '&&'
        for fld in self.filter_vals:
            if self.func[0] == 'eq':
                self.filter_expr += 'float(' + str(fld) + ')' + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += 'float(' + str(fld) + ')' + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += 'float(' + str(fld) + ')' + '<=' + str(self.func[1]) + '&&'
        self.filter_expr = self.filter_expr[:-2]
        self.filter_expr += ')'
        out = '.filter(lambda (('+str(self.keys)+'), ('+str(self.values)+')): '+self.filter_expr+')'
        return out

    def compile(self):
        self.filter_expr = '('
        for fld in self.filter_keys:
            if self.func[0] == 'eq':
                self.filter_expr += 'float(' + str(fld) + ')' + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += 'float(' + str(fld) + ')' + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += 'float(' + str(fld) + ')' + '<=' + str(self.func[1]) + '&&'
        for fld in self.filter_vals:
            if self.func[0] == 'eq':
                self.filter_expr += 'float(' + str(fld) + ')' + '==' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'geq':
                self.filter_expr += 'float(' + str(fld) + ')' + '>=' + str(self.func[1]) + ' &&'
            elif self.func[0] == 'leq':
                self.filter_expr += 'float(' + str(fld) + ')' + '<=' + str(self.func[1]) + '&&'
        self.filter_expr = self.filter_expr[:-2]
        self.filter_expr += ')'

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
        out = ''
        if len(self.join_query.compile()) > 0:
            out = '.map(lambda ('+','.join([str(elem) for elem in self.prev_keys])+'): (('+','.join([str(elem) for elem in self.join_key]) + '),('+','.join([str(elem) for elem in self.prev_keys])+')))'
            out += '.join('+self.join_query.__repr__()+'.map(lambda s: (s,1)))'
            out += '.map(lambda s: s[1][0])'
        return out

    def compile(self):
        out = ''
        if len(self.join_query.compile()) > 0:

            out = '.map(lambda ('+','.join([str(elem) for elem in self.prev_keys])+'): (('+','.join([str(elem) for elem in self.join_key]) + '),('+','.join([str(elem) for elem in self.prev_keys])+')))'
            out += '.join('+self.in_stream+self.join_query.compile()+'.map(lambda s: (s,1)))'
            out += '.map(lambda s: s[1][0])'
        return out


class JoinSameWindow(object):
    name = 'Join'

    def __init__(self, *args, **kwargs):
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.values = []

        self.left_qid = ''
        self.right_qid = ''
        self.expr = ''
        self.in_stream = ''

        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        if 'values' in map_dict:
            self.values = map_dict['values']

        if 'left_qid' in map_dict:
            self.left_qid = map_dict['left_qid']
        if 'right_qid' in map_dict:
            self.right_qid = map_dict['right_qid']

        if 'q' in map_dict:
            self.join_query = map_dict['q']

        if 'join_key' in map_dict:
            self.join_key = map_dict['join_key']

        if 'in_stream' in map_dict:
            self.in_stream = map_dict['in_stream']

    def __repr__(self):
        out = " spark_queries['" + str(self.left_qid) + "']"+".join("+"spark_queries['" + str(self.right_qid) + "']"+")"
        return out

    def compile(self):
        out = ''
        # if len(self.join_query.compile()) > 0:
        out = " spark_queries[" + str(self.left_qid) + "]"+".join("+"spark_queries[" + str(self.right_qid) + "]"+")"
        return out
