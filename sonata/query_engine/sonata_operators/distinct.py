#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)


from query import Query


class Distinct(Query):
    def __init__(self, *args, **kwargs):
        super(Distinct, self).__init__(*args, **kwargs)
        self.name = 'Distinct'
        map_dict = dict(*args, **kwargs)

        self.prev_keys = ()
        self.prev_values = ()
        self.keys = ()
        self.values = ()

        if 'prev_keys' in map_dict:
            self.prev_keys = map_dict['prev_keys']
        if 'prev_values' in map_dict:
            self.prev_values = map_dict['prev_values']
        if 'keys' in map_dict:
            self.keys = map_dict['keys']
        else:
            self.keys = self.prev_keys
        self.values = ()

    def __repr__(self):
        return '.Distinct(keys=' + str(self.keys) + ')'
