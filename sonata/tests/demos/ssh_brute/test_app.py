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

    brute_ssh = (PacketStream(1)
     # .filter(filter_keys=('proto',), func=('eq', 6))
     .map(keys=('ipv4.dstIP', 'ipv4.srcIP', 'ipv4.totalLen'))
     .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP', 'ipv4.totalLen'))
     .map(keys=('ipv4.dstIP','ipv4.totalLen'), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP','ipv4.totalLen'), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', '99'))
     .map(keys=('ipv4.dstIP',))
     )

    queries = [brute_ssh]

    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
