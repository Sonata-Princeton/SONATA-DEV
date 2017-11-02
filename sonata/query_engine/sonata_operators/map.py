#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query import Query


class Map(Query):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        self.name = 'Map'
        map_dict = dict(*args, **kwargs)
        self.keys = []
        # This is the set of keys for which we apply map function
        self.map_keys = []
        self.map_values = []
        self.values = []
        self.prev_keys = []
        self.prev_values = []
        self.func = []

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = list(map_dict['prev_values'])
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
            self.map_values = list(map_dict['map_values'])
            # for elem in self.map_values:
            #     if elem not in self.values:
            #         self.values.append(elem)

        if "func" in map_dict:
            self.func = map_dict['func']

    def get_init_keys(self):
        return tuple(list(self.keys) + list(self.values) + list(self.map_keys) + list(self.map_values))

    def __repr__(self):
        return '.Map(keys=' + str(self.keys) + ', map_keys=' + str(self.map_keys) + \
               ', values=' + str(self.values) + ', map_values=' + str(self.map_values) + \
               ', func=' + str(self.func) + ')'
