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
    T = 40

    n_resp = (PacketStream(1)
              .filter(filter_keys=('ipv4.protocol',), func=('eq', 17))
              .map(keys=('ipv4.dstIP', 'udp.sport'), map_values=('count',), func=('set', 1,))
              .reduce(keys=('ipv4.dstIP', 'udp.sport'), func=('sum',))
              .filter(filter_vals=('count',), func=('geq', T))
              )

    # Confirm the fin flag number here
    n_req = (PacketStream(2)
             .filter(filter_keys=('ipv4.protocol',), func=('eq', 17))
             .map(keys=('ipv4.srcIP', 'udp.dport'), map_values=('count',), func=('set', 1,))
             .reduce(keys=('ipv4.srcIP', 'udp.dport'), func=('sum',))
             # .filter(filter_vals=('count',), func=('geq', T))
             )

    # TODO: Commented for testing
    # TODO: put index in header field
    # T = 1
    q3 = (n_resp
          .join(query=n_req, new_qid=3)
          .map(keys=('ipv4.dstIP', 'ipv4.srcIP',), map_values=('count1', 'count2',),
               func=('diff',))  # make output diff called 'diff3'
          .filter(filter_vals=('diff3',), func=('geq', T))
          .map(keys=('ipv4.dstIP'))
          )

    queries = [q3]
    config["final_plan"] = [(1, 32, 4), (2, 32, 3)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
