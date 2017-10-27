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

    n_syn = (PacketStream(1)
             .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
             .filter(filter_keys=('tcp.flags',), func=('eq', 2))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             )

    n_synack = (PacketStream(2)
                .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
                .filter(filter_keys=('tcp.flags',), func=('eq', 17))
                .map(keys=('ipv4.srcIP',), map_values=('count',), func=('set', 1,))
                .reduce(keys=('ipv4.srcIP',), func=('sum',))
                )

    n_ack = (PacketStream(3)
             .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
             .filter(filter_keys=('tcp.flags',), func=('eq', 16))
             .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
             .reduce(keys=('ipv4.dstIP',), func=('sum',))
             )

    Th = 3

    syn_flood_victim = (n_syn
                        .join(window='Same',new_qid=4, query=n_synack)
                        .map(map_keys=('ipv4.dstIP',), map_values=('count_right', 'count_left',), func=('sum'))
                        # .join(window='Same',new_qid=5, query=n_ack)
                        # .map(keys=('ipv4.dstIP'), map_values=('count_right', 'count_left',), func=('diff', 1,))
                        # .filter(filter_keys=('count'), func=('geq', Th))
                        )

    queries = [syn_flood_victim]

    config["final_plan"] = [(1, 16, 4), (1, 32, 4),
                            (2, 16, 4), (2, 32, 4),
                            # (3, 16, 4, 1), (3, 32, 4, 1)
                            ]

    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries,
                      os.path.dirname(os.path.realpath(__file__))
                      )
