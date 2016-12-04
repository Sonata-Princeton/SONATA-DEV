#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
from query_engine.p4_queries import PacketStream

class FabricManagerConfig(object):
    def __init__(self):
        self.p4_src = ''
        self.queries = []

    def add_query(self, q):
        self.queries.append(q)

    def process_init_config(self):
        # Process initial config from RT
        return 0

    def process_delta_config(self):
        # Process delta config from RT
        return 0

    def receive_configs(self):
        # Receive configs from Runtime
        return 0

    def compile_delta_config(self):
        return 0

    def compile_init_config(self):
        # Compile the initial config to P4 source code and json output
        out = ''
        for q in self.queries:
            q.compile_pipeline()

        out += self.queries[0].p4_invariants

        out += 'parser parse_out_header {\n\t'
        for q in self.queries:
            out += 'extract(out_header_'+str(q.qid)+');\n\t'

        out += 'return parse_ethernet;\n}\n\n'

        for q in self.queries:
            out += q.p4_egress
        for q in self.queries:
            out += q.p4_utils
        for q in self.queries:
            out += q.p4_state

        out += 'control ingress {\n'
        for q in self.queries:
            out += q.p4_ingress_start
            out += '\tif ('+q.operators[0].metadata_name+'.qid == '+str(q.qid)+'){\n'
            out += q.p4_control+'\n'
            out += '\t}\n\n'
        out += '}\n\n'
        out += 'control egress {\n'
        for q in self.queries:
            out += '\tif ('+q.operators[0].metadata_name+'.qid == '+str(q.qid)+'){\n'
            out += '\t\tapply(encap_'+str(q.qid)+');\n'
            out += '\t}\n'

        out += '\n}\n\n'
        self.p4_src = out
        return out

fm = FabricManagerConfig()
q1 = PacketStream(1).distinct(keys = ('sIP', 'dIP'))
q2 = PacketStream(2).reduce(keys= ('dIP',))
q3 = PacketStream(3).distinct(keys = ('sIP', 'dIP')).reduce(keys= ('dIP',))


fm.add_query(q1)
#fm.add_query(q2)
#fm.add_query(q3)
fm.compile_init_config()

print fm.p4_src
