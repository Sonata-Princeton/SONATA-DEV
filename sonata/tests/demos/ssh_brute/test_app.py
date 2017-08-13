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

    brute_ssh = (PacketStream(4)
     # .filter(filter_keys=('proto',), func=('eq', 6))
     .map(keys=('dIP', 'sIP', 'nBytes'))
     .distinct(keys=('dIP', 'sIP', 'nBytes'))
     .map(keys=('dIP','nBytes'), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('dIP','nBytes'), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', '99'))
     .map(keys=('dIP',))
     )

    queries = [brute_ssh]

    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
