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

header_type intrinsic_metadata_t {
	fields {
	recirculate_flag : 16;}
}

metadata intrinsic_metadata_t intrinsic_metadata;

field_list recirculate_fields {
	standard_metadata;
	meta_fm;
}

action do_recirculate_to_ingress() {
	add_to_field(meta_fm.f1, 1);
	recirculate(recirculate_fields);
}

table recirculate_to_ingress {
	actions { do_recirculate_to_ingress; }
	size : 1;
}

table drop_table {
	actions {_drop;}
	size : 1;
}

table drop_packets {
	actions {_drop;}
	size : 1;
}

action mark_drop() {
	modify_field(meta_fm.is_drop, 1);
}

parser parse_out_header {
	extract(out_header_1);
	return parse_ethernet;
}

header_type out_header_1_t {
	fields {
		qid : 8;
		dIP : 32;
		sIP : 32;}
}

header out_header_1_t out_header_1;

field_list copy_to_cpu_fields_1{
	standard_metadata;
	hash_meta_distinct_1_1;
	meta_distinct_1_1;
	meta_map_init_1;
	meta_fm;
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
	modify_field(out_header_1.qid, meta_distinct_1_1.qid);
	modify_field(out_header_1.dIP, meta_map_init_1.dIP);
	modify_field(out_header_1.sIP, meta_map_init_1.sIP);
}

table drop_distinct_1_1_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_1_1_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_1_1_2 {
	actions {mark_drop;}
	size : 1;
}

header_type meta_map_init_1_t {
	 fields {
		dIP: 32;
		sIP: 32;
		proto: 8;
	}
}

metadata meta_map_init_1_t meta_map_init_1;

table map_init_1{
	actions{
		do_map_init_1;
	}
}

action do_map_init_1(){
	modify_field(meta_map_init_1.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_1.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_1.proto, ipv4.protocol);
}

table map_1_0{
	actions{
		do_map_1_0;
	}
}

action do_map_1_0() {
	bit_and(meta_map_init_1.dIP, meta_map_init_1.dIP, 0xffff0000);
}

header_type meta_distinct_1_1_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_1_1_t meta_distinct_1_1;

header_type hash_meta_distinct_1_1_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_1_1_t hash_meta_distinct_1_1;

field_list distinct_1_1_fields {
	hash_meta_distinct_1_1.sIP;
	hash_meta_distinct_1_1.dIP;
}

field_list_calculation distinct_1_1_fields_hash {
	input {
		distinct_1_1_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_1_1{
	width : 32;
	instance_count : 10;
}

action update_distinct_1_1_regs() {
	bit_or(meta_distinct_1_1.val,meta_distinct_1_1.val, 1);
	register_write(distinct_1_1,meta_distinct_1_1.idx,meta_distinct_1_1.val);
}

table update_distinct_1_1_counts {
	actions {update_distinct_1_1_regs;}
	size : 1;
}

action do_distinct_1_1_hashes() {
	modify_field(hash_meta_distinct_1_1.sIP, meta_map_init_1.sIP);
	modify_field(hash_meta_distinct_1_1.dIP, meta_map_init_1.dIP);
	modify_field(meta_distinct_1_1.qid, 1);
	modify_field_with_hash_based_offset(meta_distinct_1_1.idx, 0, distinct_1_1_fields_hash, 4096);
	register_read(meta_distinct_1_1.val, distinct_1_1, meta_distinct_1_1.idx);
}

table start_distinct_1_1 {
	actions {do_distinct_1_1_hashes;}
	size : 1;
}

action set_distinct_1_1_count() {
	modify_field(meta_distinct_1_1.val, 1);
}

table set_distinct_1_1_count {
	actions {set_distinct_1_1_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_1 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_1, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_1(){
	modify_field(meta_fm.qid_1, 1);
}

action reset_meta_fm_1(){
	modify_field(meta_fm.qid_1, 0);
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_1 == 1){
			apply(map_init_1);
			apply(map_1_0);
			apply(start_distinct_1_1);
			if(meta_distinct_1_1.val > 0) {
				apply(drop_distinct_1_1_1);
			}
			else if(meta_distinct_1_1.val == 0) {
				apply(skip_distinct_1_1_1);
			}
			else {
				apply(drop_distinct_1_1_2);
			}

			apply(update_distinct_1_1_counts);
			apply(copy_to_cpu_1);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 1) {
			apply(recirculate_to_ingress);
		}
		else {
			apply(drop_table);
		}
	}

	else if (standard_metadata.instance_type == 1) {
		if (meta_fm.is_drop == 1){
			apply(drop_packets);
		}
		else {
			if (meta_fm.f1 == 0){
				apply(encap_1);
			}
		}


	}
}
