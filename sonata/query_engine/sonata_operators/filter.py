#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query import Query


class Filter(Query):
    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)
        self.name = 'Filter'
        map_dict = dict(*args, **kwargs)
        self.keys = []
        self.filter_keys = []
        self.filter_vals = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.func = []
        self.src = 0

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

        if 'src' in map_dict:
            self.src = map_dict['src']

        if 'filter_keys' in map_dict:
            self.filter_keys = map_dict['filter_keys']

        if 'filter_vals' in map_dict:
            self.filter_vals = map_dict['filter_vals']

    def __repr__(self):
        return '.Filter(prev_keys='+str(self.prev_keys)+', filter_keys=' + str(self.filter_keys) +', filter_vals=' + str(self.filter_vals) + \
               ', func=' + str(self.func) + ' src = ' + str(self.src) + ')'
