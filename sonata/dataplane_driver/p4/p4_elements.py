#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


from sonata.dataplane_driver.utils import get_logger


class P4Element(object):
    def __init__(self, name):
        self.name = name

        # LOGGING
        self.logger = get_logger(name, 'DEBUG')

    def get_name(self):
        return self.name


class Action(P4Element):
    def __init__(self, name, primitives):
        super(Action, self).__init__(name)
        if not isinstance(primitives, list):
            self.primitives = [primitives]
        else:
            self.primitives = primitives

    def get_code(self):
        out = ''
        out += 'action %s(){\n' % (self.name, )
        for primitive in self.primitives:
            out += '\t%s;\n' % (primitive.get_code())
        out += '}\n\n'
        return out


class Table(P4Element):
    def __init__(self, name, default_action, other_actions, reads, size):
        super(Table, self).__init__(name)
        self.other_actions = other_actions  # list of strings
        self.size = size  # int
        self.reads = reads  # list of tuples (string, string)
        self.default_action = default_action

    def get_code(self):
        out = ''
        out += 'table %s {\n' % self.name
        if self.reads:
            out += '\treads {\n'
            for field, read_type in self.reads:
                out += '\t\t%s: %s;\n' % (field, read_type)
            out += '\t}\n'
        out += '\tactions {\n'
        out += '\t\t%s;\n' % self.default_action
        for action in self.other_actions:
            out += '\t\t%s;\n' % action
        out += '\t}\n'
        out += '\tsize : %i;\n' % self.size
        out += '}\n\n'
        return out

    def get_default_command(self):
        out = ''
        out += 'table_set_default %s %s' % (self.name, self.default_action)

        return out

    def get_add_rule_command(self, action_name, match_values, action_values):
        match_string = ''
        if match_values:
            match_string = ' '.join([str(x) for x in match_values])
        action_string = ''
        if action_values:
            action_string = ' '.join([str(x) for x in action_values])
        out = 'table_add %s %s %s => %s' % (self.name, action_name, match_string, action_string)
        return out


class Register(P4Element):
    def __init__(self, name, width, count):
        super(Register, self).__init__(name)
        self.width = width
        self.instance_count = count

    def get_code(self):
        out = ''
        out += 'register %s {\n' % self.name
        out += '\twidth: %i;\n' % self.width
        out += '\tinstance_count: %i;\n' % self.instance_count
        out += '}\n\n'
        return out


class FieldList(P4Element):
    def __init__(self, name, fields):
        super(FieldList, self).__init__('%s_fields' % name)
        self.fields = fields

    def get_code(self):
        out = ''
        out += 'field_list %s {\n' % self.name
        for field in self.fields:
            out += '\t%s;\n' % field
        out += '}\n\n'
        return out


class HashFields(P4Element):
    def __init__(self, name, fields, algorithm, output_width):
        super(HashFields, self).__init__('hash_%s' % name)
        self.field_list = FieldList(self.name, fields)
        self.output_width = output_width
        self.algorithm = algorithm

    def get_code(self):
        out = self.field_list.get_code()
        out += 'field_list_calculation %s {\n' % self.name
        out += '\tinput {\n'
        out += '\t\t%s;\n' % self.field_list.get_name()
        out += '\t}\n'
        out += '\talgorithm: %s;\n' % self.algorithm
        out += '\toutput_width: %i;\n' % self.output_width
        out += '}\n\n'
        return out


class MetaData(P4Element):
    def __init__(self, name, fields):
        super(MetaData, self).__init__('meta_%s' % name)
        # list of tuples where the first element is the name and the second the length of the field
        self.fields = fields

    def get_code(self):
        out = ''
        out += 'header_type %s_t {\n' % self.name
        out += '\tfields {\n'
        for field_name, length in self.fields:
            out += '\t\t%s: %i;\n' % (field_name, length)
        out += '\t}\n'
        out += '}\n\n'
        out += 'metadata %s_t %s;\n\n' % (self.name, self.name)

        return out


class Header(P4Element):
    def __init__(self, name, fields):
        super(Header, self).__init__('%s' % name)
        # list of tuples where the first element is the name and the second the length of the field
        self.fields = fields

    def get_code(self):
        out = ''
        out += 'header_type %s_t {\n' % self.name
        out += '\tfields {\n'
        for field_name, length in self.fields:
            out += '\t\t%s: %i;\n' % (field_name, length)
        out += '\t}\n'
        out += '}\n\n'
        out += 'header %s_t %s;\n\n' % (self.name, self.name)

        return out


class MirrorSession(P4Element):
    def __init__(self, mirror_id, span_port):
        super(MirrorSession, self).__init__('MirrorSession')
        self.mirror_id = mirror_id
        self.span_port = span_port

    def get_command(self):
        return 'mirroring_add %i %i' % (self.mirror_id, self.span_port)

    def get_session_id(self):
        return self.mirror_id
