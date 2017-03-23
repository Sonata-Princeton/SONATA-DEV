#!/usr/bin/env python

import logging

from threading import Thread

from p4_queries import QueryPipeline
from emitter.emitter_old import Emitter
from p4_dataplane import P4DataPlane
from utils import write_to_file

from collections import namedtuple


Operator = namedtuple('Operator', 'name keys')


class P4Target(object):
    def __init__(self, em_conf, target_conf):
        self.em_conf = em_conf

        # Code Compilation
        self.COMPILED_SRCS = target_conf['compiled_srcs']
        self.JSON_P4_COMPILED = self.COMPILED_SRCS + target_conf['json_p4_compiled']
        self.P4_COMPILED = self.COMPILED_SRCS + target_conf['p4_compiled']
        self.P4C_BM_SCRIPT = target_conf['p4c_bm_script']

        # Initialization of Switch
        self.BMV2_PATH = target_conf['bmv2_path']
        self.BMV2_SWITCH_BASE = self.BMV2_PATH + target_conf['bmv2_switch_base']

        self.SWITCH_PATH = self.BMV2_SWITCH_BASE + target_conf['switch_path']
        self.CLI_PATH = self.BMV2_SWITCH_BASE + target_conf['cli_path']
        self.THRIFTPORT = target_conf['thriftport']

        self.P4_COMMANDS = self.COMPILED_SRCS + target_conf['p4_commands']
        self.P4_DELTA_COMMANDS = self.COMPILED_SRCS + target_conf['p4_delta_commands']

        # interfaces
        self.interfaces = {
                'receiver': ['m-veth-1', 'out-veth-1'],
                'sender': ['m-veth-2', 'out-veth-2']
        }

        self.supported_operations = ['Map', 'Filter', 'Reduce', 'Distinct']

        # LOGGING
        log_level = logging.DEBUG
        # add handler
        self.logger = logging.getLogger('P4Target')
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info('init')

        # init dataplane
        self.dataplane = P4DataPlane(self.interfaces, self.SWITCH_PATH, self.CLI_PATH, self.THRIFTPORT, self.P4C_BM_SCRIPT)

        # query object
        self.queries = dict()

    def get_supported_operators(self):
        return self.supported_operations

    def compile_app(self, app):
        # Transform general DP application to list of P4 query pipelines
        p4_queries = list()
        for qid in app:
            print app[qid]
            self.logger.debug('create query pipeline for qid: %i' % (qid, ))
            query_pipeline = QueryPipeline(qid)

            # Set Parse Payload
            query_pipeline.parse_payload = app[qid].parse_payload

            # Add map init
            keys = set()
            for operator in app[qid].operators:
                if operator.name in {'Filter', 'Map', 'Reduce', 'Distinct'}:
                    keys = keys.union(set(operator.keys))
            if 'payload' in keys:
                keys.remove('payload')
            if 'count' in keys:
                keys.remove('count')
            if 'ts' in keys:
                keys.remove('ts')

            self.logger.debug('add map_init with keys: %s' % (', '.join(keys), ))
            query_pipeline.map_init(keys=keys)

            for operator in app[qid].operators:
                self.logger.debug('add %s operator' % (operator.name, ))
                # filter payload from keys
                keys = filter(lambda x: x != 'payload' and x != 'ts', operator.keys)

                if operator.name == 'Filter':
                    # TODO: get rid of this hardcoding
                    if operator.func[0] != 'geq':
                        query_pipeline.filter(keys=keys,
                                              filter_keys=operator.filter_keys,
                                              func=operator.func,
                                              src=operator.src)
                elif operator.name == 'Map':
                    if len(operator.func) > 0 and operator.func[0] == 'mask':
                        query_pipeline.map(keys=keys,
                                           map_keys=operator.map_keys,
                                           func=operator.func)
                elif operator.name == 'Reduce':
                    query_pipeline.reduce(keys=keys)

                elif operator.name == 'Distinct':
                    query_pipeline.distinct(keys=keys)

            p4_queries.append(query_pipeline)
            self.queries[qid] = query_pipeline

        # Compile all the query pipelines to P4 source code
        p4_commands = list()

        self.logger.debug('generate p4 code')
        p4_src = ''
        for q in p4_queries:
            q.compile_pipeline()

        p4_src += p4_queries[0].p4_invariants

        # Define the intrinsic metadata to specfiy recirculate flag
        p4_src += 'header_type intrinsic_metadata_t {\n'
        p4_src += '\tfields {\n\trecirculate_flag : 16;}\n}\n\n'
        p4_src += 'metadata intrinsic_metadata_t intrinsic_metadata;\n\n'

        p4_src += 'field_list recirculate_fields {\n'
        p4_src += '\tstandard_metadata;\n\tmeta_fm;\n}\n\n'

        p4_src += 'action do_recirculate_to_ingress() {\n'
        p4_src += '\tadd_to_field(meta_fm.f1, 1);\n'
        p4_src += '\trecirculate(recirculate_fields);\n}\n\n'

        p4_src += 'table recirculate_to_ingress {\n'
        p4_src += '\tactions { do_recirculate_to_ingress; }\n'
        p4_src += '\tsize : 1;\n}\n\n'
        p4_commands.append('table_set_default recirculate_to_ingress do_recirculate_to_ingress')

        p4_src += 'table drop_table {\n\tactions {_drop;}\n\tsize : 1;\n}\n\n'
        p4_src += 'table drop_packets {\n\tactions {_drop;}\n\tsize : 1;\n}\n\n'
        p4_commands.append('table_set_default drop_table _drop')
        p4_commands.append('table_set_default drop_packets _drop')

        p4_src += 'action mark_drop() {\n'
        p4_src += '\tmodify_field(meta_fm.is_drop, 1);\n}\n\n'

        # Update the initial P4 commands
        for q in p4_queries:
            p4_commands += q.p4_init_commands

        p4_src += 'parser parse_out_header {\n\t'
        for q in p4_queries:
            p4_src += 'extract(out_header_'+str(q.qid)+');\n\t'

        p4_src += 'return parse_ethernet;\n}\n\n'

        for q in p4_queries:
            p4_src += q.p4_egress
        for q in p4_queries:
            p4_src += q.p4_utils
        for q in p4_queries:
            p4_src += q.p4_state

        p4_src += 'header_type meta_fm_t {\n\tfields {\n'
        for q in p4_queries:
            p4_src += '\t\tqid_'+str(q.qid)+' : 1;\n'
        p4_src += '\t\tf1 : 8;\n'
        p4_src += '\t\tis_drop : 1;\n'
        p4_src += '\t}\n}\n\nmetadata meta_fm_t meta_fm;\n\n'

        p4_src += 'action init_meta_fm() {\n'
        for q in p4_queries:
            p4_src += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 1);\n'
        p4_src += '\tmodify_field(meta_fm.is_drop, 0);\n'
        p4_src += '}\n\n'

        p4_src += 'table init_meta_fm {\n'
        p4_src += '\tactions {init_meta_fm;}\n'
        p4_src += '\tsize: 1;\n}\n\n'
        p4_commands.append('table_set_default init_meta_fm init_meta_fm')

        for q in p4_queries:
            p4_src += 'action set_meta_fm_'+str(q.qid)+'(){\n'
            p4_src += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 1);\n'
            p4_src += '}\n\n'

        for q in p4_queries:
            p4_src += 'action reset_meta_fm_'+str(q.qid)+'(){\n'
            p4_src += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 0);\n'
            p4_src += '\tmodify_field(meta_fm.is_drop, 1);\n'
            p4_src += '}\n\n'

        for q in p4_queries:
            p4_src += q.filter_rules

        p4_src += 'control ingress {\n'
        p4_src += '\tapply(init_meta_fm);\n'
        ctr = 0
        for q in p4_queries:
            p4_src += '\tif (meta_fm.f1 == '+str(ctr)+'){\n'
            ctr += 1
            p4_src += q.filter_control
            p4_src += '\t\tif (meta_fm.qid_'+str(q.qid)+' == 1){\n'
            p4_src += '\t\t'+q.p4_ingress_start
            p4_src += q.p4_control
            p4_src += '\t\t\tapply(copy_to_cpu_'+str(q.qid)+');\n'
            p4_src += '\t\t}\n\t}\n'
            p4_commands.append('table_set_default copy_to_cpu_'+str(q.qid)+' do_copy_to_cpu_'+str(q.qid))
        p4_src += '}\n\n'

        p4_src += 'control egress {\n'
        p4_src += '\tif (standard_metadata.instance_type != 1) {\n'
        p4_src += '\t\tif(meta_fm.f1 < '+str(len(p4_queries))+') {\n'
        p4_src += '\t\t\tapply(recirculate_to_ingress);\n\t\t}\n'
        p4_src += '\t\telse {\n\t\t\tapply(drop_table);\n\t\t}\n\t}\n\n'
        p4_src += '\telse if (standard_metadata.instance_type == 1) {\n'
        p4_src += '\t\tif (meta_fm.is_drop == 1){\n'
        p4_src += '\t\t\tapply(drop_packets);\n\t\t}\n\t\telse {\n'
        ctr = 0
        for q in p4_queries:
            p4_src += '\t\t\tif (meta_fm.f1 == '+str(ctr)+'){\n'
            ctr += 1
            p4_src += '\t\t\t\tapply(encap_'+str(q.qid)+');\n\t\t\t}\n'
            p4_commands.append('table_set_default encap_'+str(q.qid)+' do_encap_'+str(q.qid))
        p4_src += '\t\t}\n\n'

        p4_src += '\n\t}\n}\n\n'

        for q in p4_queries:
            p4_commands.append('mirroring_add '+str(q.mirror_id)+' 12')

        return p4_queries, p4_src, p4_commands

    def run(self, app):
        self.logger.info('run')
        # compile app to p4
        self.logger.info('generate p4 code and commands')
        p4_queries, p4_src, p4_commands = self.compile_app(app)
        write_to_file(self.P4_COMPILED, p4_src)

        commands_string = "\n".join(p4_commands)
        write_to_file(self.P4_COMMANDS, commands_string)

        # compile p4 to json
        self.logger.info('compile p4 code to json')
        self.dataplane.compile_p4(self.P4_COMPILED, self.JSON_P4_COMPILED)

        # initialize dataplane and run the configuration
        self.logger.info('initialize the dataplane with the json configuration')
        self.dataplane.initialize(self.JSON_P4_COMPILED, self.P4_COMMANDS)

        # start the emitter
        if self.em_conf:
            self.logger.info('start the emitter')
            em = Emitter(self.em_conf, p4_queries)
            em_thread = Thread(name='emitter', target=em.start)
            em_thread.setDaemon(True)
            em_thread.start()

    def update(self, filter_update):
        self.logger.info('update')
        commands = ''
        # Reset the data plane registers/tables before pushing the new delta config
        self.dataplane.reset_switch_state()

        for qid, filter_id in filter_update:
            query = self.queries[qid]
            filter_operator = query.src_2_filter_operator[filter_id]
            filter_mask = filter_operator.filter_mask
            filter_table_fname = filter_operator.operator_name

            for dip in filter_update[(qid,filter_id)]:
                dip = dip.strip('\n')
                command = 'table_add '+filter_table_fname+' set_meta_fm_'+str(qid)+' '+str(dip)+'/'+str(filter_mask)+' => \n'
                commands += command

            write_to_file(self.P4_DELTA_COMMANDS, commands)
            self.dataplane.send_commands(self.JSON_P4_COMPILED, self.P4_DELTA_COMMANDS)
