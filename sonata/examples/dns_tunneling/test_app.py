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

    # Normally ttl is only 1 value
    # but if it is an attack it will keep changing.

    q1 = (PacketStream(1)
          # .filter(filter_keys=('ipv4.proto',), func=('eq', 17))
          .filter(filter_keys=('udp.sport',), func=('eq', 53))
          .filter(filter_keys=('dns.ancount',), func=('geq', 1))
          .map(keys=('dns.an.rdata',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('dns.an.rdata',), func=('sum',))

          )

    q2 = (PacketStream(2)
          .filter(filter_keys=('tcp.dport',), func=('eq', 80))
          .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('ipv4.dstIP',), func=('sum',))
          )

    T = 1
    q3 = (q1.join(q2)
          .map(keys=('dns.an.rdata', 'ipv4.dstIP',), map_values=('count1', 'count2',),
               func=('diff',))  # make output diff called 'diff3'
          .filter(filter_vals=('diff3',), func=('geq', T))
          .map(keys=('ipv4.dstIP'))
          )

    queries = [q3]
    config["final_plan"] = [(1, 32, 2)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
