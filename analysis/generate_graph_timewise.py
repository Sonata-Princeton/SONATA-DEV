#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
import math

from sonata.query_engine.sonata_queries import *
from sonata.core.training.utils import get_spark_context_batch, create_spark_context
from sonata.core.integration import Target
from sonata.core.refinement import apply_refinement_plan, get_refined_query_id, Refinement
from sonata.core.training.hypothesis.hypothesis import Hypothesis

def parse_log_line(logline):
    return tuple(logline.split(","))

def generate_graph(sc, query, min,T):
    TD_PATH = '/mnt/anon_all_flows_1min.csv'

    flows_File = TD_PATH
    T = T
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

    # print "Collecting the training data for the first time ...", training_data.take(2)
    training_data = sc.parallelize(training_data.collect())
    print "Collecting timestamps for the experiment ..."
    timestamps = training_data.map(lambda s: s[0]).distinct().collect()
    print "#Timestamps: ", len(timestamps)
    target = Target()
    refinement_object = Refinement(query, target)
    refinement_object.update_filter(training_data)
    hypothesis = Hypothesis(query, sc, training_data, timestamps,refinement_object, target)
    G = hypothesis.G
    fname = 'data/hypothesis_graph_'+str(query.qid) + '_T_' + str(T) +'_1min_' + str(min) + '_'+str(datetime.datetime.fromtimestamp(time.time()))+'.pickle'

    # dump the hypothesis graph: {ts:G[ts], ...}
    print "Dumping graph to", fname
    with open(fname, 'w') as f:
        pickle.dump(G, f)

if __name__ == '__main__':

    timeSlots = range(1, 11)

    for T in timeSlots:
        sc = create_spark_context()
        q = (PacketStream(1)
              # .filter(filter_keys=('proto',), func=('eq', 6))
              .map(keys=('dIP', 'sIP'))
              .distinct(keys=('dIP', 'sIP'))
              .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
              .reduce(keys=('dIP',), func=('sum',))
              .filter(filter_vals=('count',), func=('geq', '99.9'))
              .map(keys=('dIP',))
              )
        print "Starting: ", str(q.qid), " T:", str(T)
        generate_graph(sc, q, 0, T)
        sc.stop()
