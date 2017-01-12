#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from __future__ import print_function

import time
import json
import pickle
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from multiprocessing.connection import Client, Listener
from netaddr import *
spark_stream_address = 'localhost'
spark_stream_port = 7979

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000*window_length

featuresPath = ''
redKeysPath = ''


def send_reduction_keys(rdd, qid, refinement_level, itera_qid):
    print("Output received for Query", qid, "refinement level", refinement_level, "iteration id", itera_qid)
    list_rdd = rdd.collect()
    out_dict = dict((x,y) for (x,y) in list_rdd)
    print(out_dict)
    fname = "out_"+str(qid)+"_"+str(refinement_level)+"_"+str(itera_qid)+".json"
    with open(fname,'w') as f:
        json.dump(out_dict,f)


def process_log_line(flow):
    return tuple(flow.split(","))


class StreamingManager(object):
    def __init__(self, conf, ref_queries):
        # initialize config params
        self.batch_interval = conf['batch_interval']
        self.window_length = conf['window_length']
        self.sliding_interval = conf['sliding_interval']
        self.sm_socket = conf['sm_socket']

        self.sm_listener = Listener(self.sm_socket)
        print("In Streaming Manager for Query Training")
        self.start_time = time.time()
        self.refined_queries = ref_queries
        # intialize streaming context
        self.sc = SparkContext(appName="Sonata-Training")
        self.ssc = StreamingContext(self.sc, self.batch_interval)
        print("spark context initialized...")

    def start(self):
        lines = self.ssc.socketTextStream(spark_stream_address, spark_stream_port)
        lines.pprint()
        pktstream = (lines.map(lambda line: process_log_line(line)))
        self.process_pktstream(pktstream)
        print("process_pktstream initialized...")
        self.ssc.start()
        self.ssc.awaitTermination()

    def process_pktstream(self, pktstream):
        print("Waiting for streaming query expressions ...")
        for qid in self.refined_queries:
            for ref_level in refined_queries[qid]:
                for iter_qid in refined_queries[qid][ref_level]:
                    query_str = "pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.map(lambda p: p[1:])." + str(refined_queries[qid][ref_level][iter_qid].compile()) +")).foreachRDD(lambda rdd: send_reduction_keys(rdd,\'"+ str(qid)+"\',\'"+ str(ref_level)+"\',\'"+ str(iter_qid)+"\'))\n"
                    print("starting", query_str)
                    eval(query_str)


if __name__ == "__main__":
    spark_conf = {'batch_interval': batch_interval, 'window_length': window_length,
                  'sliding_interval': sliding_interval, 'sm_socket': ('localhost', 5555)}

    fname = 'query_engine/query_dumps/refined_queries_1.pickle'
    with open(fname,'r') as f:
        refined_queries = pickle.load(f)

    sm = StreamingManager(spark_conf, refined_queries)
    sm.start()
