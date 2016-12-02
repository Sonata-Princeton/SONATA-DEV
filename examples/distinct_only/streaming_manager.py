#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
from __future__ import print_function

import sys
import math
import time
import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from multiprocessing.connection import Client, Listener

from threading import Thread

spark_stream_address = 'localhost'
spark_stream_port = 8989

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000*window_length

featuresPath = ''
redKeysPath = ''

def processLogLine(flow):
    return tuple(flow.split(","))

class StreamingManager(object):
    def __init__(self, conf):
        # initialize config params
        self.batch_interval = conf['batch_interval']
        self.window_length = conf['window_length']
        self.sliding_interval = conf['sliding_interval']
        self.featuresPath = conf['featuresPath']
        self.redKeysPath = conf['redKeysPath']
        self.sm_socket = conf['sm_socket']
        self.sm_listener = Listener(self.sm_socket)
        print("In Streaming Manager", self.redKeysPath, self.featuresPath)

        # intialize streaming context
        self.sc = SparkContext(appName="Sonata-Streaming")
        self.ssc = StreamingContext(self.sc, self.batch_interval)
        print("Spark context initialized...")


    def start(self):
        lines = self.ssc.socketTextStream(spark_stream_address, spark_stream_port)
        pktstream = (lines.map(lambda line: processLogLine(line)))
        print(pktstream)
        self.process_pktstream(pktstream)
        print("process_pktstream() initialized...")
        self.ssc.start()
        self.ssc.awaitTermination()

    def process_pktstream(self, pktstream):
        def for_printing(rdd):
            list_rdd = rdd.collect()
            print("dIPs that satisfies the query: ", list_rdd)

        q = (pktstream.window(self.window_length, self.sliding_interval)
                .transform(lambda rdd: (rdd
                .map(lambda s: tuple([str(x.encode('utf-8').strip()) for x in s]))
                .map(lambda (dIP, sIP):((dIP,1)))
                .reduceByKey(lambda x,y: x+y)
                #.filter(lambda (dIP,count): count > 4)
                .map(lambda (dIP,count): (dIP))
                ))
            )
        q.foreachRDD(lambda rdd: for_printing(rdd))
if __name__ == "__main__":
    conf = {'batch_interval': batch_interval, 'window_length': window_length,
            'sliding_interval': sliding_interval, 'featuresPath': featuresPath,
            'redKeysPath': redKeysPath, 'sm_socket':('localhost',5555)}
    sm = StreamingManager(conf)
    sm.start()
