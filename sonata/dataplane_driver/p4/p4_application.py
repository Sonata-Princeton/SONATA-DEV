#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


from p4_elements import Action, MetaData, MirrorSession, FieldList, Table, Header
from p4_primitives import NoOp, CloneIngressPktToEgress, AddHeader, ModifyField
from p4_query import P4Query
from p4_layer import P4Layer, OutHeaders, P4RawFields, Ethernet
from p4_field import P4Field
from sonata.dataplane_driver.utils import get_logger
import logging

SERVER = False
ORIGINAL_PACKET = False

if SERVER:
    SENDER_PORT = 11
    RECIEVE_PORT = 10
else:
    SENDER_PORT = 11
    RECIEVE_PORT = 13

SESSION_ID = 8001
SPAN_PORT = 12


class P4Application(object):
    def __init__(self, app):
        # LOGGING
        log_level = logging.DEBUG
        self.logger = get_logger('P4Application', 'INFO')
        self.logger.setLevel(log_level)
        self.logger.info('init')

        # Define the root layer for raw packet
        self.root_layer = Ethernet()
        self.p4_raw_fields = P4RawFields(self.root_layer)

        # define the application metadata
        self.drop_meta_field = 'drop'
        self.satisfied_meta_field = 'satisfied'
        self.clone_meta_field = 'clone'

        self.mirror_session = None
        self.field_list = None

        self.final_header = None
        self.final_header_action = None
        self.final_header_table = None

        self.init_action = None
        self.init_action_table = None

        self.report_action = None
        self.report_action_table = None
        self.nop_action = None
        self.metadata = None
        self.queries = self.init_application(app)

    # INIT THE DATASTRUCTURE
    def init_application(self, app):
        queries = dict()

        # define final header
        # TODO: Use new p4 layer object
        tmp = OutHeaders("final_header")
        tmp.fields = [P4Field(tmp, "delimiter", "delimiter", 32)]
        self.final_header = tmp

        primitives = list()
        primitives.append(AddHeader(self.final_header.get_name()))
        primitives.append(ModifyField('%s.delimiter' % self.final_header.get_name(), 0))
        self.final_header_action = Action('do_add_final_header', primitives)

        self.final_header_table = Table('add_final_header', self.final_header_action.get_name(), [], None, 1)

        # define nop action
        self.nop_action = Action('_nop', NoOp())
        nop_name = self.nop_action.get_name()

        # app metadata
        fields = list()
        for query_id in app:
            fields.append(('%s_%i' % (self.drop_meta_field, query_id), 1))
            fields.append(('%s_%i' % (self.satisfied_meta_field, query_id), 1))
        fields.append((self.clone_meta_field, 1))
        self.metadata = MetaData('app_data', fields)
        meta_name = self.metadata.get_name()

        # action and table to init app metadata
        primitives = list()
        for field_name, _ in fields:
            primitives.append(ModifyField('%s.%s' % (self.metadata.get_name(), field_name), 0))
        self.init_action = Action('do_init_app_metadata', primitives)

        self.init_action_table = Table('init_app_metadata', self.init_action.get_name(), [], None, 1)

        # transforms queries
        for query_id in app:
            self.logger.debug('create query pipeline for qid: %i' % (query_id,))
            parse_payload = app[query_id].parse_payload
            operators = app[query_id].operators
            query = P4Query(query_id,
                            parse_payload,
                            operators,
                            nop_name,
                            '%s.%s' % (meta_name, self.drop_meta_field),
                            '%s.%s' % (meta_name, self.satisfied_meta_field),
                            '%s.%s' % (meta_name, self.clone_meta_field), self.p4_raw_fields)
            queries[query_id] = query

        # define mirroring session
        self.mirror_session = MirrorSession(SESSION_ID, SPAN_PORT)

        # define report action that clones the packet and sends it to the stream processor
        fields = [self.metadata.get_name()]
        for query in queries.values():
            fields.append(query.get_metadata_name())
        self.field_list = FieldList('report_packet', fields)

        self.report_action = Action('do_report_packet', CloneIngressPktToEgress(self.mirror_session.get_session_id(),
                                                                                self.field_list.get_name()))

        self.report_action_table = Table('report_packet', self.report_action.get_name(), [], None, 1)
        return queries

    # COMPILE THE CODE
    def get_p4_code(self):
        p4_src = ''

        # Get parser for raw headers (layers) that are specific to the fields used in Sonata queries
        p4_src += self.get_raw_parser_code()

        # P4 INVARIANTS
        p4_src += self.get_invariants()

        # OUT HEADER PARSER
        p4_src += self.get_out_header_parser()

        # APP METADATA, ACTIONS, FIELDLISTS, TABLES
        p4_src += self.get_app_code()

        # QUERY METADATA, HEADERS, TABLES AND ACTIONS
        p4_src += self.get_code()

        # get original packet repeat code
        if ORIGINAL_PACKET: p4_src += self.get_original_repeat_code()

        # INGRESS PIPELINE
        p4_src += self.get_ingress_pipeline()

        # EGRESS PIPELINE
        if ORIGINAL_PACKET:
            p4_src += "control egress { }"
        else:
            p4_src += self.get_egress_pipeline()

        return p4_src

    def get_invariants(self):
        # Call this from respective layer classes
        out = ''
        out += 'parser start {\n'
        out += '\treturn select(current(0, 64)) {\n'
        out += '\t\t0 : parse_out_header;\n'
        out += '\t\tdefault: parse_'+self.root_layer.name+';\n'
        out += '\t}\n'
        out += '}\n\n'
        return out

    def get_raw_parser_code(self):
        raw_layers = self.get_raw_layers()
        out = ""
        for layer in raw_layers:
            out += layer.get_header_specification_code()
            out += layer.get_parser_code(raw_layers)

        return out

    def get_raw_layers(self):
        raw_fields = set()
        for qid in self.queries:
            # all_fields.union(set(operator.get_init_keys()))
            raw_fields = raw_fields.union(self.queries[qid].all_fields)

        # TODO: get rid of this local fix. This won't be required after we fix the sonata query module
        # Start local fix
        local_fix = {'dMac': 'ethernet.dstMac', 'sIP': 'ipv4.dstIP', 'proto': 'ipv4.proto', 'sMac': 'ethernet.dstMac',
                     'nBytes': 'ipv4.totalLen', 'dPort': 'udp.sport', 'sPort': 'udp.sport', 'dIP': 'ipv4.srcIP'}
        raw_fields = [local_fix[x] for x in raw_fields]
        # End local fix

        raw_layers = self.p4_raw_fields.get_layers_for_fields(raw_fields)
        print raw_layers
        return raw_layers

    def get_out_header_parser(self):
        # This needs to be called from the header class itself
        out = ''
        out += 'parser parse_out_header {\n'
        for query in self.queries.values():
            out += '\textract(%s);\n' % query.out_header.get_name()
        out += '\t%s\n' % self.final_header.get_parser_code()
        out += '\treturn parse_ethernet;\n'
        out += '}\n\n'
        return out

    def get_app_code(self):
        out = ''
        out += self.init_action.get_code()
        out += self.init_action_table.get_code()
        out += self.metadata.get_code()
        out += self.nop_action.get_code()
        out += self.field_list.get_code()
        out += self.report_action.get_code()
        out += self.report_action_table.get_code()
        out += self.final_header.get_header_specification_code()
        out += self.final_header_action.get_code()
        out += self.final_header_table.get_code()
        return out

    def get_code(self):
        out = ''
        for query in self.queries.values():
            out += query.get_code()
        return out

    def get_original_repeat_code(self):
        original_repeat = """
action _drop() {
	drop();
}

action repeat(dport) {
    modify_field(standard_metadata.egress_spec, dport);
}

table forward {
    reads {
        standard_metadata.ingress_port: exact;
    }
    actions {
        repeat;
        _drop;
    }
    size: 2;
}\n"""
        return original_repeat

    def get_ingress_pipeline(self):
        out = ''
        out += 'control ingress {\n'
        out += '\tapply(%s);\n' % self.init_action_table.get_name()

        # add the control flow of one query after the other
        for query in self.queries.values():
            out += query.get_ingress_control_flow(2)

        out += '\n'

        # after processing all queries, determine whether the packet should be sent to the emitter as it satisfied at
        # least one query
        out += '\tif (%s.%s == 1) {\n' % (self.metadata.get_name(), self.clone_meta_field)
        out += '\t\tapply(%s);\n' % self.report_action_table.get_name()
        out += '\t}\n'

        if ORIGINAL_PACKET: out += '\tapply(forward);\n'

        out += '}\n\n'
        return out

    def get_egress_pipeline(self):
        out = ''
        out += 'control egress {\n'
        # normal forwarding of the original packet
        out += '\tif (standard_metadata.instance_type == 0) {\n'
        out += '\t\t// original packet, apply forwarding\n'
        out += '\t}\n\n'

        # adding header to the report packet which is sent to the emitter
        out += '\telse if (standard_metadata.instance_type == 1) {\n'
        for query in self.queries.values():
            out += query.get_egress_control_flow(2)
        out += '\t\tapply(%s);\n' % self.final_header_table.get_name()
        out += '\t}\n'
        out += '}\n\n'
        return out

    def get_commands(self):
        commands = list()
        for query in self.queries.values():
            commands += query.get_commands()
        commands.append(self.report_action_table.get_default_command())
        commands.append(self.final_header_table.get_default_command())
        commands.append(self.mirror_session.get_command())
        if ORIGINAL_PACKET:
            commands.append("table_set_default forward _drop")
            commands.append("table_add forward repeat %s => %s" % (SENDER_PORT, RECIEVE_PORT))
            commands.append("table_add forward repeat %s => %s" % (RECIEVE_PORT, SENDER_PORT))

        return commands

    # def get_header_format(self):
    #     header_format = dict()
    #     header_format['parse_payload'] = self.parse_payload
    #     header_format['headers'] = self.out_header_fields
    #     return header_format

    def get_header_formats(self):
        # This needs updates as we now change the logic of packet parsing at the emitter
        header_formats = dict()
        for qid, query in self.queries.iteritems():
            header_formats[qid] = query.get_header_format()
        return header_formats

    def get_update_commands(self, filter_update):
        commands = list()
        for qid, filter_id in filter_update:
            commands.extend(self.queries[qid].get_update_commands(filter_id, filter_update[(qid, filter_id)]))
        return commands
