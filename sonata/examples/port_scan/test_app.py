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

    # port scan
    # One host is scanning lot of different ports
    # this potentially happens before an attack
    port_scan = (PacketStream(1)
          .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
          .map(keys=('ipv4.srcIP', 'tcp.dport'))
          .distinct(keys=('ipv4.srcIP', 'tcp.dport'))
          .map(keys=('ipv4.srcIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('ipv4.srcIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', T))
          .map(keys=('ipv4.srcIP',))
          )

    queries = [port_scan]
    config["final_plan"] = [(1, 32, 6)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries,os.path.dirname(os.path.realpath(__file__))
                      )
