#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import sys
import random
import math
from p4_queries import MetaData, header_map, header_size


class CMSketch(object):
    prime_numbers = [926998, 925304, 951158, 962818, 933978, 978306, 984070, 993830, 994332, 920996]

    def __init__(self, *args, **kwargs):
        #(id, qid, mirror_id, CMS_M_COLS, CMS_K, CMS_MAX_VAL, thresh

        (self.id, self.qid, self.mirror_id, self.CMS_M, self.CMS_K,
           self.CMS_MAX_VAL, self.thresh) = args

        self.CMS_INDEX_WIDTH = int(math.ceil(math.log(self.CMS_M,2)))
        self.CMS_VAL_WIDTH = int(math.ceil(math.log(self.CMS_MAX_VAL,2)))

        # R is fixed for each value of K, index on K
        self.CMS_R_WIDTH = 32;
        self.CMS_R = self.get_random_numbers()
        self.name = "CMSketch"
        self.operator_name = 'cms'+str(self.id)+'_'+str(self.qid)

        self.pre_actions = ('fwd', 'fwd', 'fwd')
        self.post_actions = ('set', 'fwd', 'drop')

        self.metadata_name = 'meta_'+self.operator_name
        self.hash_metadata_name = 'hash_meta_'+self.operator_name
        self.field_list_name = self.operator_name+'_fields'

        map_dict = dict(**kwargs)
        self.keys = map_dict['keys']
        self.out_headers = tuple(['qid']+list(self.keys))
        
        self.hash_alg = 'crc32'
        self.hash_output_width = 32
        self.qid_width = header_size['qid']
        self.val_width = 96

        self.p4_state = ''
        self.p4_utils = ''
        self.p4_control = ''
        self.p4_egress = ''
        self.p4_invariants = ''
        self.p4_init_commands = []
        self.table_name = ''

        self.skip_id = 1
        self.drop_id = 1

        self.set_count = False

    def get_random_numbers(self):
        hash_primes = {}
        for elem in range(1, self.CMS_K+1):
            tmp = random.getrandbits(self.CMS_R_WIDTH)
            hash_primes[elem] = tmp
        return hash_primes

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

        for did in range(1, self.CMS_K+1):
            hdr = 'R_' + str(did)
            self.hash_metadata.fields[hdr] = self.CMS_R_WIDTH;
        print self.hash_metadata.fields

        #print self.hash_metadata.fields
        #print "Operator: ", self.operator_name+', fields:', self.hash_metadata.fields

        return self.hash_metadata.add_metadata()

    def add_metadata(self):
        # TODO: better set the size of value field in metadata
        self.metadata = MetaData(name = self.metadata_name,
                                 fields = {'qid':self.qid_width, 'val':self.CMS_VAL_WIDTH})
        for did in range(1, self.CMS_K+1):
            self.metadata.fields['idx_'+str(did)] = self.CMS_INDEX_WIDTH
            self.metadata.fields['val_'+str(did)] = self.CMS_VAL_WIDTH
        print self.metadata.fields
        return self.metadata.add_metadata()

    def add_field_list(self):
        out = ''
        for did in range(1, 1+self.CMS_K):
            out += 'field_list '+self.operator_name+'_'+str(did)+'_fields {\n\t'
            for elem in self.hash_metadata.fields:
                if not(elem.startswith("R",0)):
                    out += self.hash_metadata.name+'.'+elem+';\n\t'
            out += self.hash_metadata.name+".R_"+str(did)+';\n\t'
            out = out[:-1]
            out += '}\n\n'

        print out
        return out

    def add_field_list_calculation(self):
        out = ''
        for did in range(1, 1+self.CMS_K):
            out += 'field_list_calculation '+self.operator_name+'_'+str(did)+'_fields_hash {\n\t'
            out += 'input {\n\t\t'+self.operator_name+'_'+str(did)+'_fields'+';\n\t}\n\t'
            out += 'algorithm : '+ str(self.hash_alg) + ';\n\toutput_width : ' +str(self.hash_output_width) + ';\n}\n\n'
        print out
        return out
    def add_register(self):
        out = ''
        for did in range(1, 1+self.CMS_K):
            out += 'register '+self.operator_name+'_'+str(did)+'{\n\t'
            out += 'width : '+str(self.CMS_VAL_WIDTH)+';\n\tinstance_count :' + str(self.CMS_M)+';\n}\n\n'
            print out
        return out

    def add_action_update(self):
        out = ''
        out += 'action update_'+self.operator_name+'_regs() {\n'
        for did in range(1, 1+self.CMS_K):
            out += '\tadd_to_field('+self.metadata.name+'.val_'+str(did)+', 1);\n\t'
            out += 'register_write('+self.operator_name+'_'+str(did)+', '+self.metadata.name+'.idx_'+str(did)+', '+self.metadata.name+'.val_'+str(did)+');\n'
        out += '}\n\n'
        print out
        return out

    def add_table_update(self):
        out = ''
        self.table_name = 'update_'+self.operator_name+'_counts'
        out += 'table update_'+self.table_name+' {\n\t'
        out += 'actions {update_'+self.operator_name+'_regs;}\n\t'
        out += 'size : 1;\n'
        out += '}\n\n'
        R_VALS = map(lambda x: str(self.CMS_R[x]),range(1, self.CMS_K+1))
        self.p4_init_commands.append('table_set_default '+self.table_name+' update_'+self.operator_name+'_regs')
        self.p4_init_commands.append('table_add '+self.table_name+' => '+ " ".join(R_VALS))
        print out
        return out

    def add_action_start(self):
        args = ",".join(map(lambda x : "r"+str(x), range(1,self.CMS_K+1)))
        out = 'action do_'+self.operator_name+'_hashes('+args+') {'
        for i in range(1,self.CMS_K+1):
            out += '\n\tmodify_field('+self.hash_metadata.name+'.R_'+str(i)+", r"+str(i)+");"
        for fld in self.hash_metadata.fields:
            if not(fld.startswith("R_")): 
                meta_fld = 'meta_map_init_'+str(self.qid)+'.'+fld
                out += '\n\tmodify_field('+self.hash_metadata.name+'.'+fld+', '+str(meta_fld)+');'
            else:
            #out += 'bit_xor('+self.hash_metadata.name+'.'+fld+', '+self.hash_metadata.name+'.'+fld+', '+str(self.hash_primes[did])+');\n\t'
                did = int(fld.split('_')[1])
                out += '\n\tmodify_field_with_hash_based_offset('+self.metadata.name+'.idx_'+str(did)+', 0, '
                out += self.operator_name+'_'+str(did)+'_fields_hash, '+str(self.CMS_M)+');'
                out += '\n\tregister_read('+self.metadata.name+'.val_'+str(did)+', '+self.operator_name+'_'+str(did)+', '+self.metadata.name+'.idx_'+str(did)+');'
        out += '\n\tmodify_field('+self.metadata.name+'.val, '+ self.metadata.name+'.val_1)'
        out += '\n}\n\n'
        print out
        return out

    def add_table_start(self):
        out = 'table start_'+self.operator_name+' {\n\t'
        out += 'actions {do_'+self.operator_name+'_hashes;}\n\t'
        out += 'size : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default start_'+self.operator_name+' do_'+self.operator_name+'_hashes')
        print out
        return out

    def add_drop_action(self, id):
        out = 'table drop_'+self.operator_name+'_'+str(self.id)+' {\n\t'
        out += 'actions {mark_drop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default drop_'+self.operator_name+'_'+str(self.id)+' mark_drop')
        return out

    def add_skip_action(self, id):
        out = 'table skip_'+self.operator_name+'_'+str(self.id)+' {\n\t'
        out += 'actions {_nop;}\n\tsize : 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default skip_'+self.operator_name+'_'+str(self.id)+' _nop')
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
            out += '\t\t\t'+'if('+self.metadata.name+'.val > '+str(self.thresh)+') {\n\t'
            out += '\t\t\t'+self.add_cond_actions(1, 0)
            out += '\n\t\t\t'+'}\n'
            out += '\t\t\t'+'else if('+self.metadata.name+'.val == '+str(self.thresh)+') {\n\t'
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

    def add_count_min_control(self):
        out = ''
        # Add all update actions
        for did in range(2, 1+self.CMS_K):
            out += 'action updateMinCountFor_'+self.operator_name+'_'+str(did)+'() {\n\t'
            out += 'modify_field('+self.metadata.name+'.val,'+self.metadata.name+'.val'+str(did)+');\n}\n\n'

        # Add all update tables
        for did in range(2, 1+self.CMS_K):
            out += 'table apply_minCount_'+self.operator_name+'_'+str(did)+'{\n\t'
            out += 'actions{\n\t\t'
            out += 'updateMinCountFor_'+self.operator_name+'_'+str(did)+';\n\t}\n\tsize: 1;\n}\n\n'

        # Add the control function
        out += 'control update_'+self.operator_name+'_count() {\n\t'
        for did in range(2,1+self.CMS_K):
            out += 'if('+self.metadata.name+'.val > '+self.metadata.name+'.val_'+str(did)+'){\n\t\t'
            out += 'apply('+'apply_minCount_'+self.operator_name+'_'+str(did)+');\n\t}\n\n\t'
        out = out[:-1]
        out += '}\n\n'
        print out
        return out

    def add_action_set(self):
        out = 'action set_'+self.operator_name+'_count {\n'
        out += '\tmodify_field('+self.metadata.name+'.'+self.metadata.fields.keys()[1]+', 1);\n}\n\n'
        print out
        return out

    def add_table_set(self):
        out = 'table set_'+self.operator_name+'_count {\n\tactions {set_'+self.operator_name+'_count;}\n\
        size: 1;\n}\n\n'
        self.p4_init_commands.append('table_set_default set_'+self.operator_name+'_count set_'+self.operator_name+'_count')
        return out

    def add_sketch_control(self):
        out = ''
        out += self.add_register_preprocessing()
        out += self.add_register_action()
        out += '\t\t\t'+'update_'+self.operator_name+'_count_min();\n'
        out += self.add_register_postprocessing()
        print out
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
        self.p4_state += self.add_count_min_control()
        self.p4_state += self.add_sketch_control()
        return self.p4_state

    def update_p4_control(self):
        out = ''
        out += 'update_'+self.operator_name+'_count();\n'
        self.p4_control = out
        return out

    def add_out_header(self):
        out = 'header_type out_header_'+str(self.qid)+'_t {\n'
        out += '\tfields {\n'

        for fld in self.out_headers:
            if '/' in fld:
                fld = fld.split('/')[0]
            out += '\t\t'+fld+' : '+str(header_size[fld])+';\n'
        out += '\t\t'+'count : ' + str(self.CMS_VAL_WIDTH)+';\n'
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
        return self.p4_egress

    def compile_dp(self):
        out = ''
        out += self.update_p4_invariants()
        out += self.update_p4_state()
        out += self.update_p4_control()
        out += self.update_p4_encap()
        return out

if __name__ == "__main__":
    #(id, qid, mirror_id, CMS_M_COLS, CMS_K, CMS_MAX_VAL, thresh
    s = CMSketch(1, 1, 10, 1024, 3, 2**32, 7, keys=('dIP/24',))
    print s.compile_dp()
    print map(lambda x:sys.stdout.write(x+'\n'),s.p4_init_commands)