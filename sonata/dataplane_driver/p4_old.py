#!/usr/bin/env python


from p4_queries import QueryPipeline


class P4Target(object):
    def __init__(self):
        self.p4_commands = list()
        self.p4_src = ''

    def compile_app(self, app):
        # Transform general DP application to list of P4 query pipelines
        p4_queries = list()
        for query_object in app:
            query_pipeline = QueryPipeline(query_object.id)

            # Set Parse Payload
            query_pipeline.parse_payload = query_object.parse_payload

            for operator in query_object.operators:

                # filter payload from keys
                keys = filter(lambda x: x != 'payload', operator.keys)

                if operator.name == 'map_init':
                    query_pipeline.map_init(keys)
                elif operator.name == 'Filter':
                    # TODO: get rid of this hardcoding
                    if operator.func[0] != 'geq':
                        query_pipeline.filter(keys=keys,
                                              filter_keys=operator.filter_keys,
                                              func=operator.func,
                                              src=operator.src)
                elif operator['name'] == "Map":
                    query_pipeline.map(keys=keys,
                                       map_keys=operator.map_keys,
                                       func=operator.func)
                elif operator['name'] == "Reduce":
                    query_pipeline.reduce(keys=keys)

                elif operator['name'] == "Distinct":
                    query_pipeline.distinct(keys=keys)

            p4_queries.append(query_pipeline)

        # Compile all the query pipelines to P4 source code
        commands = list()

        out = ''
        for q in p4_queries:
            q.compile_pipeline()

        out += p4_queries[0].p4_invariants

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
        commands.append('table_set_default recirculate_to_ingress do_recirculate_to_ingress')

        out += 'table drop_table {\n\tactions {_drop;}\n\tsize : 1;\n}\n\n'
        out += 'table drop_packets {\n\tactions {_drop;}\n\tsize : 1;\n}\n\n'
        commands.append('table_set_default drop_table _drop')
        commands.append('table_set_default drop_packets _drop')

        out += 'action mark_drop() {\n'
        out += '\tmodify_field(meta_fm.is_drop, 1);\n}\n\n'

        # Update the initial P4 commands
        for q in p4_queries:
            commands += q.p4_init_commands

        out += 'parser parse_out_header {\n\t'
        for q in p4_queries:
            out += 'extract(out_header_'+str(q.qid)+');\n\t'

        out += 'return parse_ethernet;\n}\n\n'

        for q in p4_queries:
            out += q.p4_egress
        for q in p4_queries:
            out += q.p4_utils
        for q in p4_queries:
            out += q.p4_state

        out += 'header_type meta_fm_t {\n\tfields {\n'
        for q in p4_queries:
            out += '\t\tqid_'+str(q.qid)+' : 1;\n'
        out += '\t\tf1 : 8;\n'
        out += '\t\tis_drop : 1;\n'
        out += '\t}\n}\n\nmetadata meta_fm_t meta_fm;\n\n'

        out += 'action init_meta_fm() {\n'
        for q in p4_queries:
            out += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 1);\n'
        out += '\tmodify_field(meta_fm.is_drop, 0);\n'
        out += '}\n\n'

        out += 'table init_meta_fm {\n'
        out += '\tactions {init_meta_fm;}\n'
        out += '\tsize: 1;\n}\n\n'
        commands.append('table_set_default init_meta_fm init_meta_fm')

        for q in p4_queries:
            out += 'action set_meta_fm_'+str(q.qid)+'(){\n'
            out += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 1);\n'
            out += '}\n\n'

        for q in p4_queries:
            out += 'action reset_meta_fm_'+str(q.qid)+'(){\n'
            out += '\tmodify_field(meta_fm.qid_'+str(q.qid)+', 0);\n'
            out += '\tmodify_field(meta_fm.is_drop, 1);\n'
            out += '}\n\n'

        for q in p4_queries:
            out += q.filter_rules

        out += 'control ingress {\n'
        out += '\tapply(init_meta_fm);\n'
        ctr = 0
        for q in p4_queries:
            out += '\tif (meta_fm.f1 == '+str(ctr)+'){\n'
            ctr += 1
            out += q.filter_control
            out += '\t\tif (meta_fm.qid_'+str(q.qid)+' == 1){\n'
            out += '\t\t'+q.p4_ingress_start
            out += q.p4_control
            out += '\t\t\tapply(copy_to_cpu_'+str(q.qid)+');\n'
            out += '\t\t}\n\t}\n'
            commands.append('table_set_default copy_to_cpu_'+str(q.qid)+' do_copy_to_cpu_'+str(q.qid))
        out += '}\n\n'

        out += 'control egress {\n'
        out += '\tif (standard_metadata.instance_type != 1) {\n'
        out += '\t\tif(meta_fm.f1 < '+str(len(p4_queries))+') {\n'
        out += '\t\t\tapply(recirculate_to_ingress);\n\t\t}\n'
        out += '\t\telse {\n\t\t\tapply(drop_table);\n\t\t}\n\t}\n\n'
        out += '\telse if (standard_metadata.instance_type == 1) {\n'
        out += '\t\tif (meta_fm.is_drop == 1){\n'
        out += '\t\t\tapply(drop_packets);\n\t\t}\n\t\telse {\n'
        ctr = 0
        for q in p4_queries:
            out += '\t\t\tif (meta_fm.f1 == '+str(ctr)+'){\n'
            ctr += 1
            out += '\t\t\t\tapply(encap_'+str(q.qid)+');\n\t\t\t}\n'
            commands.append('table_set_default encap_'+str(q.qid)+' do_encap_'+str(q.qid))
        out += '\t\t}\n\n'

        out += '\n\t}\n}\n\n'

        for q in p4_queries:
            commands.append('mirroring_add '+str(q.mirror_id)+' 12')
        self.p4_src = out
        self.p4_commands = commands

    def send_commands_to_dataplane(self):
