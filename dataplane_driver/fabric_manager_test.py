#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine.p4_queries import QueryPipeline

class FabricManagerConfig(object):
    def __init__(self):
        self.p4_src = ''
        self.p4_init_commands = []
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


fm = FabricManagerConfig()
#q1 = PacketStream(1).filter(keys = ('proto',),values = ('17',)).distinct(keys = ('sIP', 'dIP/16'))
#q1 = QueryPipeline(1).filter(keys = ('proto',),values = ('6',)).filter(keys = ('dIP',),values = ('112.7.186.25',)).distinct(keys = ('sIP', 'dIP'))
#q2 = QueryPipeline(2).reduce(keys= ('dIP',))
#q3 = QueryPipeline(3).reduce(keys= ('dIP',))
#q4 = QueryPipeline(3).distinct(keys = ('sIP', 'dIP')).reduce(keys= ('dIP',))

q5 = QueryPipeline(1).map_init(keys=('dIP','sIP', 'proto')).map(keys = ('dIP',), func=('mask',16)).distinct(keys= ('dIP','sIP'))
q6 = QueryPipeline(2).map_init(keys=('dIP','sIP', 'proto')).map(keys = ('dIP',), func=('mask',16)).reduce(keys= ('dIP',))
fm.add_query(q5)
#fm.add_query(q6)
#fm.add_query(q2)
fm.compile_init_config()

#print fm.p4_src
example_dir = '/home/vagrant/dev/examples/multi_query_test'

with open(example_dir+'/commands.txt', 'w') as f:
    line = ''
    for cmd in fm.p4_init_commands:
        line += cmd+'\n'
    line = line[:-1]
    f.write(line)

with open(example_dir+'/p4src/test.p4', 'w') as f:
    line = fm.p4_src
    line = line[:-1]
    f.write(line)
