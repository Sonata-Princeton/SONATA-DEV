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
<<<<<<< HEAD
    T = 40
=======
    T = 1
>>>>>>> b83e2640160edda4f631dc95f71c54f1ba12c114

    # Normally ttl is only 1 value
    # but if it is an attack it will keep changing.

    dns_ttl = (PacketStream(1)
               .filter(filter_keys=('ipv4.proto',), func=('eq', 17))
               .filter(filter_keys=('udp.sport',), func=('eq', 53))
<<<<<<< HEAD
               .filter(filter_keys=('dns.qdcount',), func=('geq', 1))
               .map(keys=('dns.qd.qname', 'dns.qd.ttl'))
               .distinct(keys=('dns.qd.qname', 'dns.qd.ttl'))
               .map(keys=('dns.qd.qname',), map_values=('count',), func=('eq', 1,))
               .reduce(keys=('dns.qd.qname',), func=('sum',))
               .filter(filter_vals=('count',), func=('geq', T))
               .map(keys=('dns.qd.qname',))
=======
               .filter(filter_keys=('dns.ancount',), func=('geq', 1))
               .map(keys=('dns.an.rrname', 'dns.an.ttl'))
               .distinct(keys=('dns.an.rrname', 'dns.an.ttl'))
               .map(keys=('dns.an.rrname',), map_values=('count',), func=('eq', 1,))
               .reduce(keys=('dns.an.rrname',), func=('sum',))
               .filter(filter_vals=('count',), func=('geq', 40))
               .map(keys=('dns.an.rrname',))
>>>>>>> b83e2640160edda4f631dc95f71c54f1ba12c114
               )

    queries = [dns_ttl]
    config["final_plan"] = [(1, 32, 2, 1)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(config, queries)
