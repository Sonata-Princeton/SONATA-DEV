#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from __future__ import print_function

import time
import pickle
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from multiprocessing.connection import Client, Listener
import json


def send_reduction_keys(rdd, op_handler_socket, start_time, qid='0'):
    list_rdd = rdd.collect()
    reduction_str = ",".join([r for r in list_rdd])
    reduction_socket = Client(tuple(op_handler_socket))
    reduction_socket.send_bytes("k," + qid + "," + reduction_str + "\n")
    print("Sending P2: ", qid, list_rdd, reduction_str, " at time", time.time() - start_time)


def processLogLine(flow):
    return tuple(flow.split(","))


class StreamingDriver(object):
    def __init__(self, conf):
        # initialize config params
        self.batch_interval = conf['batch_interval']
        self.window_length = conf['window_length']
        self.sliding_interval = conf['sliding_interval']
        self.sm_socket = tuple(conf['sm_socket'])
        self.sm_listener = Listener(self.sm_socket)
        self.op_handler_socket = conf['op_handler_socket']

        self.spark_stream_address = conf['spark_stream_address']
        self.spark_stream_port = conf['spark_stream_port']

        self.start_time = time.time()

        self.sc = SparkContext(appName="Sonata-Streaming")
        self.sc.setLogLevel("OFF")
        self.ssc = StreamingContext(self.sc, self.batch_interval)

    def start(self):
        lines = self.ssc.socketTextStream(self.spark_stream_address, self.spark_stream_port)
        pktstream = (lines.map(lambda line: processLogLine(line)))
        print(self.window_length, self.sliding_interval)
        self.process_pktstream(pktstream)
        self.ssc.start()
        self.ssc.awaitTermination()

    def process_pktstream(self, pktstream):
        print("pktstream")

        spark_queries = {}

        conn = self.sm_listener.accept()
        raw_data = conn.recv()
        data = pickle.loads(raw_data)

        queries = data['queries']
        join_queries = data['join_queries']

        for queryId in queries:
            query = queries[queryId]

            if not query.has_join and queryId not in join_queries:
                query_str = "pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.filter(lambda p : (p[1]==str('" + str(queryId) + "'))).map(lambda p : (p[2:]))." + query.compile() + ")).foreachRDD(lambda rdd:send_reduction_keys(rdd, " + str(self.op_handler_socket) + "," + str(self.start_time) + ",\'" + str(queryId) + "\'))"
                print(query_str)
                spark_queries[queryId] = eval(query_str)
            elif not query.has_join and queryId in join_queries:
                query_str = "pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.filter(lambda p : (p[1]==str('" + str(queryId) + "'))).map(lambda p : (p[2:]))." + query.compile() + "))" #.foreachRDD(lambda rdd:send_reduction_keys(rdd, " + str(self.op_handler_socket) + "," + str(self.start_time) + ",\'" + str(queryId) + "\'))"
                print(query_str)
                spark_queries[queryId] = eval(query_str)
            else:
                query_str = query.compile() + ".foreachRDD(lambda rdd: print(\"Join \" + str(rdd.take(5))))"
                print(query_str)
                spark_queries[queryId] = eval(query_str)

            # spark_queries[1210032] = pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.filter(lambda p : (p[1]==str('1210032'))).map(lambda p : (p[2:])).map(lambda ((ipv4_dstIP,ipv4_srcIP,tcp_sport)): ((ipv4_dstIP,ipv4_srcIP,tcp_sport))).map(lambda ((ipv4_dstIP,ipv4_srcIP,tcp_sport)): ((ipv4_dstIP),(1))).reduceByKey(lambda x,y: x+y).filter(lambda ((ipv4_dstIP),(count)): ((float(count)>=10 ))))).foreachRDD(lambda rdd:send_reduction_keys(rdd, [u'localhost', 4949],1504476340.91,'1210032'))

        # print(spark_queries)
        # spark_queries[1220032].join(spark_queries[1210032]).map(lambda ((ipv4_dstIP),(ipv4_totalLen,count)): ((ipv4_dstIP),(ipv4_totalLen/count))).filter(lambda ((ipv4_dstIP),(count2)): ((float(count2)>=10 ))).foreachRDD(lambda rdd: print("Join " + str(rdd.take(5))))

            # spark_queries['1220032'].join(spark_queries['1210032']).map(lambda ((ipv4_dstIP),(ipv4_totalLen,count)): ((ipv4_dstIP),(ipv4_totalLen/count))).filter(lambda ((ipv4_dstIP),(count2)): ((float(count2)>=10 ))).foreachRDD(lambda rdd: print("Join " + str(rdd.take(5))))
            # spark_queries['1220032'].join(spark_queries['1210032']).map(lambda ((('ipv4.dstIP')),(ipv4.totalLen,count)): ((ipv4_dstIP),(ipv4.totalLen/count))).filter(lambda ((ipv4_dstIP),(count2)): ((float(count2)>=10 ))).foreachRDD(lambda rdd: print("Join " + str(rdd.take(5))))
            # spark_queries['1220032'].join(spark_queries['1210032']).map(lambda (((ipv4_dstIP)),(ipv4_totalLen,count)): ((ipv4_dstIP),)).filter(lambda ((ipv4_dstIP),(count2)): ((float(count2)>=10 ))).foreachRDD(lambda rdd: print("Join " + str(rdd.take(5))))
            # pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.filter(lambda p : (p[1]== '10032')).map(lambda p : (p[2:]))).collect())
            # pktstream.window(self.window_length, self.sliding_interval).transform(lambda rdd: (rdd.filter(lambda p : (p[1]==str('1210032'))).map(lambda p : (p[2:]))..map(lambda ((ipv4_dstIP,ipv4_srcIP,tcp_sport)): ((ipv4_dstIP,ipv4_srcIP,tcp_sport))).map(lambda ((ipv4_dstIP,ipv4_srcIP,tcp_sport)): ((ipv4_dstIP),(1))).reduceByKey(lambda x,y: x+y).filter(lambda ((ipv4_dstIP),(count)): ((float(count)>=10 ))))).foreachRDD(lambda rdd:send_reduction_keys(rdd, [u'localhost', 4949],1504474502.52,'1210032'))
            # spark_queries['20032'] = pktstream.window(
            #     self.window_length, self.sliding_interval) \
            #     .transform(lambda rdd: (rdd
            #                             .filter(lambda p: (p[1] == str('20032')))
            #                             .map(lambda p: (p[2:]))
            #                             .map(lambda ((ipv4_srcIP, udp_dport, count)): ((ipv4_srcIP, udp_dport), (count)))
            #                             .reduceByKey(lambda x,y: x+y))
            #                )
            #
            # spark_queries['10032'] = pktstream.window(self.window_length, self.sliding_interval)\
            #     .transform(lambda rdd: (rdd
            #                             .filter(lambda p: (p[1] == str('10032')))
            #                             .map(lambda p: (p[2:]))
            #                             .map(lambda ((ipv4_dstIP, udp_sport, count)): ((ipv4_dstIP, udp_sport), (count)))
            #                             .reduceByKey(lambda x,y: x+y))
            #                )
            #
            # spark_queries['10032'].join(spark_queries['20032'])\
            #     .map(lambda s: (s[0], float(s[1][0])-float(s[1][1]))).foreachRDD(lambda rdd: print("Join " + str(rdd.take(5))))
            # .filter(lambda s: s[1] > 1)\
            # .map(lambda s: s[0][0])\
            # .foreachRDD(lambda rdd: print("Join " + str(rdd.take(5))))


if __name__ == "__main__":
    with open('/home/vagrant/dev/sonata/config.json') as json_data_file:
        data = json.load(json_data_file)
        print(data)

    config = data["on_server"][data["is_on_server"]]["sonata"]
    sm = StreamingDriver(config)
    sm.start()
