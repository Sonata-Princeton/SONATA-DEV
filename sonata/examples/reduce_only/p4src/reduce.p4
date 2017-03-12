#include "includes/headers.p4"
#include "includes/parser.p4"
#define TABLE_WIDTH 32
#define TABLE_SIZE 1024
#define THRESHOLD 2

header_type meta_t {
	fields {
		dstIndex : 32;
		reduceVal : 8;
	}
}

metadata meta_t meta;

register reduce {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

action _drop() {
    drop();
}

field_list reduce_fields {
	ipv4.dstAddr;
}

field_list_calculation reduce_fields_hash {
    input {
       reduce_fields;
    }
    algorithm : crc32;
    output_width : TABLE_WIDTH;
}

action do_hashes() {
    modify_field_with_hash_based_offset(meta.dstIndex, 0, reduce_fields_hash, TABLE_SIZE);
    register_read(meta.reduceVal, reduce, meta.dstIndex);
}


table start {
    actions {do_hashes;}
    size : 1;
}

action update_regs() {
   add_to_field(meta.reduceVal, 1);
   register_write(reduce, meta.dstIndex, meta.reduceVal);
}


table update_counts {
    actions {update_regs;}
    size : 1;
}

#define CPU_MIRROR_SESSION_ID                  250

field_list copy_to_cpu_fields {
    standard_metadata;
		meta;
}

action do_copy_to_cpu() {
    clone_ingress_pkt_to_egress(CPU_MIRROR_SESSION_ID, copy_to_cpu_fields);
}

table copy_to_cpu {
    actions {do_copy_to_cpu;}
    size : 1;
}

table skip1 {
    actions {_drop;}
    size : 1;
}


action do_cpu_encap_val() {
    add_header(reduce_header);
    modify_field(reduce_header.dIP, ipv4.dstAddr);
    modify_field(reduce_header.count, meta.reduceVal);
}

action do_cpu_encap_one() {
    add_header(reduce_header);
    modify_field(reduce_header.dIP, ipv4.dstAddr);
    modify_field(reduce_header.count, 1);
}


table redirect0 {
    actions { do_cpu_encap_val; }
    size : 1;
}

table redirect1 {
    actions { do_cpu_encap_one; }
    size : 1;
}

control ingress {


	apply(copy_to_cpu);
}

control egress {
		apply(start);
		apply(update_counts);
		if (meta.reduceVal >= THRESHOLD){
			apply(redirect0);
		}
		else{
			apply(skip1);
		}

}
