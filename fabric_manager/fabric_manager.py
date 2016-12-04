#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)


import logging

logging.getLogger(__name__)
from multiprocessing.connection import Listener
import pickle

from switch_config.utils import *
from switch_config.interfaces import Interfaces
from switch_config.compile_p4 import compile_p4_2_json
from switch_config.initialize_switch import initialize_switch



class FabricManagerConfig(object):
    def __init__(self, fm_socket):
        self.p4_src = ''
        self.queries = []
        self.p4_commands = []
        self.fm_socket = fm_socket

    def start(self):
        logging.info("fm_manager: Starting")
        self.fm_listener = Listener(self.fm_socket)
        while True:
            conn = self.fm_listener.accept()
            raw_data = conn.recv()
            message = pickle.loads(raw_data)
            for key in message.keys():
                if key == "init":
                    for query in message[key]:
                        self.add_query(query)
                self.compile_init_config()
                logging.info("query compiled")
                logging.info("commands generated")

                with open(P4_COMPILED, 'w') as fp:
                    fp.write(self.p4_src)

                interfaces = { 'reciever': ['m-veth-1','out-veth-1'],
                               'sender': ['m-veth-2','out-veth-2']}

                for key in interfaces.keys():
                    inter = Interfaces(interfaces[key][0],interfaces[key][1])
                    inter.setup()

                compile_p4_2_json()

                initialize_switch(SWITCH_PATH, JSON_P4_COMPILED, THRIFTPORT,
                                  CLI_PATH, self.p4_commands)


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

        out += 'control ingress {\n\t'
        for q in self.queries:
            out += q.p4_control
        out += '}\n\n'
        out += 'control egress {\n\t'
        for q in self.queries:
            out += 'apply(encap_'+str(q.qid)+');'

        out += '\n}\n\n'
        self.p4_src = out

        for q in self.queries:
            self.p4_commands.extend(q.p4_init_commands)

        return out


"""
fm = FabricManagerConfig()
q1 = PacketStream(1).distinct(keys = ('sIP', 'dIP'))
q2 = PacketStream(2).reduce(keys= ('dIP',))
#q3 = PacketStream(fm.gc).distinct(keys = ('sIP', 'dIP')).reduce(keys= ('dIP',))


fm.add_query(q1)
fm.add_query(q2)
queries = fm.compile_init_config()



print str(fm.p4_commands)


with open(P4_COMPILED, 'w') as fp:
    fp.write(fm.p4_src)

interfaces = { 'reciever': ['m-veth-1','out-veth-1'],
               'sender': ['m-veth-2','out-veth-2']}

for key in interfaces.keys():
    inter = Interfaces(interfaces[key][0],interfaces[key][1])
    inter.setup()

compile_p4_2_json()

initialize_switch(SWITCH_PATH, JSON_P4_COMPILED, THRIFTPORT, CLI_PATH, fm.p4_commands)
"""