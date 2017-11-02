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
    T1 = 30
    T2 = 2
    T3 = 20

    n_resp = (PacketStream(1)
              # Add code here
              .filter(filter_vals=('count',), func=('geq', T1))
              )

    n_req = (PacketStream(2)
             # Add code here
             .filter(filter_vals=('count',), func=('geq', T2))
             )

    q3 = (n_resp
          .join(window='Same', query=n_req, new_qid=3)
          .map(map_values=('diff1',), func=('diff',))
          .filter(filter_vals=('diff1',), func=('geq', T3))
          .map(keys=('ipv4.dstIP',))
          )

    queries = [q3]

    config["final_plan"] = [(1, 32, 4), (2, 32, 4)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config,queries,os.path.dirname(os.path.realpath(__file__)))