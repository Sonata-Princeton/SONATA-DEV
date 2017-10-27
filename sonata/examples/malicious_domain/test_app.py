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

    # Ip --> Domain anomaly
    # Number of distinct IP addresses per domain name
    ip_2_domain = (PacketStream(1)
                   .filter(filter_keys=('udp.sport',), func=('eq', 53))
                   .map(keys=('dns.an.rdata', 'dns.an.rrname'))
                   .distinct(keys=('dns.an.rdata', 'dns.an.rrname'))
                   .map(keys=('dns.an.rdata',), map_values=('count',), func=('set', 1,))
                   .reduce(keys=('dns.an.rdata',), func=('sum',))
                   .filter(filter_vals=('count',), func=('geq', T))
                   .map(keys=('dns.an.rdata',))
                   )

    # Domain ---> IP anomaly
    # Number of domains that share the same IP addresses
    domain_2_ip = (PacketStream(2)
                   .filter(filter_keys=('udp.sport',), func=('eq', 53))
                   .map(keys=('dns.an.rdata', 'dns.an.rrname'))
                   .distinct(keys=('dns.an.rdata', 'dns.an.rrname'))
                   .map(keys=('dns.an.rrname',), map_values=('count',), func=('set', 1,))
                   .reduce(keys=('dns.an.rrname',), func=('sum',))
                   .filter(filter_vals=('count',), func=('geq', T))
                   .map(keys=('dns.an.rrname',))
                   )

    queries = [ip_2_domain]
    config["final_plan"] = [(1, 32, 2)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
