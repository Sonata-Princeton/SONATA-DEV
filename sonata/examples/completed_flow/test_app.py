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

    config = data["on_server"][data["is_on_server"]]["sonata"]
    T = 1

    n_syn = (PacketStream(1)
             .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
             .filter(filter_keys=('tcp.flags',), func=('eq', 2))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             )

    # Confirm the fin flag number here
    n_fin = (PacketStream(2)
             .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
             .filter(filter_keys=('tcp.flags',), func=('eq', 1))
             .map(keys=('ipv4.srcIP',), map_values=('count',), func=('set', 1,))
             .reduce(keys=('ipv4.srcIP',), func=('sum',))
             )

    T = 1
    q3 = (n_syn.join(n_fin)
          .map(keys=('ipv4.dstIP', 'ipv4.srcIP',), map_values=('count1', 'count2',),
               func=('diff',))
          .filter(filter_vals=('diff3',), func=('geq', T))
          .map(keys=('ipv4.dstIP'))
          )

    queries = [q3]
    config["final_plan"] = [(1, 32, 2)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
