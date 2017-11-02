#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


from p4_elements import Register, HashFields, Table, MetaData, Action
from p4_field import P4Field
from p4_primitives import BitAnd, ModifyField, ModifyFieldWithHashBasedOffset, RegisterRead, RegisterWrite, BitOr
from sonata.dataplane_driver.utils import get_logger

REGISTER_WIDTH = 32
REGISTER_NUM_INDEX_BITS = 16
REGISTER_INSTANCE_COUNT = 2 ** REGISTER_NUM_INDEX_BITS
TABLE_SIZE = 64
THRESHOLD = 5

# TODO: figure out a cleaner way of getting rid of these magical numbers
HEADER_MASK_SIZE = {'ipv4.srcIP': 8, 'ipv4.dstIP': 8, 'udp.sport': 4, 'udp.dport': 4,
                    'ipv4.totalLen': 4, 'ipv4.proto': 4, 'ethernet.srcMac': 12, 'ethernet.dstMac': 12,
                    'qid': 4, 'count': 4, 'index': 4}

QID_SIZE = 16
COUNT_SIZE = 16
INDEX_SIZE = 16


class P4Operator(object):
    operator_specific_fields = dict()

    def __init__(self, name, qid, operator_id, keys, p4_raw_fields):
        self.name = name
        self.operator_name = '%s_%i_%i' % (name.lower(), qid, operator_id)
        self.query_id = qid
        self.operator_id = operator_id
        self.keys = list(keys)
        self.out_headers = list(keys)
        self.p4_raw_fields = p4_raw_fields
        self.create_operator_specific_fields()

        # LOGGING
        self.logger = get_logger(name, 'DEBUG')

    def create_operator_specific_fields(self):
        for key in self.keys:
            if key not in ['qid', 'count', 'index']: self.operator_specific_fields[
                key] = self.p4_raw_fields.get_target_field(key)

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
    def __init__(self, qid, operator_id, meta_init_name, drop_action, nop_action, keys, p4_raw_fields):
        super(P4Distinct, self).__init__('Distinct', qid, operator_id, keys, p4_raw_fields)

        self.threshold = 0
        self.comp_func = '<='  # bitwise and
        self.update_func = '&'  # bitwise and

        # create METADATA to store index and value
        fields = [('value', REGISTER_WIDTH), ('index', REGISTER_NUM_INDEX_BITS)]
        self.metadata = MetaData(self.operator_name, fields)

        # create REGISTER to keep track of counts
        self.register = Register(self.operator_name, REGISTER_WIDTH, REGISTER_INSTANCE_COUNT)

        # Add map init
        hash_init_fields = list()
        for fld in self.keys:
            if fld == 'qid':
                hash_init_fields.append(P4Field(layer=None, target_name="qid", sonata_name="qid",
                                                size=QID_SIZE))
            elif fld == 'count':
                hash_init_fields.append(P4Field(layer=None, target_name="count", sonata_name="count",
                                                size=COUNT_SIZE))
            else:
                hash_init_fields.append(self.p4_raw_fields.get_target_field(fld))
        # create HASH for access to register
        hash_fields = list()
        for field in hash_init_fields:
            if '/' in field.sonata_name:
                self.logger.error('found a / in the key')
                raise NotImplementedError
            else:
                hash_fields.append('%s.%s' % (meta_init_name, field.target_name.replace(".", "_")))
        self.hash = HashFields(self.operator_name, hash_fields, 'crc16', REGISTER_NUM_INDEX_BITS)

        # name of metadata field where the index of the count within the register is stored
        self.index_field_name = '%s.index' % self.metadata.get_name()
        # name of metadata field where the count is kept temporarily
        self.value_field_name = '%s.value' % self.metadata.get_name()

        # create ACTION and TABLE to compute hash and get value
        primitives1 = list()
        primitives1.append(ModifyFieldWithHashBasedOffset(self.index_field_name, 0, self.hash.get_name(),
                                                          REGISTER_INSTANCE_COUNT))
        primitives1.append(RegisterRead(self.value_field_name, self.register.get_name(), self.index_field_name))

        self.action1 = Action('do_init_%s' % self.operator_name, primitives1)

        # create ACTION and TABLE to bit_or value & write back
        primitives2 = list()
        primitives2.append(BitOr(self.value_field_name, self.value_field_name, 1))
        primitives2.append(RegisterWrite(self.register.get_name(), self.index_field_name, self.value_field_name))
        self.action2 = Action('do_update_%s' % self.operator_name, primitives2)

        table_name = 'init_%s' % self.operator_name
        self.init_table = Table(table_name, self.action1.get_name(), [], None, 1)

        table_name = 'update_%s' % self.operator_name
        self.update_table = Table(table_name, self.action2.get_name(), [], None, 1)

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
        out += self.action1.get_code()
        out += self.action2.get_code()
        out += self.update_table.get_code()
        out += self.init_table.get_code()
        out += self.pass_table.get_code()
        out += self.drop_table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.init_table.get_default_command())
        commands.append(self.update_table.get_default_command())
        commands.append(self.pass_table.get_default_command())
        commands.append(self.drop_table.get_default_command())
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.init_table.get_name())
        out += '%sif (%s %s %i) {\n' % (indent, self.value_field_name, self.comp_func, self.threshold)
        out += '%s\tapply(%s);\n' % (indent, self.pass_table.get_name())
        out += '%s\tapply(%s);\n' % (indent, self.update_table.get_name())
        out += '%s}\n' % (indent,)
        out += '%selse {\n' % (indent,)
        out += '%s\tapply(%s);\n' % (indent, self.drop_table.get_name())
        out += '%s}\n' % (indent,)
        return out

    def get_init_keys(self):
        return self.keys


class P4Reduce(P4Operator):
    def __init__(self, qid, operator_id, meta_init_name, drop_action, keys, values, threshold, read_register,
                 p4_raw_fields):
        super(P4Reduce, self).__init__('Reduce', qid, operator_id, keys, p4_raw_fields)

        if threshold == '-1':
            self.threshold = int(THRESHOLD)
        else:
            self.threshold = int(threshold)

        self.read_register = read_register

        if self.read_register:
            self.out_headers += ['index']
        else:
            self.out_headers += ['count']

        # create METADATA to store index and value
        fields = [('value', REGISTER_WIDTH), ('index', REGISTER_NUM_INDEX_BITS)]
        self.metadata = MetaData(self.operator_name, fields)

        # create REGISTER to keep track of counts
        self.register = Register(self.operator_name, REGISTER_WIDTH, REGISTER_INSTANCE_COUNT)

        self.values = values

        # Add map init
        hash_init_fields = list()
        for fld in self.keys:
            if fld == 'qid':
                hash_init_fields.append(P4Field(layer=None, target_name="qid", sonata_name="qid",
                                                size=QID_SIZE))
            elif fld == 'count':
                hash_init_fields.append(P4Field(layer=None, target_name="count", sonata_name="count",
                                                size=COUNT_SIZE))
            elif fld == 'index':
                hash_init_fields.append(P4Field(layer=None, target_name="index", sonata_name="index",
                                                size=INDEX_SIZE))
            else:
                hash_init_fields.append(self.p4_raw_fields.get_target_field(fld))
        # create HASH for access to register
        hash_fields = list()
        for field in hash_init_fields:
            if '/' in field.sonata_name:
                self.logger.error('found a / in the key')
                raise NotImplementedError
            else:
                hash_fields.append('%s.%s' % (meta_init_name, field.target_name.replace(".", "_")))
        self.hash = HashFields(self.operator_name, hash_fields, 'crc16', REGISTER_NUM_INDEX_BITS)

        # name of metadata field where the index of the count within the register is stored
        self.index_field_name = '%s.index' % self.metadata.get_name()
        # name of metadata field where the count is kept temporarily
        self.value_field_name = '%s.value' % self.metadata.get_name()

        # create ACTION and TABLE to compute hash and get value
        primitives = list()
        primitives.append(ModifyFieldWithHashBasedOffset(self.index_field_name, 0, self.hash.get_name(),
                                                         REGISTER_INSTANCE_COUNT))
        primitives.append(RegisterRead(self.value_field_name, self.register.get_name(), self.index_field_name))


        if self.values[0] == 'count':
            if self.threshold <= 1:
                self.threshold = '1'

            primitives.append(ModifyField(self.value_field_name, '%s + %i' % (self.value_field_name, 1)))
        else:
            target_fld = self.p4_raw_fields.get_target_field(self.values[0])
            if self.threshold <= 1:
                self.threshold = '%s.%s' % (meta_init_name, target_fld.target_name.replace(".", "_"))

            primitives.append(ModifyField(self.value_field_name, '%s + %s' % (
            self.value_field_name, '%s.%s' % (meta_init_name, target_fld.target_name.replace(".", "_")))))

        primitives.append(RegisterWrite(self.register.get_name(), self.index_field_name, self.value_field_name))
        self.init_action = Action('do_init_%s' % self.operator_name, primitives)
        table_name = 'init_%s' % self.operator_name
        self.init_table = Table(table_name, self.init_action.get_name(), [], None, 1)

        # create three TABLEs that implement reduce operation
        # if count <= THRESHOLD, update count and drop,
        table_name = 'drop_%s' % self.operator_name
        self.drop_table = Table(table_name, drop_action, [], None, 1)

        # if count == THRESHOLD, pass through with current count
        field_to_modified = None
        if not self.read_register:
            field_to_modified = ModifyField('%s.count' % meta_init_name, self.value_field_name)
        else:
            field_to_modified = ModifyField('%s.index' % meta_init_name, self.index_field_name)

        self.set_count_action = Action('set_count_%s' % self.operator_name,
                                       field_to_modified)
        table_name = 'first_pass_%s' % self.operator_name
        self.first_pass_table = Table(table_name, self.set_count_action.get_name(), [], None, 1)

        if not self.read_register:
            # if count > THRESHOLD, let it pass through with count set to 1
            self.reset_count_action = Action('reset_count_%s' % self.operator_name,
                                             ModifyField('%s.count' % meta_init_name, 1))
            table_name = 'pass_%s' % self.operator_name
            self.pass_table = Table(table_name, self.reset_count_action.get_name(), [], None, 1)

    def __repr__(self):
        return '.Reduce(keys=' + ','.join([x for x in self.keys]) + ', threshold=' + str(self.threshold) + ')'

    def get_code(self):
        out = ''
        out += '// %s %i of query %i\n' % (self.name, self.operator_id, self.query_id)
        out += self.metadata.get_code()
        out += self.hash.get_code()
        out += self.register.get_code()
        out += self.init_action.get_code()
        out += self.set_count_action.get_code()
        if not self.read_register:
            out += self.reset_count_action.get_code()
            out += self.pass_table.get_code()

        out += self.init_table.get_code()
        out += self.first_pass_table.get_code()
        out += self.drop_table.get_code()
        out += '\n'
        return out

    def get_commands(self):
        commands = list()
        commands.append(self.init_table.get_default_command())
        commands.append(self.first_pass_table.get_default_command())
        if not self.read_register: commands.append(self.pass_table.get_default_command())
        commands.append(self.drop_table.get_default_command())
        return commands

    def get_control_flow(self, indent_level):
        indent = '\t' * indent_level
        out = ''
        out += '%sapply(%s);\n' % (indent, self.init_table.get_name())
        out += '%sif (%s == %s) {\n' % (indent, self.value_field_name, self.threshold)
        out += '%s\tapply(%s);\n' % (indent, self.first_pass_table.get_name())
        out += '%s}\n' % (indent,)

        if not self.read_register:
            out += '%selse if (%s > %s) {\n' % (indent, self.value_field_name, self.threshold)
            out += '%s\tapply(%s);\n' % (indent, self.pass_table.get_name())
            out += '%s}\n' % (indent,)

        out += '%selse {\n' % (indent,)
        out += '%s\tapply(%s);\n' % (indent, self.drop_table.get_name())
        out += '%s}\n' % (indent,)
        return out

    def get_init_keys(self):

        return self.keys + self.values


class P4MapInit(P4Operator):
    def __init__(self, qid, operator_id, keys, p4_raw_fields):
        super(P4MapInit, self).__init__('MapInit', qid, operator_id, keys, p4_raw_fields)

        # Add map init
        map_init_fields = list()
        for fld in self.keys:
            if fld == 'qid':
                map_init_fields.append(P4Field(layer=None, target_name="qid", sonata_name="qid",
                                               size=QID_SIZE))
            elif fld == 'count':
                map_init_fields.append(P4Field(layer=None, target_name="count", sonata_name="count",
                                               size=COUNT_SIZE))
            elif fld == 'index':
                map_init_fields.append(P4Field(layer=None, target_name="index", sonata_name="index",
                                               size=INDEX_SIZE))
            else:
                map_init_fields.append(self.p4_raw_fields.get_target_field(fld))
        # create METADATA object to store data for all keys
        meta_fields = list()
        for fld in map_init_fields:
            meta_fields.append((fld.target_name.replace(".", "_"), fld.size))

        self.metadata = MetaData(self.operator_name, meta_fields)

        # create ACTION to initialize the metadata
        primitives = list()
        for fld in map_init_fields:
            sonata_name = fld.sonata_name
            target_name = fld.target_name
            meta_field_name = '%s.%s' % (self.metadata.get_name(), target_name.replace(".", "_"))

            if sonata_name == 'qid':
                # Assign query id to this field
                primitives.append(ModifyField(meta_field_name, qid))
            elif sonata_name == 'count':
                primitives.append(ModifyField(meta_field_name, 0))
            elif sonata_name == 'index':
                primitives.append(ModifyField(meta_field_name, 0))
            else:
                # Read data from raw header fields and assign them to these meta fields
                primitives.append(ModifyField(meta_field_name, target_name))

        self.action = Action('do_%s' % self.operator_name, primitives)

        # create dummy TABLE to execute the action
        self.table = Table(self.operator_name, self.action.get_name(), [], None, 1)

    def __repr__(self):
        return '.MapInit(keys=' + str(self.keys) + ')'

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
    def __init__(self, qid, operator_id, meta_init_name, keys, map_keys, map_values, func, p4_raw_fields):
        super(P4Map, self).__init__('Map', qid, operator_id, keys, p4_raw_fields)

        self.meta_init_name = meta_init_name
        self.map_keys = map_keys
        self.func = func
        self.map_values = map_values

        # Add map init
        map_fields = list()
        for fld in self.map_keys:
            if fld == 'qid':
                map_fields.append(P4Field(layer=None, target_name="qid", sonata_name="qid",
                                          size=QID_SIZE))
            elif fld == 'count':
                map_fields.append(P4Field(layer=None, target_name="count", sonata_name="count",
                                          size=COUNT_SIZE))
            else:
                map_fields.append(self.p4_raw_fields.get_target_field(fld))

        map_fields_values = list()
        for fld in self.map_values:
            if fld == 'qid':
                map_fields_values.append(P4Field(layer=None, target_name="qid", sonata_name="qid",
                                          size=QID_SIZE))
            elif fld == 'count':
                map_fields_values.append(P4Field(layer=None, target_name="count", sonata_name="count",
                                          size=COUNT_SIZE))
            else:
                map_fields_values.append(self.p4_raw_fields.get_target_field(fld))

        # create ACTION using the function
        primitives = list()
        if len(func) > 0:
            self.func = func
            if func[0] == 'mask' or not func[0]:
                for field in map_fields:
                    mask_size = (func[1] / 4)
                    mask = '0x' + ('f' * mask_size) + ('0' * (HEADER_MASK_SIZE[field.target_name] - mask_size))
                    field_name = '%s.%s' % (self.meta_init_name, field.target_name.replace(".", "_"))
                    primitives.append(BitAnd(field_name, field_name, mask))
            if func[0] == 'set' or not func[0]:
                for field in map_fields_values:
                    field_name = '%s.%s' % (self.meta_init_name, field.target_name.replace(".", "_"))
                    primitives.append(ModifyField(field_name, func[1]))

        self.action = Action('do_%s' % self.operator_name, primitives)

        # create dummy TABLE to execute the action
        self.table = Table(self.operator_name, self.action.get_name(), [], None, 1)

    def __repr__(self):
        return '.Map(keys=' + str(self.keys) + ', map_keys=' + str(self.map_keys) + ', map_values=' + str(self.map_values) + ', func=' + str(self.func) + ')'

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
        return list(self.keys) + list(self.map_keys) + list(self.map_values)

    def get_out_headers(self):
        return list(self.keys) + list(self.map_keys) + list(self.map_values)


class P4Filter(P4Operator):
    def __init__(self, qid, operator_id, keys, filter_keys, func, source, match_action, miss_action, p4_raw_fields):
        super(P4Filter, self).__init__('Filter', qid, operator_id, keys, p4_raw_fields)

        self.filter_keys = filter_keys
        self.filter_mask = None
        self.filter_values = None
        self.func = None
        # self.out_headers = []
        self.match_action = match_action
        self.miss_action = miss_action

        self.source = source

        if not len(func) > 0 or func[0] == 'geq':
            self.logger.error('Got the following func with the Filter Operator: %s' % (str(func),))
            # raise NotImplementedError
        else:
            self.func = func[0]
            if func[0] == 'mask':
                self.filter_mask = func[1]
                self.filter_values = func[2:]
            elif func[0] == 'eq':
                self.filter_values = [func[1:]]

        reads_fields = list()
        for filter_key in self.filter_keys:
            if self.func == 'mask':
                reads_fields.append((filter_key, 'lpm'))
            else:
                reads_fields.append((filter_key, 'exact'))

        self.table = Table(self.operator_name, miss_action, (match_action,), reads_fields, TABLE_SIZE)

    def __repr__(self):
        return '.Filter(filter_keys=' + str(self.filter_keys) + ', func=' + str(self.func) + ', src = ' + str(
            self.source) + ')'

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
