TABLE_WIDTH = 16
TABLE_SIZE = 4096
DISTINCT = 0
THRESHOLD = 2

header_map = {"sIP":"ipv4.srcAddr", "dIP":"ipv4.dstAddr",
            "dIP/16":"ipv4.dstAddr", "dIP/32":"ipv4.dstAddr",
            "sPort": "tcp.srcPort", "dPort": "tcp.dstPort",
            "nBytes": "ipv4.totalLen", "proto": "ipv4.protocol",
            "sMac": "ethernet.srcAddr", "dMac":"ethernet.dstAddr"}

header_size = {"sIP":32, "dIP":32, "sPort": 16, "dPort": 16,
                "dIP/16":16, "dIP/32":32,
                "nBytes": 16, "proto": 8, "sMac": 48, "dMac":48,
                "qid":8, "count": 12}

class GlobalCounts(object):
    # maintain global counts for skip and drop actions
    # as we cannot re-use these tables
    def __init__(self):
        self.skip_id = 1
        self.drop_id = 1

class MetaData(object):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def add_metadata(self):
        out = 'header_type '+self.name+'_t {\n\tfields {\n\t\t'
        for fld in self.fields:
            out += fld+' : '+str(self.fields[fld])+';\n\t\t'
        out = out[:-1]
        out += '}\n}\n\n'
        out += 'metadata '+self.name+'_t '+self.name+';\n\n'
        return out

class Register(object):
    def __init__(self, *args, **kwargs):
        (self.id, self.qid, self.mirror_id, self.width,
        self.instance_count, self.thresh) = args

        self.metadata_name = 'meta_'+self.register_name
        self.field_list_name = self.register_name+'_fields'

        map_dict = dict(**kwargs)
        self.keys = map_dict['keys']
        self.out_headers = tuple(['qid']+list(self.keys))

        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.p4_init_commands = []

        self.skip_id = 1
        self.drop_id = 1

        self.qid_width = 8

    def add_metadata(self):
        # TODO: better set the size of value field in metadat
        self.metadata = MetaData(name = self.metadata_name,
                                fields = {'qid':self.qid_width,
                                        'idx': self.width,
                                        'val': self.width}
                                )
        return self.metadata.add_metadata()

    def add_field_list(self):
        out = 'field_list '+self.register_name+'_fields {\n\t'
        for elem in self.keys:
            out += header_map[elem]+';\n\t'
        out = out[:-1]
        out += '}\n\n'
        return out

    def add_field_list_calculation(self):
        out = 'field_list_calculation '+self.register_name+'_fields_hash {\n\t'
        out += 'input {\n\t\t'+self.field_list_name+';\n\t}\n\t'
        out += 'algorithm : crc32;\n\toutput_width : '+str(self.width)+';\n}\n\n'
        return out

    def add_register(self):
        out = 'register '+self.register_name+'{\n\t'
        out += 'width : '+str(self.width)+';\n\tinstance_count : '+str(self.instance_count)+';\n}\n\n'
        return out

    def add_action_update(self):
        out = 'action update_'+self.register_name+'_regs() {\n\t'
        out += 'bit_or('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+','+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', 1);\n\t'
        out += 'register_write('+self.register_name+','+self.metadata.name+'.'+self.metadata.fields.keys()[2]+','+self.metadata.name+'.'+self.metadata.fields.keys()[1]+');\n}\n\n'
        return out

    def add_table_update(self):
        out = 'table update_'+self.register_name+'_counts {\n\t'
        out += 'actions {update_'+self.register_name+'_regs;}\n\t'
        out += 'size : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default update_'+self.register_name+'_counts update_'+self.register_name+'_regs')
        return out

    def add_table_start(self):
        out = 'action do_'+self.register_name+'_hashes() {\n\t'
        out += 'modify_field_with_hash_based_offset('+self.metadata.name+'.'+self.metadata.fields.keys()[0]+', 0,'
        out += self.register_name+'_fields_hash , '+str(self.instance_count)+');\n\t'
        out += 'register_read('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', '+self.register_name+', '+self.metadata.name+'.'+self.metadata.fields.keys()[2]+');\n'
        out += '}\n\n'
        return out

    def add_action_start(self):
        out = 'table start_'+self.register_name+' {\n\t'
        out += 'actions {do_'+self.register_name+'_hashes;}\n\t'
        out += 'size : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default start_'+self.register_name+' do_'+self.register_name+'_hashes')
        return out

    def add_drop_action(self, id):
        out = 'table drop_'+self.register_name+'_'+str(id)+' {\n\t'
        out += 'actions {_drop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default drop_'+self.register_name+'_'+str(id)+' _drop')
        return out

    def add_skip_action(self, id):
        out = 'table skip_'+self.register_name+'_'+str(id)+' {\n\t'
        out += 'actions {_nop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default skip_'+self.register_name+'_'+str(id)+' _nop')
        return out

    def add_cond_actions(self, mode, ind):
        out = ''
        if mode == 0:
            act = self.pre_actions[ind]
        else:
            act = self.post_actions[ind]

        if act == 'drop':
            out += 'apply(drop_'+self.register_name+'_'+str(self.drop_id)+');\n'
            self.p4_utils += self.add_drop_action(self.drop_id)
            self.drop_id += 1
        elif act == 'fwd':
            out += 'apply(skip_'+self.register_name+'_'+str(self.skip_id)+');\n'
            self.p4_utils += self.add_skip_action(self.skip_id)
            self.skip_id += 1
        else:
            out += 'apply(set_'+self.register_name+'_count);'
        return out


    def add_register_preprocessing(self):
        out = ''
        if self.pre_actions.count('fwd') < 3:
            # then only we need to add condition
            out += '\t'+'if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' > '+str(self.thresh)+') {\n\t'
            out += '\t'+self.add_cond_actions(0, 0)
            out += '\t'+'}\n'
            out += '\t'+'else if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' == '+str(self.thresh)+') {\n\t'
            out += '\t'+self.add_cond_actions(0, 1)
            out += '\t'+'}\n'
            out += '\t'+'else {\n\t'
            out += '\t'+self.add_cond_actions(0, 2)
            out += '\t'+'}\n\n'
        #print out
        return out

    def add_register_postprocessing(self):
        out = ''
        if self.post_actions.count('fwd') < 3:
            # then only we need to add condition
            out += '\t'+'if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' > '+str(self.thresh)+') {\n\t'
            out += '\t'+self.add_cond_actions(1, 0)
            out += '\t'+'}\n'
            out += '\t'+'else if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' == '+str(self.thresh)+') {\n\t'
            out += '\t'+self.add_cond_actions(1, 1)
            out += '\t'+'}\n'
            out += '\t'+'else {\n\t'
            out += '\t'+self.add_cond_actions(1, 2)
            out += '\t'+'}\n\n'
        #print out
        return out

    def add_register_action(self):
        out = '\t'+'apply(update_'+self.register_name+'_counts);\n'
        #print out
        return out

    def add_action_set(self):
        out = 'action set_'+self.register_name+'_count() {\n\tmodify_field('+self.metadata.name+'.'+self.metadata.fields.keys()[0]+', 1);\n}\n\n'
        return out

    def add_table_set(self):
        out = 'table set_'+self.register_name+'_count {\n\tactions {set_'+self.register_name+'_count;}\n\
        size: 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default set_'+self.register_name+'_count set_'+self.register_name+'_count')
        return out

    def update_p4_state(self):
        self.p4_state += self.add_metadata()
        self.p4_state += self.add_field_list()
        self.p4_state += self.add_field_list_calculation()
        self.p4_state += self.add_register()
        self.p4_state += self.add_action_update()
        self.p4_state += self.add_table_update()
        self.p4_state += self.add_table_start()
        self.p4_state += self.add_action_start()
        self.p4_state += self.add_action_set()
        self.p4_state += self.add_table_set()

    def update_p4_control(self):
        self.p4_control += self.add_register_preprocessing()
        self.p4_control += self.add_register_action()
        self.p4_control += self.add_register_postprocessing()

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n\tfields {\n\t\t'

        for fld in self.out_headers:
            out += fld+' : '+str(header_size[fld])+';\n\t\t'
        out = out [:-1]
        out += '}\n}\n\n'
        out += 'header out_header_'+str(self.qid)+'_t out_header_'+str(self.qid)+';\n\n'
        return out

    def add_copy_fields(self):
        out = 'field_list copy_to_cpu_fields_'+str(self.qid)
        out += '{\n\tstandard_metadata;\n\t'+self.metadata.name+';\n}\n\n'

        out += 'action do_copy_to_cpu_'+str(self.qid)+'() {\n\tclone_ingress_pkt_to_egress('+str(self.mirror_id)+', copy_to_cpu_fields_'+str(self.qid)+');\n}\n\n'
        out += 'table copy_to_cpu_'+str(self.qid)+' {\n\tactions {do_copy_to_cpu_'+str(self.qid)+';}\n\tsize : 1;\n}\n\n'
        return out

    def add_encap_table(self):
        out = 'table encap_'+str(self.qid)+' {\n\tactions { do_encap_'+str(self.qid)+'; }\n\tsize : 1;\n}\n\n'
        return out

    def add_encap_action(self):
        out = 'action do_encap_'+str(self.qid)+'() {\n\tadd_header(out_header_'+str(self.qid)+');\n\t'
        for fld in self.out_headers:
            if fld in header_map:
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '+header_map[fld]+');\n\t'
            elif fld in self.metadata.fields:
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '+self.metadata.name+'.'+fld+');\n\t'
        out = out [:-1]
        out += '}\n\n'
        return out

    def update_p4_invariants(self):
        out = '#include "includes/headers.p4"\n'
        out += '#include "includes/parser.p4"\n\n'
        out += 'parser start {\n\treturn select(current(0, 64)) {\n\t\t0 : parse_out_header;\n\t\tdefault: parse_ethernet;\n\t}\n}\n'
        out += 'action _drop() {\n\tdrop();\n}\n\n'
        out += 'action _nop() {\n\tno_op();\n}\n\n'

        self.p4_invariants += out
        return out

    def update_p4_encap(self):
        self.p4_egress += self.add_out_header()
        self.p4_egress += self.add_copy_fields()
        self.p4_egress += self.add_encap_table()
        self.p4_egress += self.add_encap_action()

    def compile_dp(self):
        self.update_p4_invariants()
        self.update_p4_state()
        self.update_p4_control()
        self.update_p4_encap()

class Distinct(Register):
    def __init__(self, *args, **kwargs):
        (self.id, self.qid, self.mirror_id, self.width,
        self.instance_count, self.thresh) = args
        self.register_name = 'distinct_'+str(self.id)+'_'+str(self.qid)
        super(Distinct, self).__init__(*args, **kwargs)
        self.pre_actions = ('drop', 'fwd', 'drop')
        self.post_actions = ('fwd', 'fwd', 'fwd')



class Reduce(Register):
    def __init__(self, *args, **kwargs):
        (self.id, self.qid, self.mirror_id, self.width,
        self.instance_count, self.thresh) = args
        self.register_name = 'reduce_'+str(self.id)+'_'+str(self.qid)
        super(Reduce, self).__init__(*args, **kwargs)
        self.pre_actions = ('fwd', 'fwd', 'fwd')
        self.post_actions = ('set', 'fwd', 'drop')
        self.out_headers = tuple(['count']+list(self.out_headers))


    def add_action_update(self):
        out = 'action update_'+self.register_name+'_regs() {\n\t'
        out += 'add_to_field('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', 1);\n\t'
        out += 'register_write('+self.register_name+','+self.metadata.name+'.'+self.metadata.fields.keys()[2]+','+self.metadata.name+'.'+self.metadata.fields.keys()[1]+');\n}\n\n'
        return out

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n\tfields {\n\t\t'
        for fld in self.out_headers:
            out += fld+' : '+str(header_size[fld])+';\n\t\t'

        # for reduce add the count value as part of out header
        #out += 'count : '+str(8)+';\n\t\t'
        out = out [:-1]
        out += '}\n}\n\n'
        out += 'header out_header_'+str(self.qid)+'_t out_header_'+str(self.qid)+';\n\n'
        return out

    def add_encap_action(self):
        out = 'action do_encap_'+str(self.qid)+'() {\n\tadd_header(out_header_'+str(self.qid)+');\n\t'
        for fld in self.out_headers:
            if fld in header_map:
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '+header_map[fld]+');\n\t'
            elif fld in self.metadata.fields:
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '+self.metadata.name+'.'+fld+');\n\t'
        out += 'modify_field(out_header_'+str(self.qid)+'.count, '+self.metadata.name+'.'+self.metadata.fields.keys()[1]+');\n\t'
        out = out [:-1]
        out += '}\n\n'
        return out

class PacketStream(object):
    '''Multiple packet streams can exist for a switch'''
    def __init__(self,id):
        self.qid = id
        self.mirror_id = 200+self.qid
        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.operators = []
        self.p4_init_commands = []

    def reduce(self, *args, **kwargs):
        id = len(self.operators)
        new_args = (id, self.qid, self.mirror_id, TABLE_WIDTH, TABLE_SIZE, DISTINCT)+args
        operator = Reduce(*new_args, **kwargs)
        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        id = len(self.operators)
        new_args = (id, self.qid, self.mirror_id, TABLE_WIDTH, TABLE_SIZE, DISTINCT)+args
        operator = Distinct(*new_args, **kwargs)
        self.operators.append(operator)
        return self

    def update_p4_src(self):


        for operator in self.operators:
            operator.compile_dp()

        self.p4_invariants += self.operators[0].p4_invariants
        self.p4_egress += self.operators[-1].p4_egress

        for operator in self.operators:
            self.p4_utils += operator.p4_utils

        for operator in self.operators:
            self.p4_state += operator.p4_state

        for operator in self.operators:
            self.p4_control += 'apply(start_'+operator.register_name+');\n\t'
        self.p4_control = self.p4_control[:-1]

        for operator in self.operators:
            self.p4_control += operator.p4_control

        self.p4_control += '\tapply(copy_to_cpu_'+str(self.qid)+');'

        # Update all the initial commands
        for operator in self.operators:
            self.p4_init_commands += operator.p4_init_commands

    def compile_pipeline(self):
        self.update_p4_src()
