#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from __future__ import print_function

import time
import pickle
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from multiprocessing.connection import Client, Listener

spark_stream_address = 'localhost'
spark_stream_port = 8989

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000*window_length

featuresPath = ''
redKeysPath = ''

def send_reduction_keys(rdd, op_handler_socket, start_time, qid='0'):
    list_rdd = rdd.collect()
    reduction_str = "," .join([r for r in list_rdd])
    reduction_socket = Client(op_handler_socket)
    reduction_socket.send_bytes("k," + qid + "," + reduction_str + "\n")
    print("Sending P2: ", qid, list_rdd, reduction_str, " at time", time.time()-start_time)


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
        self.op_handler_socket = conf['op_handler_socket']
        print("In Streaming Manager", self.redKeysPath, self.featuresPath)
        self.start_time = time.time()
        #self.reduction_socket = Client(conf['op_handler_socket'])

        # intialize streaming context
        self.sc = SparkContext(appName="Sonata-Streaming")
        self.ssc = StreamingContext(self.sc, self.batch_interval)
        print("spark context initialized...")

    def start(self):
        lines = self.ssc.socketTextStream(spark_stream_address, spark_stream_port)
        #lines.pprint()
        pktstream = (lines.map(lambda line: processLogLine(line)))
        self.process_pktstream(pktstream)
        print("process_pktstream initialized...")
        self.ssc.start()
        self.ssc.awaitTermination()



    def process_pktstream(self, pktstream):

        print("Waiting for streaming query expressions ...")
        conn = self.sm_listener.accept()
        print("Connection request accepted")
        raw_data = conn.recv()
        queries = pickle.loads(raw_data)
        print ("Received queries", queries)
        spark_queries = {}
        pktstream.window(self.window_length, self.sliding_interval)\
            .transform(lambda rdd: (
            rdd.filter(lambda ((k,qid,dIP,count)): ((qid=='10001' )))
                .reduceByKey(lambda x,y: x+y)
                .filter(lambda ((dIP)): ((count>=3 )))
                .map(lambda ((dIP)): ((dIP)))))
        for queryId in queries:
            query = queries[queryId]
            query_str = "pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd." + query.compile() + ")).foreachRDD(lambda rdd: send_reduction_keys(rdd, " + str(self.op_handler_socket)+ "," + str(self.start_time)+",\'"+ str(queryId)+"\'))"
            print(query_str)
            spark_queries[queryId] = eval(query_str)

if __name__ == "__main__":
    conf = {'batch_interval': batch_interval, 'window_length': window_length,
            'sliding_interval': sliding_interval, 'featuresPath': featuresPath,
            'redKeysPath': redKeysPath, 'sm_socket':('localhost', 5555)}
    sm = StreamingManager(conf)
    sm.start()
