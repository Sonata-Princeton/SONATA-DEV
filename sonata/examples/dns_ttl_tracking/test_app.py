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

    # Normally ttl is only 1 value
    # but if it is an attack it will keep changing.

    dns_ttl = (PacketStream(1)
               .filter(filter_keys=('ipv4.protocol',), func=('eq', 17))
               .filter(filter_keys=('udp.sport',), func=('eq', 53))
               .filter(filter_keys=('dns.ancount',), func=('geq', 1))
               .map(keys=('dns.an.rrname', 'dns.an.ttl'))
               .distinct(keys=('dns.an.rrname', 'dns.an.ttl'))
               .map(keys=('dns.an.rrname',), map_values=('count',), func=('set', 1,))
               .reduce(keys=('dns.an.rrname',), func=('sum',))
               .filter(filter_vals=('count',), func=('geq', 40))
               .map(keys=('dns.an.rrname',))
               )

    queries = [dns_ttl]
    config["final_plan"] = [(1, 32, 2)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
