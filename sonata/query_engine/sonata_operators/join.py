#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query import Query


class Join(Query):
    def __init__(self, *args, **kwargs):
        super(Join, self).__init__(*args, **kwargs)
        self.name = 'Join'
        map_dict = dict(*args, **kwargs)
        self.query = map_dict['query']

    def __repr__(self):
        return '.Join(query=' + self.query.__repr__() + ')'
