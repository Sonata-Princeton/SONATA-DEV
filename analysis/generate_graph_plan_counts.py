#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
import math

from sonata.query_engine.sonata_queries import *
from sonata.core.training.utils import create_spark_context
from sonata.core.integration import Target
from sonata.core.refinement import Refinement
from sonata.core.training.hypothesis.hypothesis import Hypothesis

def parse_log_line(logline):
    return tuple(logline.split(","))

def generate_graph(sc, query):
    TD_PATH = '/mnt/caida_5min.csv'

    flows_File = TD_PATH
    T = 10

    if query.qid == 1:
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto) == '17')
                         )

    elif query.qid == 2:
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         )

    if query.qid == 3:
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto) == '6')
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(sPort) == '22' or str(dPort) == '22')
                         .map(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): (ts,sIP,sPort,dIP,dPort,int(nBytes)/10,proto,sMac,dMac))
                         )
    elif query.qid == 4:
        # only applied over DNS response traffic
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto) == '17')
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(sPort) == '53')
                         )
    elif query.qid == 5:
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto) == '17')
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(sPort) == '19')
                         )
    elif query.qid == 6:
        # Response traffic for NTP protocol
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto) == '17')
                         )


    training_data = sc.parallelize(training_data.collect())
    print "Collecting timestamps for the experiment ..."
    timestamps = training_data.map(lambda s: s[0]).distinct().collect()
    print "#Timestamps: ", len(timestamps)
    target = Target()
    refinement_object = Refinement(query, target)
    refinement_object.update_filter(training_data)
    hypothesis = Hypothesis(query, sc, training_data, timestamps,refinement_object, target)
    G = hypothesis.G
    fname = 'data/hypothesis_graph_'+str(query.qid) + '_plan_counts_' +'_5min_caida_' + str(min) + '_'+str(datetime.datetime.fromtimestamp(time.time()))+'.pickle'

    # dump the hypothesis graph: {ts:G[ts], ...}
    print "Dumping graph to", fname
    with open(fname, 'w') as f:
        pickle.dump(G, f)

if __name__ == '__main__':
    # original reflection attack query
    q1 = (PacketStream(1)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.9'))
          .map(keys=('dIP',))
          )

    # port scan
    q2 = (PacketStream(2)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('sIP', 'dPort'))
          .distinct(keys=('sIP', 'dPort'))
          .map(keys=('sIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('sIP',))
          )

    # ssh brute forcing
    q3 = (PacketStream(3)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP', 'nBytes'))
          .distinct(keys=('dIP', 'sIP', 'nBytes'))
          .map(keys=('dIP','nBytes'), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP','nBytes'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('dIP',))
          )

    # reflection attack query (DNS)
    q4 = (PacketStream(4)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('dIP',))
          )

    # reflection attack query (NTP)
    q5 = (PacketStream(5)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('dIP',))
          )

    q6 = (PacketStream(6)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('sIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('sIP',))
          )

    queries = [q1, q2, q3, q4, q5, q6]

    for q in queries:
        sc = create_spark_context()
        generate_graph(sc, q)
        sc.stop()