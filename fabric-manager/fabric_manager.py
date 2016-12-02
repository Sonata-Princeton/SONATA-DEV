#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

class FabricManagerConfig(object):
    def __init__(self):
        self.p4_src = ''
        self.queries = []

    def add_query(self, q):
        self.queries.append(q)

    def compile_dp(self):
        out = ''
        for q in self.queries:
            q.compile_dp()

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

        out += 'control ingress {\n\t'
        for q in self.queries:
            out += q.p4_control
        out += '}\n\n'
        out += 'control egress {\n\t'
        for q in self.queries:
            out += 'apply(encap_'+str(q.qid)+');'

        out += '\n}\n\n'
        self.p4_src = out
        return out

fm = FabricManagerConfig()
q1 = PacketStream(1).distinct(keys = ('sIP', 'dIP'))
q2 = PacketStream(2).reduce(keys= ('dIP',))
#q3 = PacketStream(fm.gc).distinct(keys = ('sIP', 'dIP')).reduce(keys= ('dIP',))



#fm.add_query(q1)
fm.add_query(q2)
fm.compile_dp()
