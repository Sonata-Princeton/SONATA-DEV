#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime
import math
from netaddr import *

from sonata.query_engine.sonata_queries import *
from sonata.core.training.utils import get_spark_context_batch, create_spark_context
from sonata.core.integration import Target
from sonata.core.refinement import apply_refinement_plan, get_refined_query_id, Refinement
from sonata.core.training.hypothesis.hypothesis import Hypothesis

def parse_log_line(logline):
    return tuple(logline.split(","))

def generate_graph(sc, query):
    TD_PATH = '/mnt/anon_all_flows_5min.csv'
    # TD_PATH = '/mnt/anon_all_flows_1min.csv'
    # TD_PATH = '/mnt/anon_all_flows_5min.csv/part-00500'
    # TD_PATH = '/mnt/anon_all_flows_1min.csv'
    TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv/part-00496'
    TD_PATH = '/mnt/anon_all_flows_1min.csv/part-00496'
    # TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv'

    flows_File = TD_PATH
    T = 1
    if query.qid == 1:
        training_data = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto) == '17')
                         )

    elif query.qid == 2:
        # training_data = (sc.textFile(flows_File)
        #                  .map(parse_log_line)
        #                  .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
        #                  #TODO: Remove from here
        #                  .map(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): (ts,1))
        #                  .reduceByKey(lambda x,y: x+y)
        #                  .collect()
        #                  )
        # print training_data
        #
        # training_data = (sc.textFile(flows_File)
        #                  .map(parse_log_line)
        #                  .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
        #                  #TODO: Remove from here
        #                  .map(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): ((ts,str(IPNetwork(str(str(dIP)+"/4")).network)),1))
        #                  .reduceByKey(lambda x,y: x+y)
        #                  .filter(lambda  ((ts, dIP), count): ts == 1440289056)
        #                  .collect()
        #                  )
        # print training_data
        # .map(keys=('dIP', 'dPort','sPort','sIP'), map_values=('count',), func=('eq', 1,))
        # .reduce(keys=('dIP', 'dPort','sPort','sIP',), func=('sum',))
        # .filter(filter_vals=('count',), func=('geq', '99'))
        # .map(keys=('dIP',))
        output_level_4 = (sc.textFile(flows_File)
                         .map(parse_log_line)
                         .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                         .filter(lambda s: int(s[0])==1440289056)
                         #TODO: Remove from here
                         .map(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): ((ts, str(IPNetwork(str(str(dIP)+"/4")).network), dPort,sPort,sIP),int(nBytes)))
                         .reduceByKey(lambda x,y: x+y)
                         .filter(lambda ((ts, dIP,dPort,sPort,sIP), count): count >= 4530)
                         .map(lambda ((ts, dIP,dPort,sPort,sIP), count): ((ts, dIP),1))
                         .distinct()
                         .collect()
                         )

        print output_level_4
        # output_level_4_code = (sc.textFile(flows_File)
        #                        .map(parse_log_line)
        #                        .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
        #                      .map(lambda ((ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac)): ((ts,sIP,sPort,str(IPNetwork(str(str(dIP)+"/4")).network),dPort,nBytes,proto,sMac,dMac)))
        #                      .map(lambda ((ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac)): ((ts,dIP,dPort,sPort,sIP),(1)))
        #                      .map(lambda s: (s[0], float(s[1])))
        #                      .reduceByKey(lambda x,y: x+y)
        #                      .filter(lambda ((ts,dIP,dPort,sPort,sIP),(count)): ((float(count)>=2.0 ))).collect())
        #
        # print output_level_4[:5], output_level_4_code[:5]
        # print len(output_level_4), len(output_level_4_code)
        output_level_32_total = (sc.textFile(flows_File)
                           .map(parse_log_line)
                           .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                           .filter(lambda s: int(s[0])==1440289056)
                           .map(lambda s: (s[0],1))
                           .reduceByKey(lambda x,y: x+y)
                           .collect()
                           )
        print output_level_32_total

        output_level_32_after_join = (sc.textFile(flows_File)
                          .map(parse_log_line)
                          .map(lambda s: tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                          .map(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac):
                           ((ts, str(IPNetwork(str(str(dIP)+"/4")).network)), (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac)))
                          # #TODO: Remove from here
                          .join(sc.parallelize(output_level_4))
                          .map(lambda s: s[1][0])
                          .map(lambda s: (s[0],1))
                          .reduceByKey(lambda x,y: x+y)
                          .collect()
                          )

        print output_level_32_after_join

        # output_level_4_to_32 = (sc.parallelize(output_level_32)
        #     .map(lambda ((ts,dIP,dPort,sPort,sIP),(count)):((ts, str(IPNetwork(str(dIP)+"/"+str(4)).network)),((ts,dIP,dPort,sPort,sIP),(count))))
        #     .join(sc.parallelize(output_level_4))
        #     .map(lambda x: x[1][0]).map(lambda s: (s[0][0], s[1]))
        #     .groupByKey()
        #     .map(lambda s: (s[0], list(s[1])))
        #     .collect())
        #
        #
        #
        # print output_level_4_to_32


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
        # training_data = sc.parallelize(training_data.collect())
        # print "Collecting timestamps for the experiment ..."
        # timestamps = training_data.map(lambda s: s[0]).distinct().collect()
        # print "#Timestamps: ", len(timestamps)
        # target = Target()
        # refinement_object = Refinement(query, target)
        # refinement_object.update_filter(training_data)
        # hypothesis = Hypothesis(query, sc, training_data, timestamps,refinement_object, target)
        # G = hypothesis.G
        # fname = 'data/hypothesis_graph_'+str(query.qid)+'_'+str(datetime.datetime.fromtimestamp(time.time()))+'.pickle'
        #
        # # dump the hypothesis graph: {ts:G[ts], ...}
        # print "Dumping graph to", fname
        # with open(fname, 'w') as f:
        #     pickle.dump(G, f)

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
    # heavy hitter detection
    # q2 = (PacketStream(2)
    #       # .filter(filter_keys=('proto',), func=('eq', 6))
    #       .map(keys=('dIP', 'dPort','sPort','sIP'), values=('nBytes',))
    #       .reduce(keys=('dIP', 'dPort','sPort','sIP',), func=('sum',))
    #       .filter(filter_vals=('nBytes',), func=('geq', '99'))
    #       .map(keys=('dIP',))
    #       )

    q2 = (PacketStream(2)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          # .map(keys=('dIP', 'dPort','sPort','sIP'), values=('nBytes',))
          .map(keys=('dIP', 'dPort','sPort','sIP'), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP', 'dPort','sPort','sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('dIP',))
          )

    # ssh brute forcing
    q3 = (PacketStream(3)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP', 'nBytes'))
          .distinct(keys=('dIP', 'sIP', 'nBytes'))
          .map(keys=('dIP','nBytes'), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP','nBytes'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
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

    queries = [q1, q3, q4, q5, q6]
    queries = [q2]
    sc = create_spark_context()
    for q in queries:
        generate_graph(sc, q)