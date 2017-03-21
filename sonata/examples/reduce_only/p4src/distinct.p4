#include "includes/headers.p4"
#include "includes/parser.p4"
#define TABLE_WIDTH 16
#define TABLE_SIZE 4096
#define DISTINCT 0


header_type intrinsic_metadata_t {
	fields {
		tupleIndex : TABLE_WIDTH;
		dstIndex : TABLE_WIDTH;
		src : 32;
		dst : 32;
		distinctVal : 1;
		reduceVal : TABLE_WIDTH;

	}
}

header intrinsic_metadata_t imd;

register distinct {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

action _drop() {
    drop();
}


action _nop() {
}

field_list distinct_fields {
	ipv4.srcAddr;
	ipv4.dstAddr;
}


field_list_calculation distinct_fields_hash {
    input {
       distinct_fields;
    }
    algorithm : crc32;
    output_width : TABLE_WIDTH;
}


action do_hashes() {
    modify_field_with_hash_based_offset(imd.tupleIndex, 0, distinct_fields_hash, TABLE_SIZE);
    register_read(imd.distinctVal, distinct, imd.tupleIndex);
}


table start {
    actions {do_hashes;}
    size : 1;
}

action update_regs() {
    bit_or(imd.distinctVal, imd.distinctVal, 1);
    register_write(distinct,imd.tupleIndex,imd.distinctVal);
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

  if(imd.distinctVal == DISTINCT) {
    apply(update_counts);
    apply(copy_to_cpu);
	}
	else {
	  apply(skip1);
	}
}

action do_cpu_encap() {
    add_header(distinct_header);
    modify_field(distinct_header.sIP, ipv4.srcAddr);
    modify_field(distinct_header.dIP, ipv4.dstAddr);
    modify_field(distinct_header.count, 1);
}

table redirect {
    actions { do_cpu_encap; }
    size : 1;
}

control egress {
    apply(redirect);
}
