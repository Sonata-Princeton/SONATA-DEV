#include "includes/headers.p4"
#include "includes/parser.p4"
#define TABLE_WIDTH 16
#define TABLE_SIZE 1024
#define THRESHOLD 2


header_type intrinsic_metadata_t {
	fields {
		tupleIndex : TABLE_WIDTH;
		dstIndex : TABLE_WIDTH;
		src : 32;
		dst : 32;
		currentVal : TABLE_WIDTH;
		reduceVal : TABLE_WIDTH;

	}
}


header intrinsic_metadata_t imd;


register reduce {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

action _drop() {
    drop();
}


action _nop() {
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
    modify_field_with_hash_based_offset(imd.dstIndex, 0, reduce_fields_hash, TABLE_SIZE);
    register_read(imd.reduceVal, reduce, imd.dstIndex);
}


table start {
    actions {do_hashes;}
    size : 1;
}

action update_regs() {
   add_to_field(imd.reduceVal, 1);
   register_write(reduce, imd.dstIndex, imd.reduceVal);
}


table update_counts {
    actions {update_regs;}
    size : 1;
}

#define CPU_MIRROR_SESSION_ID                  250

field_list copy_to_cpu_fields {
    standard_metadata;
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


control ingress {

	apply(start);
	apply(update_counts);

  if(imd.reduceVal > THRESHOLD) {
    apply(copy_to_cpu);
	}
	else {
	  apply(skip1);
	}
}
