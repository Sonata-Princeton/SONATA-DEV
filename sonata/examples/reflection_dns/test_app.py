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

    reflection_dns = (PacketStream(1)
                      .filter(filter_keys=('ipv4.protocol',), func=('eq', 17))
                      .filter(filter_keys=('udp.sport',), func=('eq', 53))
                      .filter(filter_keys=('dns.ns.type',), func=('eq', 46))
                      .map(keys=('ipv4.dstIP', 'ipv4.srcIP'))
                      .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP'))
                      .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
                      .reduce(keys=('ipv4.dstIP',), func=('sum',))
                      .filter(filter_vals=('count',), func=('geq', 40))
                      .map(keys=('ipv4.dstIP',))
                      )

    queries = [reflection_dns]
    config["final_plan"] = [(1, 32, 3)]

    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
