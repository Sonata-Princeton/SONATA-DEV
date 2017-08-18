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
    T = 1

    # super spreader detection
    # One host makes too many connections to different

    super_spreader = (PacketStream(1)
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('sIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('sIP',))
          )

    queries = [super_spreader]
    config["final_plan"] = [(1, 32, 2, 1)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
