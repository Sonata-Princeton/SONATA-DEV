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

    # super spreader detection
    # One host makes too many connections to different

    super_spreader = (PacketStream(1)
          .map(keys=('ipv4.dstIP', 'ipv4.srcIP'))
          .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP'))
          .map(keys=('ipv4.srcIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('ipv4.srcIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 40))
          .map(keys=('ipv4.srcIP',))
          )

    queries = [super_spreader]
    config["final_plan"] = [(1, 32, 5)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config,
                      queries,
                      os.path.dirname(os.path.realpath(__file__))
                      )