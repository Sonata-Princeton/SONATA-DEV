#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

def get_streaming_cost(sc, last_operator_name, query_out):
    return sc.parallelize(query_out)