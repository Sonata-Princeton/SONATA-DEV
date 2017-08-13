#!/usr/bin/env python
# Author: Arpit Gupta (arpitg@cs.princeton.edu)


class P4Field(object):

    def __init__(self, layer, target_name, sonata_name, size):
        # type: (object, object, object, object) -> object
        self.layer = layer
        self.target_name = target_name
        self.sonata_name = sonata_name
        self.size = size

    def __repr__(self):
        return "P4Field(target=" + self.target_name + ", sonata=" + self.sonata_name + ", size=" + str(self.size) +")"
