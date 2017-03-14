#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

TABLE_WIDTH = 32
TABLE_SIZE = 4096
DISTINCT = 0
THRESHOLD = 2

header_map = {"sIP":"ipv4.srcAddr", "dIP":"ipv4.dstAddr",
            "sPort": "tcp.srcPort", "dPort": "tcp.dstPort",
            "nBytes": "ipv4.totalLen", "proto": "ipv4.protocol",
            "sMac": "ethernet.srcAddr", "dMac":"ethernet.dstAddr", "payload": ""}

header_size = {"sIP":32, "dIP":32, "sPort": 16, "dPort": 16,
               "nBytes": 16, "proto": 16, "sMac": 48, "dMac":48,
               "qid":16, "count": 16}


class MetaData(object):
    def __init__(self, name, fields={}):
        self.name = name
        self.fields = fields

    def add_metadata(self):
        out = 'header_type '+self.name+'_t {\n\tfields {\n\t\t'
        for fld in self.fields:
            if fld in header_size:
                out += fld+' : '+str(header_size[fld])+';\n\t\t'
            else:
                out += fld+' : '+str(self.fields[fld])+';\n\t\t'
        out = out[:-1]
        out += '}\n}\n\n'
        out += 'metadata '+self.name+'_t '+self.name+';\n\n'
        return out


class Register(object):
    def __init__(self, *args, **kwargs):
        (self.id, self.qid, self.mirror_id, self.width,
        self.instance_count, self.thresh) = args

        self.metadata_name = 'meta_' + self.operator_name
        self.hash_metadata_name = 'hash_meta_'+self.operator_name
        self.field_list_name = self.operator_name+'_fields'

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
        self.set_count = False

    def add_hash_metadata(self):
        self.hash_metadata = MetaData(name = self.hash_metadata_name)

        #print self.keys
        #print "Operator: ", self.operator_name
        self.hash_metadata.fields = {}
        for fld in self.keys:
            if '/' in fld:
                hdr = fld.split('/')[0]
                mask = fld.split('/')[1]
            else:
                hdr = fld
                mask = header_size[hdr]
            self.hash_metadata.fields[hdr] = mask
        #print self.hash_metadata.fields
        #print "Operator: ", self.operator_name+', fields:', self.hash_metadata.fields
        return self.hash_metadata.add_metadata()

    def add_metadata(self):
        # TODO: better set the size of value field in metadata
        self.metadata = MetaData(name = self.metadata_name,
                                fields = {'qid':self.qid_width,
                                        'idx': self.width,
                                        'val': self.width}
                                )
        return self.metadata.add_metadata()

    def add_field_list(self):
        out = 'field_list '+self.operator_name+'_fields {\n\t'
        for elem in self.hash_metadata.fields:
            out += self.hash_metadata.name+'.'+elem+';\n\t'
        out = out[:-1]
        out += '}\n\n'
        #print out
        return out

    def add_field_list_calculation(self):
        out = 'field_list_calculation '+self.operator_name+'_fields_hash {\n\t'
        out += 'input {\n\t\t'+self.field_list_name+';\n\t}\n\t'
        out += 'algorithm : crc32;\n\toutput_width : '+str(self.width)+';\n}\n\n'
        return out

    def add_register(self):
        out = 'register '+self.operator_name+'{\n\t'
        out += 'width : '+str(self.width)+';\n\tinstance_count : '+str(self.instance_count)+';\n}\n\n'
        return out

    def add_action_update(self):
        out = 'action update_'+self.operator_name+'_regs() {\n\t'
        out += 'bit_or('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+','+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', 1);\n\t'
        out += 'register_write('+self.operator_name+','+self.metadata.name+'.'+self.metadata.fields.keys()[2]+','+self.metadata.name+'.'+self.metadata.fields.keys()[1]+');\n}\n\n'
        return out

    def add_table_update(self):
        self.table_name = 'update_'+self.operator_name+'_counts'
        out = 'table update_'+self.operator_name+'_counts {\n\t'
        out += 'actions {update_'+self.operator_name+'_regs;}\n\t'
        out += 'size : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default update_'+self.operator_name+'_counts update_'+self.operator_name+'_regs')
        return out

    def add_table_start(self):
        out = 'action do_'+self.operator_name+'_hashes() {\n\t'
        for fld in self.hash_metadata.fields:
            meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
            out += 'modify_field('+self.hash_metadata.name+'.'+fld+', '+str(meta_fld)+');\n\t'
        out += 'modify_field('+self.metadata.name+'.'+self.metadata.fields.keys()[0]+', '+str(self.qid)+');\n\t'
        out += 'modify_field_with_hash_based_offset('+self.metadata.name+'.'+self.metadata.fields.keys()[2]+', 0, '
        out += self.operator_name+'_fields_hash, '+str(self.instance_count)+');\n\t'
        out += 'register_read('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', '+self.operator_name+', '+self.metadata.name+'.'+self.metadata.fields.keys()[2]+');\n'
        out += '}\n\n'
        #print out
        return out

    def add_action_start(self):
        out = 'table start_'+self.operator_name+' {\n\t'
        out += 'actions {do_'+self.operator_name+'_hashes;}\n\t'
        out += 'size : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default start_'+self.operator_name+' do_'+self.operator_name+'_hashes')
        return out

    def add_drop_action(self, id):
        out = 'table drop_'+self.operator_name+'_'+str(id)+' {\n\t'
        out += 'actions {mark_drop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default drop_'+self.operator_name+'_'+str(id)+' mark_drop')
        return out

    def add_skip_action(self, id):
        out = 'table skip_'+self.operator_name+'_'+str(id)+' {\n\t'
        out += 'actions {_nop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default skip_'+self.operator_name+'_'+str(id)+' _nop')
        return out

    def add_cond_actions(self, mode, ind):
        out = ''
        if mode == 0:
            act = self.pre_actions[ind]
        else:
            act = self.post_actions[ind]

        if act == 'drop':
            out += 'apply(drop_'+self.operator_name+'_'+str(self.drop_id)+');\n'
            self.p4_utils += self.add_drop_action(self.drop_id)
            self.drop_id += 1
        elif act == 'fwd':
            out += 'apply(skip_'+self.operator_name+'_'+str(self.skip_id)+');\n'
            self.p4_utils += self.add_skip_action(self.skip_id)
            self.skip_id += 1
        else:
            self.set_count = True
            out += 'apply(set_'+self.operator_name+'_count);'
        return out

    def add_register_preprocessing(self):
        out = ''
        if self.pre_actions.count('fwd') < 3:
            # then only we need to add condition
            out += '\t\t\t'+'if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' > '+str(self.thresh)+') {\n\t'
            out += '\t\t\t'+self.add_cond_actions(0, 0)
            out += '\t\t\t'+'}\n'
            out += '\t\t\t'+'else if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' == '+str(self.thresh)+') {\n\t'
            out += '\t\t\t'+self.add_cond_actions(0, 1)
            out += '\t\t\t'+'}\n'
            out += '\t\t\t'+'else {\n\t'
            out += '\t\t\t'+self.add_cond_actions(0, 2)
            out += '\t\t\t'+'}\n\n'
        #print out
        return out

    def add_register_postprocessing(self):
        out = ''
        if self.post_actions.count('fwd') < 3:
            # then only we need to add condition
            out += '\t\t\t'+'if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' > '+str(self.thresh)+') {\n\t'
            out += '\t\t\t'+self.add_cond_actions(1, 0)
            out += '\t\t\t'+'}\n'
            out += '\t\t\t'+'else if('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+' == '+str(self.thresh)+') {\n\t'
            out += '\t\t\t'+self.add_cond_actions(1, 1)
            out += '\t\t\t'+'}\n'
            out += '\t\t\t'+'else {\n\t'
            out += '\t\t\t'+self.add_cond_actions(1, 2)
            out += '\t\t\t'+'}\n\n'
        #print out
        return out

    def add_register_action(self):
        out = '\t\t\t'+'apply(update_'+self.operator_name+'_counts);\n'
        #print out
        return out

    def add_action_set(self):
        out = 'action set_'+self.operator_name+'_count() {\n'
        out += '\tmodify_field('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', 1);\n}\n\n'
        return out

    def add_table_set(self):
        out = 'table set_'+self.operator_name+'_count {\n\tactions {set_'+self.operator_name+'_count;}\n\
        size: 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default set_'+self.operator_name+'_count set_'+self.operator_name+'_count')
        return out

    def update_p4_state(self):
        self.p4_state += self.add_metadata()
        self.p4_state += self.add_hash_metadata()
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
        out = 'header_type out_header_'+str(self.qid)+'_t {\n'
        out += '\tfields {\n'

        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            out += '\t\t'+fld+' : '+str(header_size[fld])+';\n'
        out = out [:-1]
        out += '}\n}\n\n'
        out += 'header out_header_'+str(self.qid)+'_t out_header_'+str(self.qid)+';\n\n'
        return out

    def add_copy_fields(self):
        out = 'field_list copy_to_cpu_fields_'+str(self.qid)
        out += '{\n'
        out += '\tstandard_metadata;\n'
        out += '\t'+self.hash_metadata.name+';\n'
        out += '\t'+self.metadata.name+';\n'
        out += '\tmeta_map_init_'+str(self.qid)+';\n'
        out += '\tmeta_fm;\n'
        out += '}\n\n'

        out += 'action do_copy_to_cpu_'+str(self.qid)+'() {\n\tclone_ingress_pkt_to_egress('+str(self.mirror_id)+', copy_to_cpu_fields_'+str(self.qid)+');\n}\n\n'
        out += 'table copy_to_cpu_'+str(self.qid)+' {\n\tactions {do_copy_to_cpu_'+str(self.qid)+';}\n\tsize : 1;\n}\n\n'

        return out

    def add_encap_table(self):
        out = 'table encap_'+str(self.qid)+' {\n\tactions { do_encap_'+str(self.qid)+'; }\n\tsize : 1;\n}\n\n'
        return out

    def add_encap_action(self):
        out = 'action do_encap_'+str(self.qid)
        out += '() {\n\tadd_header(out_header_'+str(self.qid)+');\n\t'
        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            if fld in header_map:
                meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '
                out += meta_fld+ ');\n\t'
            elif fld in self.metadata.fields:
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld
                out += ', '+self.metadata.name+'.'+fld+');\n\t'
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
        self.name = "Distinct"
        self.operator_name = 'distinct_'+str(self.id)+'_'+str(self.qid)
        super(Distinct, self).__init__(*args, **kwargs)
        self.pre_actions = ('drop', 'fwd', 'drop')
        self.post_actions = ('fwd', 'fwd', 'fwd')

    def __repr__(self):
        return '.Distinct(keys='+str(self.keys)+')'

class Reduce(Register):
    def __init__(self, *args, **kwargs):
        (self.id, self.qid, self.mirror_id, self.width,
        self.instance_count, self.thresh) = args
        self.operator_name = 'reduce_'+str(self.id)+'_'+str(self.qid)
        self.name = "Reduce"
        super(Reduce, self).__init__(*args, **kwargs)
        # TODO: this sequence should be determined by the filter operation that follows this reduce operation
        # TODO: remove this hardcoding
        self.pre_actions = ('fwd', 'fwd', 'fwd')
        self.post_actions = ('set', 'fwd', 'drop')
        self.out_headers = tuple(list(self.out_headers)+['count'])

    def __repr__(self):
        return '.Reduce(keys=' + ','.join([x for x in self.keys]) + ', threshold='+str(self.thresh)+')'

    def add_action_update(self):
        out = 'action update_'+self.operator_name+'_regs() {\n\t'
        out += 'add_to_field('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', 1);\n\t'
        out += 'register_write('+self.operator_name+','+self.metadata.name+'.'+self.metadata.fields.keys()[2]+','+self.metadata.name+'.'+self.metadata.fields.keys()[1]+');\n}\n\n'
        return out

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n\tfields {\n\t\t'
        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
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
            if '/' in fld:
                fld = fld.split('/')[0]
            if fld in header_map:
                meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '+meta_fld+');\n\t'
            elif fld in self.metadata.fields:
                out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '+self.metadata.name+'.'+fld+');\n\t'
        out += 'modify_field(out_header_'+str(self.qid)+'.count, '+self.metadata.name+'.'+self.metadata.fields.keys()[1]+');\n\t'
        out = out [:-1]
        out += '}\n\n'
        return out

class Map(object):
    def __init__(self, *args, **kwargs):
        self.name = "Map"
        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.p4_init_commands = []
        self.id, self.qid, self.mirror_id = args

        map_dict = dict(**kwargs)
        self.map_keys = map_dict['map_keys']
        self.keys = map_dict['keys']
        self.func = map_dict['func']

        self.out_headers = tuple(['qid']+list(self.keys))
        self.expr = ''

        self.operator_name = 'map_'+str(self.qid)+'_'+str(self.id)

    def __repr__(self):
        return '.Map(keys='+str(self.keys)+', map_keys='+str(self.map_keys)+', func='+str(self.func)+')'

    def update_map_table(self):
        out = ''
        # Add match table for inital map operator
        out += 'table '+self.operator_name+'{\n'
        out += '\tactions{\n'
        out += '\t\tdo_'+self.operator_name+';\n'
        out += '\t}\n}\n\n'
        self.p4_init_commands.append('table_set_default '+self.operator_name+' do_'+str(self.operator_name))

        if len(self.func) > 0:
            out += 'action do_'+self.operator_name+'() {\n'
            if self.func[0] == 'mask':
                # TODO: add more functions to generalize this map operator
                mask = self.func[1]

                for fld in self.map_keys:
                    size = header_size[fld]
                    fs = int(mask)/4
                    zeros = size/4-fs
                    mask_str = '0x'
                    for i in range(fs):
                        mask_str += 'f'
                    for i in range(zeros):
                        mask_str += '0'
                    meta_init_name = 'meta_map_init_'+str(self.qid)
                    out += '\tbit_and('+meta_init_name+'.'+str(fld)+', '+meta_init_name+'.'+str(fld)+', '+mask_str+');\n'
                out += '}\n\n'
            else:
                # TODO add more functions for map operations
                raise NotImplementedError
                pass

        self.p4_state += out

    def update_p4_invariants(self):
        out = '#include "includes/headers.p4"\n'
        out += '#include "includes/parser.p4"\n\n'
        out += 'parser start {\n\treturn select(current(0, 64)) {\n\t\t0 : parse_out_header;\n\t\tdefault: parse_ethernet;\n\t}\n}\n'
        out += 'action _drop() {\n\tdrop();\n}\n\n'
        out += 'action _nop() {\n\tno_op();\n}\n\n'

        self.p4_invariants += out
        return out

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n'
        out += '\tfields {\n'

        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            out += '\t\t'+fld+' : '+str(header_size[fld])+';\n'
        out = out [:-1]
        out += '}\n}\n\n'
        out += 'header out_header_'+str(self.qid)+'_t out_header_'+str(self.qid)+';\n\n'
        return out

    def add_copy_fields(self):
        out = 'field_list copy_to_cpu_fields_'+str(self.qid)
        out += '{\n'
        out += '\tstandard_metadata;\n'
        out += '\tmeta_map_init_'+str(self.qid)+';\n'
        out += '\tmeta_fm;\n'
        out += '}\n\n'

        out += 'action do_copy_to_cpu_'+str(self.qid)+'() {\n\tclone_ingress_pkt_to_egress('+str(self.mirror_id)+', copy_to_cpu_fields_'+str(self.qid)+');\n}\n\n'
        out += 'table copy_to_cpu_'+str(self.qid)+' {\n\tactions {do_copy_to_cpu_'+str(self.qid)+';}\n\tsize : 1;\n}\n\n'

        return out

    def add_encap_table(self):
        out = 'table encap_'+str(self.qid)+' {\n\tactions { do_encap_'+str(self.qid)+'; }\n\tsize : 1;\n}\n\n'
        return out

    def add_encap_action(self):
        out = 'action do_encap_'+str(self.qid)
        out += '() {\n\tadd_header(out_header_'+str(self.qid)+');\n\t'
        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            #if fld in header_map:
            meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
            out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '
            out += meta_fld+ ');\n\t'
        out = out [:-1]
        out += '}\n\n'
        return out

    def update_p4_encap(self):
        self.p4_egress += self.add_out_header()
        self.p4_egress += self.add_copy_fields()
        self.p4_egress += self.add_encap_table()
        self.p4_egress += self.add_encap_action()

    def compile_dp(self):
        self.update_p4_invariants()
        self.update_map_table()
        self.update_p4_encap()


class Map_Init(object):
    def __init__(self, *args, **kwargs):
        self.name = "Map"
        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.p4_init_commands = []
        self.id, self.qid, self.mirror_id = args

        map_dict = dict(**kwargs)
        self.keys = map_dict['keys']

        self.out_headers = tuple(['qid']+list(self.keys))
        self.expr = ''

        self.operator_name = 'map_init_'+str(self.qid)

    def __repr__(self):
        return '.MapInit('+str(self.keys)+')'

    def update_map_table(self):
        out = ''

        # Add match table for inital map operator
        out += 'table '+self.operator_name+'{\n'
        out += '\tactions{\n'
        out += '\t\tdo_'+self.operator_name+';\n'
        out += '\t}\n}\n\n'
        self.p4_init_commands.append('table_set_default '+self.operator_name+' do_'+str(self.operator_name))

        out += 'action do_'+self.operator_name+'(){\n'
        fld = 'qid'
        out += '\tmodify_field(meta_'+self.operator_name+'.'+str(fld)+', '+str(self.qid)+');\n'
        for fld in self.keys:
            out += '\tmodify_field(meta_'+self.operator_name+'.'+str(fld)+', '+header_map[fld]+');\n'
        out += '}\n\n'

        out += 'header_type meta_'+self.operator_name+'_t {\n'
        out += '\t fields {\n'

        out += '\t\t'+ 'qid' + ': '+str(header_size['qid'])+';\n'
        for fld in self.keys:
            out += '\t\t'+ fld + ': '+str(header_size[fld])+';\n'
        out += '\t}\n}\n\n'

        out += 'metadata meta_'+self.operator_name+'_t meta_'+self.operator_name+';\n\n'


        self.p4_state += out

    def update_p4_invariants(self):
        out = '#include "includes/headers.p4"\n'
        out += '#include "includes/parser.p4"\n\n'
        out += 'parser start {\n\treturn select(current(0, 64)) {\n\t\t0 : parse_out_header;\n\t\tdefault: parse_ethernet;\n\t}\n}\n'
        out += 'action _drop() {\n\tdrop();\n}\n\n'
        out += 'action _nop() {\n\tno_op();\n}\n\n'

        self.p4_invariants += out
        return out

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n'
        out += '\tfields {\n'

        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            out += '\t\t'+fld+' : '+str(header_size[fld])+';\n'
        out = out [:-1]
        out += '}\n}\n\n'
        out += 'header out_header_'+str(self.qid)+'_t out_header_'+str(self.qid)+';\n\n'
        return out

    def add_copy_fields(self):
        out = 'field_list copy_to_cpu_fields_'+str(self.qid)
        out += '{\n'
        out += '\tstandard_metadata;\n'
        out += '\tmeta_map_init_'+str(self.qid)+';\n'
        out += '\tmeta_fm;\n'
        out += '}\n\n'

        out += 'action do_copy_to_cpu_'+str(self.qid)+'() {\n\tclone_ingress_pkt_to_egress('+str(self.mirror_id)+', copy_to_cpu_fields_'+str(self.qid)+');\n}\n\n'
        out += 'table copy_to_cpu_'+str(self.qid)+' {\n\tactions {do_copy_to_cpu_'+str(self.qid)+';}\n\tsize : 1;\n}\n\n'

        return out

    def add_encap_table(self):
        out = 'table encap_'+str(self.qid)+' {\n\tactions { do_encap_'+str(self.qid)+'; }\n\tsize : 1;\n}\n\n'
        return out

    def add_encap_action(self):
        out = 'action do_encap_'+str(self.qid)
        out += '() {\n\tadd_header(out_header_'+str(self.qid)+');\n\t'
        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            #if fld in header_map:
            meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
            out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '
            out += meta_fld+ ');\n\t'
        out = out [:-1]
        out += '}\n\n'
        return out

    def update_p4_encap(self):
        self.p4_egress += self.add_out_header()
        self.p4_egress += self.add_copy_fields()
        self.p4_egress += self.add_encap_table()
        self.p4_egress += self.add_encap_action()

    def compile_dp(self):
        #print "MapInit Compiling"
        self.update_p4_invariants()
        self.update_map_table()
        self.update_p4_encap()


class Filter(object):
    def __init__(self, *args, **kwargs):
        self.name = "Filter"
        self.operator_name = ""
        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.p4_init_commands = []
        self.filter_rules = ''
        self.expr = ''

        self.id, self.qid, self.mirror_id, self.filter_rules_id, self.filter_name = args
        self.operator_name = 'filter_'+str(self.qid)+'_'+str(self.id)

        map_dict = dict(**kwargs)
        self.filter_mask = ''
        self.filter_values = ()
        self.src = 0



        if 'filter_values' in map_dict:
            self.filter_values = map_dict['filter_values']

        self.keys = map_dict['keys']
        self.filter_keys = map_dict['filter_keys']
        self.func = map_dict['func']
        if len(self.func) > 0:
            if self.func[0] == 'mask':
                self.filter_mask = self.func[1]
                self.filter_values = self.func[2:]
            elif self.func[0] == 'eq':
                self.filter_values = self.func[1:]

        if 'src' in map_dict:
            self.src = map_dict['src']

        self.out_headers = tuple(['qid']+list(self.keys))

    def __repr__(self):
        return '.Filter(filter_keys='+str(self.filter_keys)+', func='+str(self.func)+', src = '+str(self.src)+')'


    def update_p4_invariants(self):
        out = '#include "includes/headers.p4"\n'
        out += '#include "includes/parser.p4"\n\n'
        out += 'parser start {\n\treturn select(current(0, 64)) {\n\t\t0 : parse_out_header;\n\t\tdefault: parse_ethernet;\n\t}\n}\n'
        out += 'action _drop() {\n\tdrop();\n}\n\n'
        out += 'action _nop() {\n\tno_op();\n}\n\n'

        self.p4_invariants += out
        return out

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n'
        out += '\tfields {\n'

        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            out += '\t\t'+fld+' : '+str(header_size[fld])+';\n'
        out = out [:-1]
        out += '}\n}\n\n'
        out += 'header out_header_'+str(self.qid)+'_t out_header_'+str(self.qid)+';\n\n'
        return out

    def add_copy_fields(self):
        out = 'field_list copy_to_cpu_fields_'+str(self.qid)
        out += '{\n'
        out += '\tstandard_metadata;\n'
        out += '\tmeta_map_init_'+str(self.qid)+';\n'
        out += '\tmeta_fm;\n'
        out += '}\n\n'

        out += 'action do_copy_to_cpu_'+str(self.qid)+'() {\n\tclone_ingress_pkt_to_egress('+str(self.mirror_id)+', copy_to_cpu_fields_'+str(self.qid)+');\n}\n\n'
        out += 'table copy_to_cpu_'+str(self.qid)+' {\n\tactions {do_copy_to_cpu_'+str(self.qid)+';}\n\tsize : 1;\n}\n\n'

        return out

    def add_encap_table(self):
        out = 'table encap_'+str(self.qid)+' {\n\tactions { do_encap_'+str(self.qid)+'; }\n\tsize : 1;\n}\n\n'
        return out

    def add_encap_action(self):
        out = 'action do_encap_'+str(self.qid)
        out += '() {\n\tadd_header(out_header_'+str(self.qid)+');\n\t'
        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            #if fld in header_map:
            meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
            out += 'modify_field(out_header_'+str(self.qid)+'.'+fld+', '
            out += meta_fld+ ');\n\t'
        out = out [:-1]
        out += '}\n\n'
        return out

    def update_p4_encap(self):
        self.p4_egress += self.add_out_header()
        self.p4_egress += self.add_copy_fields()
        self.p4_egress += self.add_encap_table()
        self.p4_egress += self.add_encap_action()

    def update_filter_tables(self):
        out = ''
        out += 'table '+self.filter_name+'{\n'
        out += '\treads {\n'
        print "Adding filter for", self.filter_name, self.func, self.filter_keys
        for key in self.filter_keys:
            if self.func[0] == 'mask':
                out += '\t\t'+str(header_map[key])+': lpm;\n'
            else:
                out += '\t\t'+str(header_map[key])+': exact;\n'
        out += '\t}\n'
        out += '\tactions{\n'
        out += '\t\tset_meta_fm_'+str(self.qid)+';\n'
        out += '\t\treset_meta_fm_'+str(self.qid)+';\n\t}\n}\n\n'
        self.p4_init_commands.append('table_set_default '+self.filter_name+' reset_meta_fm_'+str(self.qid))
        #self.filter_rules_id += 1
        for val in self.filter_values:
            self.p4_init_commands.append('table_add '+self.filter_name+' set_meta_fm_'+str(self.qid)+' '+str(val)+' =>')

        self.filter_rules += out

    def compile_dp(self):
        self.update_p4_invariants()
        self.update_filter_tables()
        self.update_p4_encap()


class QueryPipeline(object):
    '''Multiple packet streams can exist for a switch'''
    def __init__(self, id):
        self.qid = id
        self.mirror_id = 200+self.qid
        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_ingress_start = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.operators = []
        self.filter_rules = ''
        self.filter_control = ''
        self.filter_rules_id = 1
        self.src_2_filter_operator = {}
        self.p4_init_commands = []
        self.expr = 'In'
        self.refinement_filter_id = 0
        self.parse_payload = False

    def __repr__(self):
        expr = 'In\n'
        for operator in self.operators:
            expr += ''+operator.__repr__()+'\n'
        return expr

    def reduce(self, *args, **kwargs):
        id = len(self.operators)
        new_args = (id, self.qid, self.mirror_id, TABLE_WIDTH, TABLE_SIZE, THRESHOLD)+args
        map_dict = dict(*args, **kwargs)
        keys = map_dict['keys']
        values = ()
        func = ''
        if 'values' in map_dict:
            values = map_dict['values']
        if 'func' in map_dict:
            func = map_dict['func']

        operator = Reduce(*new_args, **kwargs)
        self.expr += '\n\t.Reduce(keys=' + ','.join([x for x in keys]) + ', values='+str(values)+', func='+str(func)+', threshold='+str(operator.thresh)+')'

        self.operators.append(operator)
        return self

    def distinct(self, *args, **kwargs):
        self.expr += '\n\t.Distinct()'
        id = len(self.operators)
        new_args = (id, self.qid, self.mirror_id, TABLE_WIDTH, TABLE_SIZE, DISTINCT)+args
        operator = Distinct(*new_args, **kwargs)
        self.operators.append(operator)
        return self

    def filter(self, *args, **kwargs):
        #print "Filter operator called ", self.expr, len(self.operators)
        map_dict = dict(**kwargs)
        filter_keys = map_dict['filter_keys']
        filter_mask = ()
        src = 0
        if 'src' in map_dict:
            src = map_dict['src']
        if 'mask' in map_dict:
            filter_mask = map_dict['mask']

        self.filter_rules_id = len(self.operators)
        filter_name = 'filter_'+str(self.qid)+'_'+str(self.filter_rules_id)

        id = len(self.operators)
        new_args = (id, self.qid, self.mirror_id, self.filter_rules_id, filter_name)+args
        self.operators.append(Filter(*new_args, **kwargs))
        self.src_2_filter_operator[src] = self.operators[-1]

        return self

    def map(self, *args, **kwargs):
        map_dict = dict(**kwargs)
        keys = map_dict['map_keys']
        func = map_dict['func']
        if len(func) > 0:
            id = len(self.operators)
            self.operators.append(Map(id, self.qid, self.mirror_id, *args, **kwargs))
            self.expr += '\n\t.Map(map_keys='+str(keys)+', func='+str(func)+')'
        return self

    def map_init(self, *args, **kwargs):
        map_dict = dict(**kwargs)
        self.keys = map_dict['keys']

        self.operators.append(Map_Init(id, self.qid, self.mirror_id, *args, **kwargs))
        self.expr += '\n\t.MapInit('+str(self.keys)+')'
        return self

    def update_p4_src(self):
        for operator in self.operators:
            operator.compile_dp()

        self.p4_invariants += self.operators[-1].p4_invariants
        self.p4_egress += self.operators[-1].p4_egress
        #print "Qid", self.qid, self.p4_egress

        for operator in self.operators:
            self.p4_utils += operator.p4_utils

        for src in self.src_2_filter_operator:
            filter_operator = self.src_2_filter_operator[src]
            # IR filters will have non-zero src value
            if src > 0:
                self.filter_control += '\t\tif (meta_fm.qid_'+str(self.qid)+'== 1){\n'
                self.filter_control += '\t\t\tapply('+filter_operator.filter_name+');\n'
                self.filter_control += '\t\t}\n'
            else:
                self.filter_control += '\t\tapply('+filter_operator.filter_name+');\n'

            self.filter_rules += filter_operator.filter_rules

        for operator in self.operators:
            self.p4_state += operator.p4_state

        #self.p4_ingress_start += '\tapply(map_init_'+str(self.qid)+');\n'
        for operator in self.operators:
            if operator.name not in ['Map','Filter']:
                self.p4_ingress_start += '\t\t\tapply(start_'+operator.operator_name+');\n'
            elif operator.name in ['Map']:
                self.p4_ingress_start += '\t\t\tapply('+operator.operator_name+');\n'

        self.p4_control = self.p4_control[:-1]

        for operator in self.operators:
            self.p4_control += operator.p4_control

        # Update all the initial commands
        for operator in self.operators:
            self.p4_init_commands += operator.p4_init_commands

    def compile_pipeline(self):
        self.update_p4_src()
