#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query import Query


class Reduce(Query):
    def __init__(self, *args, **kwargs):
        super(Reduce, self).__init__(*args, **kwargs)
        self.name = 'Reduce'
        map_dict = dict(*args, **kwargs)

        self.prev_keys = ()
        self.prev_values = ()
        self.keys = ()
        self.values = ()
        self.func = ()
        self.threshold = 1

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']
        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        else:
            self.keys = self.prev_keys
        self.values = self.prev_values
        if 'func' in map_dict:
            self.func = map_dict['func']

    def get_init_keys(self):
        return tuple(list(self.keys) + list(self.values))

    def __repr__(self):
        return '.Reduce( keys=(' + ','.join([x for x in self.keys])+ '), values=(' + ','.join([x for x in self.values])+ \
               '), func=' + str(self.func)+', threshold='+str(self.threshold)+')'
