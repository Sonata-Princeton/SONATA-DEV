#include "includes/headers.p4"
#include "includes/parser.p4"
#define TABLE_WIDTH 32
#define TABLE_SIZE 1024
#define THRESHOLD 2
#define HASH_PRIME1 958704
#define HASH_PRIME2 966628

header_type meta_t {
	fields {
	    dstAddr1: 32;
		dstHash1 : 32;
		reduceCount1 : 8;

		dstAddr2: 32;
		dstHash2 : 32;
        reduceCount2 : 8;

        minCount: 8;
	}
}

metadata meta_t meta;

register reduce_hash1 {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

register reduce_hash2 {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

action _drop() {
    drop();
}

field_list reduce_fields1 {
	meta.dstAddr1;
}

field_list reduce_fields2 {
	meta.dstAddr2;
}

field_list_calculation reduce_fields_hash1 {
    input {
       reduce_fields1;
    }
    algorithm : crc32;
    output_width : TABLE_WIDTH;
}

field_list_calculation reduce_fields_hash2 {
    input {
       reduce_fields2;
    }
    algorithm : crc32;
    output_width : TABLE_WIDTH;
}

action do_hashes() {
    modify_field(meta.minCount, 255);
    //meta.minCount = meta.minCount.max;

    modify_field(meta.dstAddr1, ipv4.dstAddr);
    bit_xor(meta.dstAddr1, meta.dstAddr1, HASH_PRIME1);
    modify_field_with_hash_based_offset(meta.dstHash1, 0, reduce_fields_hash1, TABLE_SIZE);
    register_read(meta.reduceCount1, reduce_hash1, meta.dstHash1);

    modify_field(meta.dstAddr2, ipv4.dstAddr);
    bit_xor(meta.dstAddr2, meta.dstAddr2, HASH_PRIME2);
    modify_field_with_hash_based_offset(meta.dstHash2, 0, reduce_fields_hash2, TABLE_SIZE);
    register_read(meta.reduceCount2, reduce_hash2, meta.dstHash2);
}


table start {
    actions {do_hashes;}
    size : 1;
}

action update_regs() {
   add_to_field(meta.reduceCount1, 1);
   register_write(reduce_hash1, meta.dstHash1, meta.reduceCount1);

   add_to_field(meta.reduceCount2, 1);
   register_write(reduce_hash2, meta.dstHash2, meta.reduceCount2);
}


table update_hashes {
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
    modify_field(reduce_header.count, meta.minCount);
}


table redirect0 {
    actions { do_cpu_encap_val; }
    size : 1;
}

table apply_minCount1 {
    actions {
        updateMinCountFor1;
    }
    size : 1;
}

action updateMinCountFor1() {
    modify_field(meta.minCount, meta.reduceCount1);
}

table apply_minCount2 {
    actions {
        updateMinCountFor2;
    }
    size : 1;
}

action updateMinCountFor2() {
    modify_field(meta.minCount, meta.reduceCount2);
}


control update_min_count {
    if(meta.minCount > meta.reduceCount1) {
     apply(apply_minCount1);
    }

    if(meta.minCount > meta.reduceCount2) {
     apply(apply_minCount2);
    }
}

control ingress {
    apply(start);
    apply(update_hashes);
	apply(copy_to_cpu);
}

control egress {
    update_min_count();
    if (meta.minCount > THRESHOLD){
        apply(redirect0);
    }
    else {
        apply(skip1);

    }
}
