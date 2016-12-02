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

    def start_fabric_managers(self):
        # Start the fabric managers local to each data plane element
        return 0

    def start_streaming_managers(self):
        # Start streaming managers local to each stream processor
        return 0

    def apply_iterative_refinement(self):
        return 0

    def compile(self):
        query_expressions = []
        for query in self.queries:
            query_expressions.append(query.compile_sp())
        return query_expressions

    def send_config(self):
        self.send_to_sm()
        self.send_to_fm()

    def send_init_config(self):
        # send initial config to FMs and SMs
        return 0

    def send_update_config(self):
        # send delta config updates to SMs & FMs
        return 0

    def receive_query_output(self):
        # receive query output from stream processor
        return 0


    def send_to_sm(self):
        # Send compiled query expression to streaming manager
        query_expressions = self.compile()
        print query_expressions
        conn = Client(self.conf['sm_socket'])
        conn.send(json.dumps(query_expressions))
        time.sleep(3)
        print "Config Sent to Streaming Manager ..."

    def send_to_fm(self):
        # Send compiled query expression to fabric manager
        return ''



#.reduceByKey("sum")
