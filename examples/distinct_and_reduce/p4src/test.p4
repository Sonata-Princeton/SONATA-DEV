#include "includes/headers.p4"
#include "includes/parser.p4"

parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}
action _drop() {
	drop();
}

action _nop() {
	no_op();
}

parser parse_out_header {
	extract(out_header_1);
	return parse_ethernet;
}

header_type out_header_1_t {
	fields {
		qid : 8;
		sIP : 32;
		dIP : 32;
	}
}

header out_header_1_t out_header_1;

field_list copy_to_cpu_fields_1{
	standard_metadata;
	meta_distinct_0_1;
}

action do_copy_to_cpu_1() {
	clone_ingress_pkt_to_egress(201, copy_to_cpu_fields_1);
}

table copy_to_cpu_1 {
	actions {do_copy_to_cpu_1;}
	size : 1;
}

table encap_1 {
	actions { do_encap_1; }
	size : 1;
}

action do_encap_1() {
	add_header(out_header_1);
	modify_field(out_header_1.qid, meta_distinct_0_1.qid);
	modify_field(out_header_1.sIP, hash_meta_distinct_0_1.sIP);
	modify_field(out_header_1.dIP, hash_meta_distinct_0_1.dIP);
}

table drop_distinct_0_1_1 {
	actions {_drop;}
	size : 1;
}

table skip_distinct_0_1_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_0_1_2 {
	actions {_drop;}
	size : 1;
}

header_type meta_distinct_0_1_t {
	fields {
		qid : 8;
		val : 16;
		idx : 16;
	}
}

metadata meta_distinct_0_1_t meta_distinct_0_1;

header_type hash_meta_distinct_0_1_t {
	fields {
		sIP : 32;
		dIP : 16;
	}
}

metadata hash_meta_distinct_0_1_t hash_meta_distinct_0_1;

field_list distinct_0_1_fields {
	hash_meta_distinct_0_1.sIP;
	hash_meta_distinct_0_1.dIP;
}

field_list_calculation distinct_0_1_fields_hash {
	input {
		distinct_0_1_fields;
	}
	algorithm : crc32;
	output_width : 16;
}

register distinct_0_1{
	width : 16;
	instance_count : 4096;
}

action update_distinct_0_1_regs() {
	bit_or(meta_distinct_0_1.val,meta_distinct_0_1.val, 1);
	register_write(distinct_0_1,meta_distinct_0_1.idx,meta_distinct_0_1.val);
}

table update_distinct_0_1_counts {
	actions {update_distinct_0_1_regs;}
	size : 1;
}

action do_distinct_0_1_hashes() {
	modify_field(hash_meta_distinct_0_1.sIP, ipv4.srcAddr);
	modify_field(hash_meta_distinct_0_1.dIP, ipv4.dstAddr);
	modify_field(meta_distinct_0_1.qid, 1);
	modify_field_with_hash_based_offset(meta_distinct_0_1.idx, 0, distinct_0_1_fields_hash, 4096);
	register_read(meta_distinct_0_1.val, distinct_0_1, meta_distinct_0_1.idx);
}

table start_distinct_0_1 {
	actions {do_distinct_0_1_hashes;}
	size : 1;
}

control ingress {
	apply(start_distinct_0_1);
	if (meta_distinct_0_1.qid == 1){
		if(meta_distinct_0_1.val > 0) {
			apply(drop_distinct_0_1_1);
		}
		else if(meta_distinct_0_1.val == 0) {
			apply(skip_distinct_0_1_1);
		}
		else {
			apply(drop_distinct_0_1_2);
		}

		apply(update_distinct_0_1_counts);
		apply(copy_to_cpu_1);
	}

}

control egress {
	if (meta_distinct_0_1.qid == 1){
		apply(encap_1);
	}

}
