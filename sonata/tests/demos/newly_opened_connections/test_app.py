#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

from sonata.query_engine.sonata_queries import *
from sonata.core.runtime import Runtime
import json

if __name__ == '__main__':
    with open('/home/vagrant/dev/sonata/config.json') as json_data_file:
        data = json.load(json_data_file)
        print(data)

    config = data["on_server"][data["is_on_server"]]["sonata"]
    T = 1

    n_syn = (PacketStream(1)
             .filter(filter_keys=('ipv4.proto',), func=('eq', 6))
             .filter(filter_keys=('tcp.flags',), func=('eq', 2))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             .filter(filter_vals=('ipv4.dstIP',), func=('geq', T))
             )

    queries = [n_syn]

    config["final_plan"] = [(1, 32, 2, 1)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
