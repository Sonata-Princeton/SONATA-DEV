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
        #self.reduction_key_updater = Thread(target=self.update_reduction_keys)
        #self.reduction_key_updater.start()
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

        def for_printing1(rdd):
            list_rdd = rdd.collect()
            #print(list_rdd)
            fname = "test.txt"
            with open(fname,'w') as f:
                f.write(",".join([x for x in list_rdd]))

        """
        sm_listener = Listener(('localhost',7777))
        print("Waiting for streaming query expressions ...")
        conn = sm_listener.accept()
        print("Connection request accepted")
        raw_data = conn.recv()
        query_expressions = [str(x) for x in json.loads(raw_data)]
        print(query_expressions)


        q2 = eval("pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.map(lambda s: tuple([str(x.encode('utf-8').strip()) for x in s]))."
                +query_expressions[0]+"))")


        q1 = (pktstream.window(self.window_length, self.sliding_interval)
                .transform(lambda rdd: (rdd
                .map(lambda s: tuple([str(x.encode('utf-8').strip()) for x in s]))
                .filter(lambda (ts,te,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): proto == '17')
                .map(lambda (ts,te,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): ((dMac,sIP)))
                .distinct()
                .map(lambda (dMac, sIP):((dMac,1)))
                .reduceByKey(lambda x,y: x+y)
                .filter(lambda (dMac,count): count > 20)
                .map(lambda (dMac,count): (dMac))))
            )
        """

        q2 = (pktstream.window(self.window_length, self.sliding_interval)
                .transform(lambda rdd: (rdd
                .map(lambda s: tuple([str(x.encode('utf-8').strip()) for x in s]))
                #.filter(lambda (ts,te,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): proto == '17')
                #.map(lambda (ts,te,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac):
                #    (dMac,(ts,te,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac)))
                #.join(self.reduction_keys)
                #.map(lambda s: s[1][0])
                #.map(lambda (ts,te,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): ((dIP,sIP)))
                #.distinct()
                .map(lambda (dIP, sIP):((dIP,1)))
                .reduceByKey(lambda x,y: x+y)
                #.filter(lambda (dIP,count): count > 4)
                .map(lambda (dIP,count): (dIP))
                ))
            )


        """

        #q1.foreachRDD(lambda rdd: for_printing1(rdd))
        q2 = (pktstream.window(self.window_length, self.sliding_interval)
                .transform(lambda rdd: (rdd
                .map(lambda s: tuple([str(x.encode('utf-8').strip()) for x in s]))
                #.map(lambda (dIP, sIP):((dIP,1)))
                #.reduceByKey(lambda x,y: x+y)
                #.filter(lambda (dIP,count): count > 2)
                #.map(lambda (dIP,count): (dIP))
                ))
            )
        """
        q2.foreachRDD(lambda rdd: for_printing2(rdd))

        #q = eval(query)

if __name__ == "__main__":
    conf = {'batch_interval': batch_interval, 'window_length': window_length,
            'sliding_interval': sliding_interval, 'featuresPath': featuresPath,
            'redKeysPath': redKeysPath, 'sm_socket':('localhost',5555)}
    sm = StreamingManager(conf)
    sm.start()
