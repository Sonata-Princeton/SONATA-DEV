#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


from p4_elements import Register, HashFields, Table, MetaData, Action
from p4_primitives import BitAnd, ModifyField, ModifyFieldWithHashBasedOffset, RegisterRead, RegisterWrite, BitOr
from sonata.dataplane_driver.utils import get_logger

HEADER_MAP = {'sIP': 'ipv4.srcAddr', 'dIP': 'ipv4.dstAddr',
              'sPort': 'tcp.srcPort', 'dPort': 'tcp.dstPort',
              'nBytes': 'ipv4.totalLen', 'proto': 'ipv4.protocol',
              'sMac': 'ethernet.srcAddr', 'dMac': 'ethernet.dstAddr', 'payload': ''}

HEADER_SIZE = {'sIP': 32, 'dIP': 32, 'sPort': 16, 'dPort': 16,
               'nBytes': 16, 'proto': 16, 'sMac': 48, 'dMac': 48,
               'qid': 16, 'count': 16}

HEADER_MASK_SIZE = {'sIP': 8, 'dIP': 8, 'sPort': 4, 'dPort': 4,
               'nBytes': 4, 'proto': 4, 'sMac': 12, 'dMac': 12,
               'qid': 4, 'count': 4}

REGISTER_WIDTH = 32
REGISTER_NUM_INDEX_BITS = 12
REGISTER_INSTANCE_COUNT = 2**REGISTER_NUM_INDEX_BITS
TABLE_SIZE = 64
THRESHOLD = 5


class P4Operator(object):
    def __init__(self, name, qid, operator_id, keys):
        self.name = name
        self.operator_name = '%s_%i_%i' % (name.lower(), qid, operator_id)
        self.query_id = qid
        self.operator_id = operator_id
        self.keys = list(keys)
        self.out_headers = list(keys)

        # LOGGING
        self.logger = get_logger(name, 'DEBUG')

    def get_out_headers(self):
        return self.out_headers

    def get_name(self):
        return self.operator_name

    def get_commands(self):
        pass

    def get_code(self):
        pass

    def get_control_flow(self, indent_level):
        pass


class P4Distinct(P4Operator):
    def __init__(self, qid, operator_id, meta_init_name, drop_action, nop_action, keys):
        super(P4Distinct, self).__init__('Distinct', qid, operator_id, keys)

        self.threshold = 1
        self.comp_func = '<='  # bitwise and
        self.update_func = '&'  # bitwise and

        # create METADATA to store index and value
        fields = [('value', REGISTER_WIDTH), ('index', REGISTER_NUM_INDEX_BITS)]
        self.metadata = MetaData(self.operator_name, fields)

        # create REGISTER to keep track of counts
        self.register = Register(self.operator_name, REGISTER_WIDTH, REGISTER_INSTANCE_COUNT)

        # create HASH for access to register
        hash_fields = list()
        for key in self.keys:
            if '/' in key:
                self.logger.error('found a / in the key')
                raise NotImplementedError
            else:
                hash_fields.append('%s.%s' % (meta_init_name, key))
        self.hash = HashFields(self.operator_name, hash_fields, 'crc32', REGISTER_NUM_INDEX_BITS)

        # name of metadata field where the index of the count within the register is stored
        self.index_field_name = '%s.index' % self.metadata.get_name()
        # name of metadata field where the count is kept temporarily
        self.value_field_name = '%s.value' % self.metadata.get_name()

        # create ACTION and TABLE to compute hash and get value
        primitives = list()
        primitives.append(ModifyFieldWithHashBasedOffset(self.index_field_name, 0, self.hash.get_name(),
                                                         REGISTER_INSTANCE_COUNT))
        primitives.append(RegisterRead(self.value_field_name, self.register.get_name(), self.index_field_name))
        primitives.append(BitOr(self.value_field_name, self.value_field_name, 1))
        primitives.append(RegisterWrite(self.register.get_name(), self.index_field_name, self.value_field_name))
        self.action = Action('do_init_%s' % self.operator_name, primitives)

        table_name = 'init_%s' % self.operator_name
        self.init_table = Table(table_name, self.action.get_name(), [], None, 1)

        # create two TABLEs that implement reduce operation: if count <= THRESHOLD, update count and drop, else let it
        # pass through
        table_name = 'pass_%s' % self.operator_name
        self.pass_table = Table(table_name, nop_action, [], None, 1)
        table_name = 'drop_%s' % self.operator_name
        self.drop_table = Table(table_name, drop_action, [], None, 1)

    def __repr__(self):
        return '.Distinct(keys=' + ', '.join([x for x in self.keys]) + ')'

    def get_code(self):
        out = ''
        out += '// %s %i of query %i\n' % (self.name, self.operator_id, self.query_id)
        out += self.metadata.get_code()
        out += self.hash.get_code()
        out += self.register.get_code()
        out += self.action.get_code()
        out += self.init_table.get_code()
        out += self.pass_table.get_code()
        out += self.drop_table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.init_table.get_default_command())
        commands.append(self.pass_table.get_default_command())
        commands.append(self.drop_table.get_default_command())
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.init_table.get_name())
        out += '%sif (%s %s %i) {\n' % (indent, self.value_field_name, self.comp_func, self.threshold)
        out += '%s\tapply(%s);\n' % (indent, self.pass_table.get_name())
        out += '%s}\n' % (indent, )
        out += '%selse {\n' % (indent, )
        out += '%s\tapply(%s);\n' % (indent, self.drop_table.get_name())
        out += '%s}\n' % (indent,)
        return out

    def get_init_keys(self):
        return self.keys


class P4Reduce(P4Operator):
    def __init__(self, qid, operator_id, meta_init_name, drop_action, keys, threshold):
        super(P4Reduce, self).__init__('Reduce', qid, operator_id, keys)
        self.out_headers += ['count']

        if threshold == '-1':
            self.threshold = THRESHOLD
        else:
            self.threshold = threshold

        # create METADATA to store index and value
        fields = [('value', REGISTER_WIDTH), ('index', REGISTER_NUM_INDEX_BITS)]
        self.metadata = MetaData(self.operator_name, fields)

        # create REGISTER to keep track of counts
        self.register = Register(self.operator_name, REGISTER_WIDTH, REGISTER_INSTANCE_COUNT)

        # create HASH for access to register
        hash_fields = list()
        for key in self.keys:
            if '/' in key:
                self.logger.error('found a / in the key')
                raise NotImplementedError
            else:
                hash_fields.append('%s.%s' % (meta_init_name, key))
        self.hash = HashFields(self.operator_name, hash_fields, 'crc32', REGISTER_NUM_INDEX_BITS)

        # name of metadata field where the index of the count within the register is stored
        self.index_field_name = '%s.index' % self.metadata.get_name()
        # name of metadata field where the count is kept temporarily
        self.value_field_name = '%s.value' % self.metadata.get_name()

        # create ACTION and TABLE to compute hash and get value
        primitives = list()
        primitives.append(ModifyFieldWithHashBasedOffset(self.index_field_name, 0, self.hash.get_name(),
                                                         REGISTER_INSTANCE_COUNT))
        primitives.append(RegisterRead(self.value_field_name, self.register.get_name(), self.index_field_name))
        primitives.append(ModifyField(self.value_field_name, '%s + %i' % (self.value_field_name, 1)))
        primitives.append(RegisterWrite(self.register.get_name(), self.index_field_name, self.value_field_name))
        self.init_action = Action('do_init_%s' % self.operator_name, primitives)
        table_name = 'init_%s' % self.operator_name
        self.init_table = Table(table_name, self.init_action.get_name(), [], None, 1)

        # create three TABLEs that implement reduce operation
        # if count <= THRESHOLD, update count and drop,
        table_name = 'drop_%s' % self.operator_name
        self.drop_table = Table(table_name, drop_action, [], None, 1)

        # if count == THRESHOLD, pass through with current count
        self.set_count_action = Action('set_count_%s' % self.operator_name,
                                       ModifyField('%s.count' % meta_init_name, self.value_field_name))
        table_name = 'first_pass_%s' % self.operator_name
        self.first_pass_table = Table(table_name, self.set_count_action.get_name(), [], None, 1)

        # if count > THRESHOLD, let it pass through with count set to 1
        self.reset_count_action = Action('reset_count_%s' % self.operator_name,
                                         ModifyField('%s.count' % meta_init_name, 1))
        table_name = 'pass_%s' % self.operator_name
        self.pass_table = Table(table_name, self.reset_count_action.get_name(), [], None, 1)

    def __repr__(self):
        return '.Reduce(keys=' + ','.join([x for x in self.keys]) + ', threshold='+str(self.threshold)+')'

    def get_code(self):
        out = ''
        out += '// %s %i of query %i\n' % (self.name, self.operator_id, self.query_id)
        out += self.metadata.get_code()
        out += self.hash.get_code()
        out += self.register.get_code()
        out += self.init_action.get_code()
        out += self.set_count_action.get_code()
        out += self.reset_count_action.get_code()
        out += self.init_table.get_code()
        out += self.first_pass_table.get_code()
        out += self.pass_table.get_code()
        out += self.drop_table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.init_table.get_default_command())
        commands.append(self.first_pass_table.get_default_command())
        commands.append(self.pass_table.get_default_command())
        commands.append(self.drop_table.get_default_command())
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.init_table.get_name())
        out += '%sif (%s == %i) {\n' % (indent, self.value_field_name, self.threshold)
        out += '%s\tapply(%s);\n' % (indent, self.first_pass_table.get_name())
        out += '%s}\n' % (indent, )
        out += '%selse if (%s > %i) {\n' % (indent, self.value_field_name, self.threshold)
        out += '%s\tapply(%s);\n' % (indent, self.pass_table.get_name())
        out += '%s}\n' % (indent, )
        out += '%selse {\n' % (indent, )
        out += '%s\tapply(%s);\n' % (indent, self.drop_table.get_name())
        out += '%s}\n' % (indent,)
        return out

    def get_init_keys(self):
        return self.keys + ['count']


class P4MapInit(P4Operator):
    def __init__(self, qid, operator_id, keys):
        super(P4MapInit, self).__init__('MapInit', qid, operator_id, keys)

        # create METADATA object to store data for all keys
        fields = list()
        for key in self.keys:
            fields.append((key, HEADER_SIZE[key]))

        self.metadata = MetaData(self.operator_name, fields)

        # create ACTION to initialize the metadata
        primitives = list()
        for key in self.keys:
            if key in HEADER_MAP:
                meta_field_name = '%s.%s' % (self.metadata.get_name(), key)
                field_name = HEADER_MAP[key]
                primitives.append(ModifyField(meta_field_name, field_name))
            elif key == 'qid':
                meta_field_name = '%s.%s' % (self.metadata.get_name(), key)
                primitives.append(ModifyField(meta_field_name, qid))

        self.action = Action('do_%s' % self.operator_name, primitives)

        # create dummy TABLE to execute the action
        self.table = Table(self.operator_name, self.action.get_name(), [], None, 1)

    def __repr__(self):
        return '.MapInit(keys='+str(self.keys)+')'

    def get_meta_name(self):
        return self.metadata.get_name()

    def get_code(self):
        out = ''
        out += '// MapInit of query %i\n' % self.query_id
        out += self.metadata.get_code()
        out += self.action.get_code()
        out += self.table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.table.get_default_command())
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.table.get_name())
        return out

    def get_init_keys(self):
        return self.keys


class P4Map(P4Operator):
    def __init__(self, qid, operator_id, meta_init_name, keys, map_keys, func):
        super(P4Map, self).__init__('Map', qid, operator_id, keys)

        self.meta_init_name = meta_init_name
        self.map_keys = map_keys
        self.func = func
        # create ACTION using the function
        primitives = list()
        if len(func) > 0:
            self.func = func
            if func[0] == 'mask' or not func[0]:
                for field in self.map_keys:
                    # print self.__repr__(), self.map_keys
                    mask_size = (func[1]/4)
                    mask = '0x' + ('f' * mask_size) + ('0' * (HEADER_MASK_SIZE[field] - mask_size))
                    field_name = '%s.%s' % (self.meta_init_name, field)
                    primitives.append(BitAnd(field_name, field_name, mask))
        #     else:
        #         # self.logger.error('Got the following func with the Map Operator: %s' % (str(func), ))
        #         # raise NotImplementedError
        # else:
        #     # self.logger.error('Got an invalid func with the Map Operator: %s' % (str(func),))
        #     # raise NotImplementedError

        self.action = Action('do_%s' % self.operator_name, primitives)

        # create dummy TABLE to execute the action
        self.table = Table(self.operator_name, self.action.get_name(), [], None, 1)

    def __repr__(self):
        return '.Map(keys='+str(self.keys)+', map_keys='+str(self.map_keys)+', func='+str(self.func)+')'

    def get_code(self):
        out = ''
        out += '// Map %i of query %i\n' % (self.operator_id, self.query_id)
        out += self.action.get_code()
        out += self.table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.table.get_default_command())
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.table.get_name())
        return out

    def get_init_keys(self):
        return self.keys


class P4Filter(P4Operator):
    def __init__(self, qid, operator_id, keys, filter_keys, func, source, match_action, miss_action):
        super(P4Filter, self).__init__('Filter', qid, operator_id, keys)

        self.filter_keys = filter_keys
        self.filter_mask = None
        self.filter_values = None
        self.func = None

        self.match_action = match_action
        self.miss_action = miss_action

        self.source = source

        if not len(func) > 0 or func[0] == 'geq':
            self.logger.error('Got the following func with the Filter Operator: %s' % (str(func), ))
            # raise NotImplementedError
        else:
            self.func = func[0]
            if func[0] == 'mask':
                self.filter_mask = func[1]
                self.filter_values = func[2:]
            elif func[0] == 'eq':
                self.filter_values = func[1:]

        reads_fields = list()
        for filter_key in self.filter_keys:
            if self.func == 'mask':
                reads_fields.append((HEADER_MAP[filter_key], 'lpm'))
            else:
                reads_fields.append((HEADER_MAP[filter_key], 'exact'))

        self.table = Table(self.operator_name, miss_action, (match_action, ), reads_fields, TABLE_SIZE)

    def __repr__(self):
        return '.Filter(filter_keys='+str(self.filter_keys)+', func='+str(self.func)+', src = '+str(self.source)+')'

    def get_code(self):
        out = ''
        out += '// Filter %i of query %i\n' % (self.operator_id, self.query_id)
        out += self.table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.table.get_default_command())
        if self.filter_values:
            for filter_value in self.filter_values:
                commands.append(self.table.get_add_rule_command(self.match_action, filter_value, None))
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.table.get_name())
        return out

    def get_match_action(self):
        return self.match_action

    def get_filter_mask(self):
        return self.filter_mask

    def get_init_keys(self):
        return self.keys
