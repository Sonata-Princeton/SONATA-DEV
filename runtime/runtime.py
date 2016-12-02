#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine import *
import json, time
from multiprocessing.connection import Client

class Runtime(object):
    def __init__(self, conf, queries):
        self.conf = conf
        self.queries = queries

    def send_to_sm(self):
        # Send compiled query expression to streaming manager
        query_expressions = []
        for query in self.queries:
            query_expressions.append(query.compile_sp())
        print query_expressions
        conn = Client(self.conf['sm_socket'])
        conn.send(json.dumps(query_expressions))
        time.sleep(3)
        print "Query Expressions sent"

    def send_to_fm(self):
        # Send compiled query expression to fabric manager
        return ''



#.reduceByKey("sum")
