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
	extract(out_header_2);
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
	hash_meta_distinct_2_1;
	meta_distinct_2_1;
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
	modify_field(out_header_1.qid, meta_distinct_2_1.qid);
	modify_field(out_header_1.dIP, meta_map_init_1.dIP);
	modify_field(out_header_1.sIP, meta_map_init_1.sIP);
}

header_type out_header_2_t {
	fields {
		qid : 8;
		dIP : 32;
		sIP : 32;}
}

header out_header_2_t out_header_2;

field_list copy_to_cpu_fields_2{
	standard_metadata;
	hash_meta_distinct_3_2;
	meta_distinct_3_2;
	meta_map_init_2;
	meta_fm;
}

action do_copy_to_cpu_2() {
	clone_ingress_pkt_to_egress(202, copy_to_cpu_fields_2);
}

table copy_to_cpu_2 {
	actions {do_copy_to_cpu_2;}
	size : 1;
}

table encap_2 {
	actions { do_encap_2; }
	size : 1;
}

action do_encap_2() {
	add_header(out_header_2);
	modify_field(out_header_2.qid, meta_distinct_3_2.qid);
	modify_field(out_header_2.dIP, meta_map_init_2.dIP);
	modify_field(out_header_2.sIP, meta_map_init_2.sIP);
}

table drop_distinct_2_1_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_1_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_1_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_2_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_2_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_2_2 {
	actions {mark_drop;}
	size : 1;
}

header_type meta_map_init_1_t {
	 fields {
		sIP: 32;
		dIP: 32;
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
	modify_field(meta_map_init_1.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_1.dIP, ipv4.dstAddr);
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

header_type meta_distinct_2_1_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_1_t meta_distinct_2_1;

header_type hash_meta_distinct_2_1_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_1_t hash_meta_distinct_2_1;

field_list distinct_2_1_fields {
	hash_meta_distinct_2_1.sIP;
	hash_meta_distinct_2_1.dIP;
}

field_list_calculation distinct_2_1_fields_hash {
	input {
		distinct_2_1_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_1{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_1_regs() {
	bit_or(meta_distinct_2_1.val,meta_distinct_2_1.val, 1);
	register_write(distinct_2_1,meta_distinct_2_1.idx,meta_distinct_2_1.val);
}

table update_distinct_2_1_counts {
	actions {update_distinct_2_1_regs;}
	size : 1;
}

action do_distinct_2_1_hashes() {
	modify_field(hash_meta_distinct_2_1.sIP, meta_map_init_1.sIP);
	modify_field(hash_meta_distinct_2_1.dIP, meta_map_init_1.dIP);
	modify_field(meta_distinct_2_1.qid, 1);
	modify_field_with_hash_based_offset(meta_distinct_2_1.idx, 0, distinct_2_1_fields_hash, 4096);
	register_read(meta_distinct_2_1.val, distinct_2_1, meta_distinct_2_1.idx);
}

table start_distinct_2_1 {
	actions {do_distinct_2_1_hashes;}
	size : 1;
}

action set_distinct_2_1_count() {
	modify_field(meta_distinct_2_1.val, 1);
}

table set_distinct_2_1_count {
	actions {set_distinct_2_1_count;}
        size: 1;
}

header_type meta_map_init_2_t {
	 fields {
		sIP: 32;
		dIP: 32;
		proto: 8;
	}
}

metadata meta_map_init_2_t meta_map_init_2;

table map_init_2{
	actions{
		do_map_init_2;
	}
}

action do_map_init_2(){
	modify_field(meta_map_init_2.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_2.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_2.proto, ipv4.protocol);
}

table map_2_1{
	actions{
		do_map_2_1;
	}
}

action do_map_2_1() {
	bit_and(meta_map_init_2.dIP, meta_map_init_2.dIP, 0xffffffff);
}

header_type meta_distinct_3_2_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_2_t meta_distinct_3_2;

header_type hash_meta_distinct_3_2_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_2_t hash_meta_distinct_3_2;

field_list distinct_3_2_fields {
	hash_meta_distinct_3_2.sIP;
	hash_meta_distinct_3_2.dIP;
}

field_list_calculation distinct_3_2_fields_hash {
	input {
		distinct_3_2_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_2{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_2_regs() {
	bit_or(meta_distinct_3_2.val,meta_distinct_3_2.val, 1);
	register_write(distinct_3_2,meta_distinct_3_2.idx,meta_distinct_3_2.val);
}

table update_distinct_3_2_counts {
	actions {update_distinct_3_2_regs;}
	size : 1;
}

action do_distinct_3_2_hashes() {
	modify_field(hash_meta_distinct_3_2.sIP, meta_map_init_2.sIP);
	modify_field(hash_meta_distinct_3_2.dIP, meta_map_init_2.dIP);
	modify_field(meta_distinct_3_2.qid, 2);
	modify_field_with_hash_based_offset(meta_distinct_3_2.idx, 0, distinct_3_2_fields_hash, 4096);
	register_read(meta_distinct_3_2.val, distinct_3_2, meta_distinct_3_2.idx);
}

table start_distinct_3_2 {
	actions {do_distinct_3_2_hashes;}
	size : 1;
}

action set_distinct_3_2_count() {
	modify_field(meta_distinct_3_2.val, 1);
}

table set_distinct_3_2_count {
	actions {set_distinct_3_2_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_1 : 1;
		qid_2 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_1, 1);
	modify_field(meta_fm.qid_2, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_1(){
	modify_field(meta_fm.qid_1, 1);
}

action set_meta_fm_2(){
	modify_field(meta_fm.qid_2, 1);
}

action reset_meta_fm_1(){
	modify_field(meta_fm.qid_1, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_2(){
	modify_field(meta_fm.qid_2, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_1_1{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_1;
		reset_meta_fm_1;
	}
}

table filter_2_0{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_2;
		reset_meta_fm_2;
	}
}

table filter_2_2{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_2;
		reset_meta_fm_2;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		apply(filter_1_1);
		if (meta_fm.qid_1 == 1){
			apply(map_init_1);
			apply(map_1_0);
			apply(start_distinct_2_1);
			if(meta_distinct_2_1.val > 0) {
				apply(drop_distinct_2_1_1);
			}
			else if(meta_distinct_2_1.val == 0) {
				apply(skip_distinct_2_1_1);
			}
			else {
				apply(drop_distinct_2_1_2);
			}

			apply(update_distinct_2_1_counts);
			apply(copy_to_cpu_1);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_2== 1){
			apply(filter_2_0);
		}
		if (meta_fm.qid_2== 1){
			apply(filter_2_2);
		}
		if (meta_fm.qid_2 == 1){
			apply(map_init_2);
			apply(map_2_1);
			apply(start_distinct_3_2);
			if(meta_distinct_3_2.val > 0) {
				apply(drop_distinct_3_2_1);
			}
			else if(meta_distinct_3_2.val == 0) {
				apply(skip_distinct_3_2_1);
			}
			else {
				apply(drop_distinct_3_2_2);
			}

			apply(update_distinct_3_2_counts);
			apply(copy_to_cpu_2);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 2) {
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
			if (meta_fm.f1 == 1){
				apply(encap_2);
			}
		}


	}
}

