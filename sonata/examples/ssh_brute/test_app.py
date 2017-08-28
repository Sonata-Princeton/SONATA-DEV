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

    brute_ssh = (PacketStream(1)
                 # .filter(filter_keys=('proto',), func=('eq', 6))
                 .map(keys=('ipv4.dstIP', 'ipv4.srcIP', 'ipv4.totalLen'))
                 .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP', 'ipv4.totalLen'))
                 .map(keys=('ipv4.dstIP', 'ipv4.totalLen'))
                 .map(keys=('ipv4.dstIP', 'ipv4.totalLen'), map_values=('count',), func=('eq', 1,))
                 .reduce(keys=('ipv4.dstIP', 'ipv4.totalLen'), func=('sum',))
                 .filter(filter_vals=('count',), func=('geq', 40))
                 .map(keys=('ipv4.dstIP',))
                 )

    dorros_payload = (PacketStream(2)
                      .map(keys=('ipv4.dstIP', 'ipv4.srcIP', 'ipv4.totalLen'))
                      )

    dorros_attack = (brute_ssh.join)

    queries = [brute_ssh]
    config["final_plan"] = [(1, 8, 3, 1), (1, 32, 3, 1)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
