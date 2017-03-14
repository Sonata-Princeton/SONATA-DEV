#!/usr/bin/env python


class P4Target(object):
    def __init__(self):
        pass

    def compile_app(self):
        # P4 INVARIANTS
        # add header and parser includes

        # define general actions (_nop, _drop)
        pass


# TODO integrate p4 queries here

# Class that holds one refined query - which consists of an ordered list of operators
class P4Query(object):
    def __init__(self):
        self.operators = None

    def get_control_flow(self):
        # get init action - compute all hashes
        pass

    def get_state(self):
        pass


class P4Operator(object):
    def __init__(self, name, qid, id):
        self.name = name
        self.query_id = qid
        self.operator_id = id
        self.tables = list()
        self.registers = list()
        self.metadata = list()

    # get_control_flow
    # get_state
    # get_metadata


class P4Reduce(P4Operator):
    def __init__(self, qid, id):
        super(P4Reduce, self).__init__('Reduce', qid, id)


class P4Map(P4Operator):
    def __init__(self, qid, id):
        super(P4Map, self).__init__('Map', qid, id)


class P4Distinct(P4Operator):
    def __init__(self, qid, id, keys):
        super(P4Distinct, self).__init__('Distinct', qid, id)

        self.threshold = 0
        self.instance_count = 0
        self.width = 0

        self.keys = keys


class P4Filter(P4Operator):
    def __init__(self, qid, id):
        super(P4Filter, self).__init__('Filter', qid, id)

        self.filter_keys = None
        self.filter_mask = None


class P4Truncate(P4Operator):
    def __init__(self, qid, id):
        super(P4Truncate, self).__init__('Truncate', qid, id)


# TODO integrate p4 queries here

class P4Element(object):
    def __init__(self, name):
        self.name = name


class Register(P4Element):
    def __init__(self, width, count):
        super(Register, self).__init__('Register')
        self.width = width
        self.instance_count = count


class Table(P4Element):
    def __init__(self, actions, reads, size):
        super(Table, self).__init__('Table')
        self.actions = actions
        self.size = size
        self.reads = reads


class HashFields(P4Element):
    def __init__(self, fields, algorithm, output_width):
        super(HashFields, self).__init__('HashFields')
        self.fields = fields
        self.output_width = output_width
        self.algorithm = algorithm


class MetaData(P4Element):
    def __init__(self, qid):
        super(MetaData, self).__init__('MetaData')
        # list of tuples where the first element is the name and the second the length of the field
        self.qid = qid
        self.fields = list()

    def add_field(self, name, length):
        self.fields.append((name, length))

    def add_fields(self, fields):
        self.fields.extend(fields)
