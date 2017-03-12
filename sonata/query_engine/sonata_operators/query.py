#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

class Query(object):
    """
    Abstract Query Class
    """
    basic_headers = ["sIP", "sPort", "dIP", "dPort", "nBytes",
                     "proto", "sMac", "dMac", "payload"]
    refinement_headers = ["dIP", "sIP"]

    def __init__(self, *args, **kwargs):
        self.fields = []
        self.keys = []
        self.values = []
        self.expr = ''
        self.name = ''

    def eval(self):
        """
        evaluate this policy
        :param ?
        :type pkt: ?
        :rtype: ?
        """
        return self.expr