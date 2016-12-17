#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from __future__ import print_function

import time
import pickle
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
        print("spark context initialized...")

    def update_reduction_keys(self):
        while True:
            fname = "test.txt"
            print("Reduction Key fname ",fname)
            with open(fname, 'r') as f:
                dps = f.read().splitlines()
                if len(dps) == 0:
                    dmacs = []
                else:
                    dmacs = dps[0].split(',')
                print("Dmacs:", dmacs)
                self.reduction_keys = self.sc.parallelize([(x,1) for x in dmacs])
                #self.reduction_keys = self.sc.parallelize(dmacs)
                # for dubuging only
                print("File read:", self.reduction_keys.take(2))
                time.sleep(window_length)


    def start(self):
        self.reduction_key_updater = Thread(target=self.update_reduction_keys)
        self.reduction_key_updater.start()
        lines = self.ssc.socketTextStream(spark_stream_address, spark_stream_port)
        pktstream = (lines.map(lambda line: processLogLine(line)))
        print(pktstream)
        self.process_pktstream(pktstream)
        print("process_pktstream initialized...")
        self.ssc.start()
        self.ssc.awaitTermination()

    def process_pktstream(self, pktstream):
        def for_printing2(rdd):
            list_rdd = rdd.collect()
            print("P2: ", list_rdd)

        print("Waiting for streaming query expressions ...")
        conn = self.sm_listener.accept()
        print("Connection request accepted")
        raw_data = conn.recv()
        queries = pickle.loads(raw_data)
        print(queries)
        query_expressions = [x.compile() for x in queries]
        print(query_expressions)
        for query in query_expressions:
            q = eval("pktstream." + query)
            q.foreachRDD(lambda rdd: for_printing2(rdd))


if __name__ == "__main__":
    conf = {'batch_interval': batch_interval, 'window_length': window_length,
            'sliding_interval': sliding_interval, 'featuresPath': featuresPath,
            'redKeysPath': redKeysPath, 'sm_socket':('localhost',5555)}
    sm = StreamingManager(conf)
    sm.start()
