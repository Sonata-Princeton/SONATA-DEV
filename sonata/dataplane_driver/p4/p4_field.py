#!/usr/bin/env python
# Author: Arpit Gupta (arpitg@cs.princeton.edu)


class P4Field(object):

    def __init__(self, layer, target_name, sonata_name, size):
        self.layer = layer
        self.target_name = target_name
        self.sonata_name = sonata_name
        self.size = size
