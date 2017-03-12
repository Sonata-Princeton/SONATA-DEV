#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import logging
import pickle
import time
from multiprocessing.connection import Listener
from threading import Thread

from sonata.dataplane_driver.emitter.emitter import Emitter
from switch_config.compile_p4 import compile_p4_2_json
from switch_config.initialize_switch import initialize_switch
from switch_config.interfaces import Interfaces
from switch_config.utils import *


class DPDriverConfig(object):
    def __init__(self, fm_conf, em_conf):
        self.p4_src = ''
        self.queries = []
        self.id_2_query = {}
        self.p4_init_commands = []
        self.fm_socket = fm_conf['fm_socket']
        self.em_conf = em_conf

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(fm_conf['log_file'])
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

        self.reset_bool = False
        self.interfaces = {'reciever': ['m-veth-1', 'out-veth-1'],
                           'sender': ['m-veth-2', 'out-veth-2']}
        self.em_thread = Thread(name='emitter', target=self.start_emitter)

    def start(self):
        self.fm_listener = Listener(self.fm_socket)
        while True:
            start = time.time()
            conn = self.fm_listener.accept()
            raw_data = conn.recv()
            message = pickle.loads(raw_data)
            for key in message.keys():
                if key == "init":
                    self.process_init_config(message[key])
                    self.logger.info("fabric_manager,init,"+str(start)+","+ str(time.time()))
                elif key == "delta":
                    self.logger.info("fabric_manager,delta_in,"+str(start)+","+ str(time.time()))
                    self.process_delta_config(message[key])
                    self.logger.info("fabric_manager,delta_out,"+str(start)+","+ str(time.time()))
                else:
                    print "ERROR Unsupported Key"

    def start_emitter(self):
        # Start the packet parser
        em = Emitter(self.em_conf, self.queries)
        em.start()
        while True:
            time.sleep(5)
        return 0

    def create_interfaces(self):
        for key in self.interfaces.keys():
            inter = Interfaces(self.interfaces[key][0], self.interfaces[key][1])
            inter.setup()

    def add_query(self, q):
        self.queries.append(q)
        self.id_2_query[q.qid] = q

    def process_init_config(self, message):
        # Process initial config from RT
        for queryID in message:
            self.add_query(message[queryID])
        self.compile_init_config()
        print "FM: Received ", len(self.queries), " queries from Runtime"

        write_to_file(P4_COMPILED, self.p4_src)

        P4_COMMANDS_STR = "\n".join(self.p4_init_commands)

        write_to_file(P4_COMMANDS, P4_COMMANDS_STR)

        compile_p4_2_json()
        self.create_interfaces()
        cmd = SWITCH_PATH + " >/dev/null 2>&1"
        get_out(cmd)
        initialize_switch(SWITCH_PATH, JSON_P4_COMPILED, THRIFTPORT,
                          CLI_PATH)

        # Start packet parser (tuple emmiter)
        self.em_thread.start()

    def reset_switch(self):
        reset_switch_state()
        # Sending initial commands after reset
        send_commands_to_dp(CLI_PATH, P4_COMPILED, THRIFTPORT, P4_COMMANDS)

    def process_delta_config(self, message):
        commands = ''
        # Reset the data plane registers/tables before pushing the new delta config
        start = time.time()
        self.reset_switch()
        self.logger.info("fabric_manager,delta_reset,"+str(start)+","+ str(time.time()))

        for (qid,filter_id) in message:
            start = time.time()
            query = self.id_2_query[qid]
            filter_operator = query.src_2_filter_operator[filter_id]
            filter_mask = filter_operator.filter_mask
            filter_table_fname = filter_operator.operator_name
            print "Message received:", message[(qid,filter_id)]

            for dip in message[(qid,filter_id)]:
                dip = dip.strip('\n')
                print "dIP:",dip
                command = 'table_add '+filter_table_fname+' set_meta_fm_'+str(qid)+' '+str(dip)+'/'+str(filter_mask)+' => \n'
                commands += command
                print "Added command ", qid, command

            write_to_file(P4_DELTA_COMMANDS, commands)
            send_commands_to_dp(CLI_PATH, JSON_P4_COMPILED, THRIFTPORT, P4_DELTA_COMMANDS)
            self.logger.info("fabric_manager,delta_compute_push,"+str(start)+","+ str(time.time()))

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
            out += '\tmodify_field(meta_fm.is_drop, 1);\n'
            out += '}\n\n'

        for q in self.queries:
            out += q.filter_rules

        out += 'control ingress {\n'
        out += '\tapply(init_meta_fm);\n'
        ctr = 0
        for q in self.queries:
            out += '\tif (meta_fm.f1 == '+str(ctr)+'){\n'
            ctr += 1
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
        ctr = 0
        for q in self.queries:
            out += '\t\t\tif (meta_fm.f1 == '+str(ctr)+'){\n'
            ctr += 1
            out += '\t\t\t\tapply(encap_'+str(q.qid)+');\n\t\t\t}\n'
            self.p4_init_commands.append('table_set_default encap_'+str(q.qid)+' do_encap_'+str(q.qid))
        out += '\t\t}\n\n'

        out += '\n\t}\n}\n\n'

        for q in self.queries:
            self.p4_init_commands.append('mirroring_add '+str(q.mirror_id)+' 12')
        self.p4_src = out

if __name__ == "__main__":
    blah = 1
