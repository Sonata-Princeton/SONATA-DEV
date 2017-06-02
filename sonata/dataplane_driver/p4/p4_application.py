#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


from p4_elements import Action, MetaData, MirrorSession, FieldList, Table, Header
from p4_primitives import NoOp, CloneIngressPktToEgress, AddHeader, ModifyField
from p4_query import P4Query
from sonata.dataplane_driver.utils import get_logger
import logging

SESSION_ID = 8001
SPAN_PORT = 12


class P4Application(object):
    def __init__(self, app):
        # LOGGING
        log_level = logging.ERROR
        self.logger = get_logger('P4Application', 'INFO')
        self.logger.setLevel(log_level)
        self.logger.info('init')

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
        self.final_header = Header('final_header', [('delimiter', 32)])

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
            self.logger.debug('create query pipeline for qid: %i' % (query_id, ))
            parse_payload = app[query_id].parse_payload
            operators = app[query_id].operators
            query = P4Query(query_id,
                            parse_payload,
                            operators,
                            nop_name,
                            '%s.%s' % (meta_name, self.drop_meta_field),
                            '%s.%s' % (meta_name, self.satisfied_meta_field),
                            '%s.%s' % (meta_name, self.clone_meta_field))
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

        # P4 INVARIANTS
        p4_src += self.get_invariants()

        # OUT HEADER PARSER
        p4_src += self.get_out_header_parser()

        # APP METADATA, ACTIONS, FIELDLISTS, TABLES
        p4_src += self.get_app_code()

        # QUERY METADATA, HEADERS, TABLES AND ACTIONS
        p4_src += self.get_code()

        # INGRESS PIPELINE
        p4_src += self.get_ingress_pipeline()

        # EGRESS PIPELINE
        p4_src += self.get_egress_pipeline()

        return p4_src

    @staticmethod
    def get_invariants():
        out = ''
        out += '#include "includes/headers.p4"\n'
        out += '#include "includes/parser.p4"\n\n'
        out += 'parser start {\n'
        out += '\treturn select(current(0, 64)) {\n'
        out += '\t\t0 : parse_out_header;\n'
        out += '\t\tdefault: parse_ethernet;\n'
        out += '\t}\n'
        out += '}\n\n'
        return out

    def get_out_header_parser(self):
        out = ''
        out += 'parser parse_out_header {\n'
        for query in self.queries.values():
            out += '\textract(%s);\n' % query.get_out_header()
        out += '\treturn parse_final_header;\n'
        out += '}\n\n'
        out += 'parser parse_final_header {\n'
        out += '\textract(%s);\n' % self.final_header.get_name()
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
        out += self.final_header.get_code()
        out += self.final_header_action.get_code()
        out += self.final_header_table.get_code()
        return out

    def get_code(self):
        out = ''
        for query in self.queries.values():
            out += query.get_code()
        return out

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
        return commands

    def get_header_formats(self):
        header_formats = dict()
        for qid, query in self.queries.iteritems():
            header_formats[qid] = query.get_header_format()
        return header_formats

    def get_update_commands(self, filter_update):
        commands = list()
        for qid, filter_id in filter_update:
            commands.extend(self.queries[qid].get_update_commands(filter_id, filter_update[(qid, filter_id)]))
        return commands
