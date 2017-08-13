#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

import os

from sonata.query_engine.sonata_queries import *
from sonata.core.runtime import Runtime
import json

if __name__ == '__main__':

    with open('/home/vagrant/dev/sonata/config.json') as json_data_file:
        data = json.load(json_data_file)
        print(data)

    config = data["on_server"][data["is_on_server"]]["sonata"]

    # q1 = (PacketStream(1)
    #       .filter(filter_keys=('ipv4.proto',), func=('eq', 17))
    #       .filter(filter_keys=('udp.sport',), func=('eq', 53))
    #       .filter(filter_keys=('dns.ns.type',), func=('eq', 46))
    #       .map(keys=('ipv4.dstIP', 'ipv4.srcIP'))
    #       .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP'))
    #       .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
    #       .reduce(keys=('ipv4.dstIP',), func=('sum',))
    #       .filter(filter_vals=('count',), func=('geq', 40))
    #       .map(keys=('ipv4.dstIP',))
    #       )

    n_syn = (PacketStream(1)
             .filter(filter_keys=('ipv4.proto'), func=('eq', 6))
             .filter(filter_keys=('tcp.flags'), func=('eq', 2))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             )

    n_synack = (PacketStream(2)
                .filter(filter_keys=('ipv4.proto'), func=('eq', 6))
                .filter(filter_keys=('tcp.flags'), func=('eq', 17))
                .map(keys=('ipv4.srcIP',), map_values=('count',), func=('eq', 1,))
                .reduce(keys=('ipv4.srcIP',), func=('sum',))
                )

    n_ack = (PacketStream(3)
             .filter(filter_keys=('ipv4.proto'), func=('eq', 6))
             .filter(filter_keys=('tcp.flags'), func=('eq', 16))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             )

    Th = 3

    # P4 - TCP Flags should be parsed in P4, right now they are missing in parser section
    # make qid = 1,2,3 run in dataplane in same window interval.
    # make qid = 4,5 - run in stream processor, enable join and sum/diff operations in SP
    # Also how to support 2*n3
    # also how multiple map_values might work here
    # Implement two kinds of joins here
    # Same Window Join - Spark
    # Consecutive Window Join - DataPlane filter operation
    syn_flood_victim = (n_syn
                        .join(new_qid=4, query=n_synack)
                        .map(map_keys=('ipv4.dstIP'), map_values=('count1', 'count2'), func=('sum'))
                        .join(new_qid=5, query=n_ack)
                        .map(keys=('ipv4.dstIP'), map_values=('count12', 'count3'), func=('diff', 1,))
                        .filter(filter_keys=('count'), func=('geq', Th))
                        #.map(IP, n1+n2-2*n3))
                        #.filter(IP, count => count > Th)
                        )

    queries = [syn_flood_victim]

    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
