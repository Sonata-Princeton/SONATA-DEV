#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from __future__ import print_function

import time
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

def send_reduction_keys(rdd, op_handler_socket, start_time, qid='0', refinement_level='0', itera_qid='0'):
    list_rdd = rdd.collect()
    reduction_str = "," .join([str(r) for r in list_rdd])
    reduction_socket = Client(op_handler_socket)
    reduction_socket.send_bytes("k," + qid + "," + reduction_str + "\n")
    print("Sending P2: ", qid, list_rdd, reduction_str, " at time", time.time()-start_time)


def processLogLine(flow):
    return tuple(flow.split(","))

class StreamingManager(object):
    def __init__(self, conf, query_str, ref_queries):
        # initialize config params
        self.batch_interval = conf['batch_interval']
        self.window_length = conf['window_length']
        self.sliding_interval = conf['sliding_interval']
        self.featuresPath = conf['featuresPath']
        self.redKeysPath = conf['redKeysPath']
        self.sm_socket = conf['sm_socket']
        self.sm_listener = Listener(self.sm_socket)
        self.op_handler_socket = conf['op_handler_socket']
        print("In Streaming Manager", self.redKeysPath, self.featuresPath)
        self.start_time = time.time()
        #self.reduction_socket = Client(conf['op_handler_socket'])

        self.query = query_str
        self.refined_queries = ref_queries
        # intialize streaming context
        self.sc = SparkContext(appName="Sonata-Streaming")
        self.ssc = StreamingContext(self.sc, self.batch_interval)
        print("spark context initialized...")

    def start(self):
        lines = self.ssc.socketTextStream(spark_stream_address, spark_stream_port)
        lines.pprint()
        pktstream = (lines.map(lambda line: processLogLine(line)))
        self.process_pktstream(pktstream)
        print("process_pktstream initialized...")
        self.ssc.start()
        self.ssc.awaitTermination()

    def process_pktstream(self, pktstream):
        print("Waiting for streaming query expressions ...")


        for qid in self.refined_queries:
            for ref_level in refined_queries[qid]:
                for iter_qid in refined_queries[qid][ref_level]:
                    query_str = "pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd." + str(refined_queries[qid][ref_level][iter_qid].compile()) +")).foreachRDD(lambda rdd: send_reduction_keys(rdd, " + str(spark_conf['op_handler_socket']) + ",0,\'"+ str(qid)+"\',\'"+ str(ref_level)+"\',\'"+ str(iter_qid)+"\'))\n"
                    print("starting", query_str)
                    eval(query_str)



if __name__ == "__main__":
    spark_conf = {'batch_interval': batch_interval, 'window_length': window_length,
                  'sliding_interval': sliding_interval, 'featuresPath': featuresPath, 'redKeysPath': redKeysPath,
                  'sm_socket': ('localhost', 5555),
                  'op_handler_socket': ('localhost', 4949)}

    fname = 'query_engine/query_dumps/refined_queries_1.pickle'
    with open(fname,'r') as f:
        refined_queries = pickle.load(f)


    query_str = ""


    print(query_str)
    sm = StreamingManager(spark_conf, query_str, refined_queries)
    sm.start()
