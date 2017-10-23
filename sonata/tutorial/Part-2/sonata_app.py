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
    Th1 = 10
    Th2 = 2

    host_send = (PacketStream(1)
                 .filter(filter_keys=('ipv4.protocol',), func=('eq', 17))
                 .filter(filter_keys=('udp.sport',), func=('eq', 53))
                  ## Add code here
                 .filter(filter_vals=('count',), func=('geq', Th1))
                 )

    host_receive = (PacketStream(2)
                    .filter(filter_keys=('ipv4.protocol',), func=('eq', 17))
                    .filter(filter_keys=('udp.sport',), func=('eq', 53))
                    .map(keys=('ipv4.dstIP', 'dns.an.rdata',))
                     ## Add code here
                    .filter(filter_vals=('count',), func=('leq', Th2))
                    )

    iot_hosts = (host_send
                 .join(window='Same', new_qid=3, query=host_receive)
                 .map(keys=('ipv4.dstIP',))
                 )

    queries = [iot_hosts]
    config["final_plan"] = [(1, 32, 4, 1), (2, 32, 2, 1)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config,
                      queries,
                      os.path.dirname(os.path.realpath(__file__))
                      )
