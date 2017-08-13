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
        print(data)

    config = data["on_server"][data["is_on_server"]]["sonata"]
    T = 40

    # Normally ttl is only 1 value
    # but if it is an attack it will keep changing.

    dns_ttl = (PacketStream(1)
               .filter(filter_keys=('ipv4.proto',), func=('eq', 17))
               .filter(filter_keys=('udp.sport',), func=('eq', 53))
               .filter(filter_keys=('dns.qdcount',), func=('geq', 1))
               .map(keys=('dns.qd.qname', 'dns.qd.ttl'))s
               .distinct(keys=('dns.qd.qname', 'dns.qd.ttl'))
               .map(keys=('dns.qd.qname',), map_values=('count',), func=('eq', 1,))
               .reduce(keys=('dns.qd.qname',), func=('sum',))
               .filter(filter_vals=('count',), func=('geq', T))
               .map(keys=('dns.qd.qname',))
               )

    queries = [dns_ttl]

    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
