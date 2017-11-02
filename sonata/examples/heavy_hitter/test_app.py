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

    # heavy hitter detection
    # This works with training data since we need to
    # first know how much is 99 percentile and then
    # use that 99 percentile as threshold
    heavy_hitter = (PacketStream(1)
                    .map(keys=('ipv4.dstIP', 'ipv4.srcIP'), map_values=('ipv4.totalLen',))
                    .reduce(keys=('ipv4.dstIP', 'ipv4.srcIP',), func=('sum',))
                    .filter(filter_vals=('ipv4.totalLen',), func=('geq', 40))
                    .map(keys=('ipv4.dstIP',))
                    )

    queries = [heavy_hitter]
    config["final_plan"] = [(1, 32, 3)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries,
                      os.path.dirname(os.path.realpath(__file__))
                      )
