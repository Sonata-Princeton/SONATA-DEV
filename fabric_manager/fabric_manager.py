#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import logging
logging.getLogger(__name__)
from multiprocessing.connection import Listener
from switch_config.utils import *
from switch_config.interfaces import Interfaces
from switch_config.compile_p4 import compile_p4_2_json
from switch_config.initialize_switch import initialize_switch
import pickle


class FabricManagerConfig(object):
    def __init__(self, fm_socket):
        self.p4_src = ''
        self.queries = []
        self.id_2_query = {}
        self.p4_init_commands = []
        self.fm_socket = fm_socket
        self.interfaces = {'reciever': ['m-veth-1', 'out-veth-1'],
                           'sender': ['m-veth-2', 'out-veth-2']}

    def start(self):
        logging.info("fm_manager: Starting")
        self.fm_listener = Listener(self.fm_socket)
        while True:
            logging.debug("Listening again...")
            conn = self.fm_listener.accept()
            raw_data = conn.recv()
            message = pickle.loads(raw_data)
            for key in message.keys():
                if key == "init":

                elif key == "delta":
                    self.process_delta_config()
                else:
                    logging.error("Unsupported Command: " + key)

    def create_interfaces(self):
        for key in self.interfaces.keys():
            inter = Interfaces(self.interfaces[key][0], self.interfaces[key][1])
            inter.setup()

    def add_query(self, q):
        self.queries.append(q)
        self.id_2_query[q.qid] = q

    def process_init_config(self):
        # Process initial config from RT
        for query in message[key]:
            self.add_query(query)
        self.compile_init_config()
        logging.info("query compiled")

        write_to_file(P4_COMPILED, self.p4_src)

        P4_COMMANDS_STR = "\n".join(self.p4_init_commands)

        write_to_file(P4_COMMANDS, P4_COMMANDS_STR)

        compile_p4_2_json()
        self.create_interfaces()
        cmd = SWITCH_PATH + " >/dev/null 2>&1"
        logging.info(cmd)
        get_out(cmd)
        initialize_switch(SWITCH_PATH, JSON_P4_COMPILED, THRIFTPORT,
                          CLI_PATH)

    def process_delta_config(self):
        logging.info("Sending deltas to Data Plane")
        #send_commands_to_dp(CLI_PATH, JSON_P4_COMPILED, THRIFTPORT, self.p4_init_commands)
        for qid in message_key:
            query = self.id_2_query[qid]
            filter_name = 'filter_'+str(query.qid)+'_'+str(query.filter_rules_id)
            for elem in 
        return 0

    def receive_configs(self):
        # Receive configs from Runtime
        return 0

    def compile_delta_config(self):
        return 0

    def compile_init_config(self):
        # Compile the initial config to P4 source code and json output

        logging.info("FM: Compilation....")

        out = ''
        for q in self.queries:
            q.compile_pipeline()

        out += self.queries[0].p4_invariants

        # Define the intrinsic metadata to specfiy recirculate flag
        out += 'header_type intrinsic_metadata_t {\n'
        out += '\tfields {\n\trecirculate_flag : 16;}\n}\n\n'
        out += 'metadata intrinsic_metadata_t intrinsic_metadata;\n\n'

        out += 'field_list recirculate_fields {\n'
        out += '\tstandard_metadata;\n\tmeta_fm;\n}\n\n'

        out += 'action do_recirculate_to_ingress() {\n'
        out += '\tadd_to_field(meta_fm.f1, 1);\n'
        out += '\trecirculate(recirculate_fields);\n}\n\n'

        out += 'table recirculate_to_ingress {\n'
        out += '\tactions { do_recirculate_to_ingress; }\n'
        out += '\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default recirculate_to_ingress do_recirculate_to_ingress')


        out += 'table drop_table {\n\tactions {_drop;}\n\tsize : 1;\n}\n\n'
        out += 'table drop_packets {\n\tactions {_drop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default drop_table _drop')
        self.p4_init_commands.append('table_set_default drop_packets _drop')

        out += 'action mark_drop() {\n'
        out += '\tmodify_field(meta_fm.is_drop, 1);\n}\n\n'

        # Update the initial P4 commands
        for q in self.queries:
            self.p4_init_commands += q.p4_init_commands


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

        out += 'header_type meta_fm_t {\n\tfields {\n'
        for q in self.queries:
            out += '\t\tqid_'+str(q.qid)+' : 1;\n'
        out += '\t\tf1 : 8;\n'
        out += '\t\tis_drop : 1;\n'
        out += '\t}\n}\n\nmetadata meta_fm_t meta_fm;\n\n'

        out += 'action init_meta_fm() {\n'
        for q in self.queries:
            out += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 1);\n'
        out += '\tmodify_field(meta_fm.is_drop, 0);\n'
        out += '}\n\n'

        out += 'table init_meta_fm {\n'
        out += '\tactions {init_meta_fm;}\n'
        out += '\tsize: 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default init_meta_fm init_meta_fm')

        for q in self.queries:
            out += 'action set_meta_fm_'+str(q.qid)+'(){\n'
            out += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 1);\n'
            out += '}\n\n'

        for q in self.queries:
            out += 'action reset_meta_fm_'+str(q.qid)+'(){\n'
            out += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 0);\n'
            out += '}\n\n'

        for q in self.queries:
            out += q.filter_rules

        out += 'control ingress {\n'
        out += '\tapply(init_meta_fm);\n'
        for q in self.queries:
            out += '\tif (meta_fm.f1 == '+str(q.qid-1)+'){\n'
            out += q.filter_control
            out += '\t\tif (meta_fm.qid_'+str(q.qid)+' == 1){\n'
            out += '\t\t'+q.p4_ingress_start
            out += q.p4_control
            out += '\t\t\tapply(copy_to_cpu_'+str(q.qid)+');\n'
            out += '\t\t}\n\t}\n'
            self.p4_init_commands.append('table_set_default copy_to_cpu_'+str(q.qid)+' do_copy_to_cpu_'+str(q.qid))
        out += '}\n\n'

        out += 'control egress {\n'
        out += '\tif (standard_metadata.instance_type != 1) {\n'
        out += '\t\tif(meta_fm.f1 < '+str(len(self.queries))+') {\n'
        out += '\t\t\tapply(recirculate_to_ingress);\n\t\t}\n'
        out += '\t\telse {\n\t\t\tapply(drop_table);\n\t\t}\n\t}\n\n'
        out += '\telse if (standard_metadata.instance_type == 1) {\n'
        out += '\t\tif (meta_fm.is_drop == 1){\n'
        out += '\t\t\tapply(drop_packets);\n\t\t}\n\t\telse {\n'
        for q in self.queries:
            out += '\t\t\tif (meta_fm.f1 == '+str(q.qid-1)+'){\n'
            out += '\t\t\t\tapply(encap_'+str(q.qid)+');\n\t\t\t}\n'
            self.p4_init_commands.append('table_set_default encap_'+str(q.qid)+' do_encap_'+str(q.qid))
        out += '\t\t}\n\n'

        out += '\n\t}\n}\n\n'

        for q in self.queries:
            self.p4_init_commands.append('mirroring_add '+str(q.mirror_id)+' 12')
        self.p4_src = out
