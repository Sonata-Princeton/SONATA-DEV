#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

from sonata.query_engine.sonata_queries import *
from sonata.core.runtime import Runtime
import json, os

if __name__ == '__main__':
    with open('/home/vagrant/dev/sonata/config.json') as json_data_file:
        data = json.load(json_data_file)

    config = data["on_server"][data["is_on_server"]]["sonata"]
    T = 40

    n_syn = (PacketStream(1)
             .filter(filter_keys=('tcp.flags',), func=('eq', 2))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             .filter(filter_vals=('count',), func=('geq', T))
             .map(keys=('ipv4.dstIP',))
             )

    queries = [n_syn]

    # config["final_plan"] = [(1, 32, 1)]
    # config["final_plan"] = [(1, 32, 4)]
    config["final_plan"] = [(1, 24, 4), (1, 32, 4)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries, os.path.dirname(os.path.realpath(__file__)))