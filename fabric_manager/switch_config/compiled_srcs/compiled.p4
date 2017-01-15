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
	extract(out_header_30032);
	extract(out_header_10032);
	extract(out_header_30012);
	extract(out_header_10012);
	extract(out_header_10028);
	return parse_ethernet;
}

header_type out_header_30032_t {
	fields {
		qid : 16;
		dIP : 32;
		proto : 16;}
}

header out_header_30032_t out_header_30032;

field_list copy_to_cpu_fields_30032{
	standard_metadata;
	meta_map_init_30032;
	meta_fm;
}

action do_copy_to_cpu_30032() {
	clone_ingress_pkt_to_egress(30232, copy_to_cpu_fields_30032);
}

table copy_to_cpu_30032 {
	actions {do_copy_to_cpu_30032;}
	size : 1;
}

table encap_30032 {
	actions { do_encap_30032; }
	size : 1;
}

action do_encap_30032() {
	add_header(out_header_30032);
	modify_field(out_header_30032.qid, meta_map_init_30032.qid);
	modify_field(out_header_30032.dIP, meta_map_init_30032.dIP);
	modify_field(out_header_30032.proto, meta_map_init_30032.proto);
}

header_type out_header_10032_t {
	fields {
		qid : 16;
		dIP : 32;
		sIP : 32;}
}

header out_header_10032_t out_header_10032;

field_list copy_to_cpu_fields_10032{
	standard_metadata;
	hash_meta_distinct_4_10032;
	meta_distinct_4_10032;
	meta_map_init_10032;
	meta_fm;
}

action do_copy_to_cpu_10032() {
	clone_ingress_pkt_to_egress(10232, copy_to_cpu_fields_10032);
}

table copy_to_cpu_10032 {
	actions {do_copy_to_cpu_10032;}
	size : 1;
}

table encap_10032 {
	actions { do_encap_10032; }
	size : 1;
}

action do_encap_10032() {
	add_header(out_header_10032);
	modify_field(out_header_10032.qid, meta_distinct_4_10032.qid);
	modify_field(out_header_10032.dIP, meta_map_init_10032.dIP);
	modify_field(out_header_10032.sIP, meta_map_init_10032.sIP);
}

header_type out_header_30012_t {
	fields {
		qid : 16;
		dIP : 32;
		proto : 16;}
}

header out_header_30012_t out_header_30012;

field_list copy_to_cpu_fields_30012{
	standard_metadata;
	meta_map_init_30012;
	meta_fm;
}

action do_copy_to_cpu_30012() {
	clone_ingress_pkt_to_egress(30212, copy_to_cpu_fields_30012);
}

table copy_to_cpu_30012 {
	actions {do_copy_to_cpu_30012;}
	size : 1;
}

table encap_30012 {
	actions { do_encap_30012; }
	size : 1;
}

action do_encap_30012() {
	add_header(out_header_30012);
	modify_field(out_header_30012.qid, meta_map_init_30012.qid);
	modify_field(out_header_30012.dIP, meta_map_init_30012.dIP);
	modify_field(out_header_30012.proto, meta_map_init_30012.proto);
}

header_type out_header_10012_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_10012_t out_header_10012;

field_list copy_to_cpu_fields_10012{
	standard_metadata;
	hash_meta_reduce_4_10012;
	meta_reduce_4_10012;
	meta_map_init_10012;
	meta_fm;
}

action do_copy_to_cpu_10012() {
	clone_ingress_pkt_to_egress(10212, copy_to_cpu_fields_10012);
}

table copy_to_cpu_10012 {
	actions {do_copy_to_cpu_10012;}
	size : 1;
}

table encap_10012 {
	actions { do_encap_10012; }
	size : 1;
}

action do_encap_10012() {
	add_header(out_header_10012);
	modify_field(out_header_10012.qid, meta_reduce_4_10012.qid);
	modify_field(out_header_10012.dIP, meta_map_init_10012.dIP);
	modify_field(out_header_10012.count, meta_reduce_4_10012.val);
}

header_type out_header_10028_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_10028_t out_header_10028;

field_list copy_to_cpu_fields_10028{
	standard_metadata;
	hash_meta_reduce_5_10028;
	meta_reduce_5_10028;
	meta_map_init_10028;
	meta_fm;
}

action do_copy_to_cpu_10028() {
	clone_ingress_pkt_to_egress(10228, copy_to_cpu_fields_10028);
}

table copy_to_cpu_10028 {
	actions {do_copy_to_cpu_10028;}
	size : 1;
}

table encap_10028 {
	actions { do_encap_10028; }
	size : 1;
}

action do_encap_10028() {
	add_header(out_header_10028);
	modify_field(out_header_10028.qid, meta_reduce_5_10028.qid);
	modify_field(out_header_10028.dIP, meta_map_init_10028.dIP);
	modify_field(out_header_10028.count, meta_reduce_5_10028.val);
}

table drop_distinct_4_10032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_4_10032_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_4_10032_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_10012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_10012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_10012_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_10012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_10012_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_4_10028_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_4_10028_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_4_10028_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_10028_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_10028_1 {
	actions {mark_drop;}
	size : 1;
}

table map_init_30032{
	actions{
		do_map_init_30032;
	}
}

action do_map_init_30032(){
	modify_field(meta_map_init_30032.qid, 30032);
	modify_field(meta_map_init_30032.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_30032.proto, ipv4.protocol);
}

header_type meta_map_init_30032_t {
	 fields {
		qid: 16;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_30032_t meta_map_init_30032;

table map_30032_2{
	actions{
		do_map_30032_2;
	}
}

action do_map_30032_2() {
	bit_and(meta_map_init_30032.dIP, meta_map_init_30032.dIP, 0xffffffff);
}

table map_init_10032{
	actions{
		do_map_init_10032;
	}
}

action do_map_init_10032(){
	modify_field(meta_map_init_10032.qid, 10032);
	modify_field(meta_map_init_10032.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10032.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_10032.proto, ipv4.protocol);
}

header_type meta_map_init_10032_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_10032_t meta_map_init_10032;

table map_10032_2{
	actions{
		do_map_10032_2;
	}
}

action do_map_10032_2() {
	bit_and(meta_map_init_10032.dIP, meta_map_init_10032.dIP, 0xffffffff);
}

header_type meta_distinct_4_10032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_4_10032_t meta_distinct_4_10032;

header_type hash_meta_distinct_4_10032_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_4_10032_t hash_meta_distinct_4_10032;

field_list distinct_4_10032_fields {
	hash_meta_distinct_4_10032.sIP;
	hash_meta_distinct_4_10032.dIP;
}

field_list_calculation distinct_4_10032_fields_hash {
	input {
		distinct_4_10032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_4_10032{
	width : 32;
	instance_count : 4096;
}

action update_distinct_4_10032_regs() {
	bit_or(meta_distinct_4_10032.val,meta_distinct_4_10032.val, 1);
	register_write(distinct_4_10032,meta_distinct_4_10032.idx,meta_distinct_4_10032.val);
}

table update_distinct_4_10032_counts {
	actions {update_distinct_4_10032_regs;}
	size : 1;
}

action do_distinct_4_10032_hashes() {
	modify_field(hash_meta_distinct_4_10032.sIP, meta_map_init_10032.sIP);
	modify_field(hash_meta_distinct_4_10032.dIP, meta_map_init_10032.dIP);
	modify_field(meta_distinct_4_10032.qid, 10032);
	modify_field_with_hash_based_offset(meta_distinct_4_10032.idx, 0, distinct_4_10032_fields_hash, 4096);
	register_read(meta_distinct_4_10032.val, distinct_4_10032, meta_distinct_4_10032.idx);
}

table start_distinct_4_10032 {
	actions {do_distinct_4_10032_hashes;}
	size : 1;
}

action set_distinct_4_10032_count() {
	modify_field(meta_distinct_4_10032.val, 1);
}

table set_distinct_4_10032_count {
	actions {set_distinct_4_10032_count;}
        size: 1;
}

table map_init_30012{
	actions{
		do_map_init_30012;
	}
}

action do_map_init_30012(){
	modify_field(meta_map_init_30012.qid, 30012);
	modify_field(meta_map_init_30012.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_30012.proto, ipv4.protocol);
}

header_type meta_map_init_30012_t {
	 fields {
		qid: 16;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_30012_t meta_map_init_30012;

table map_30012_2{
	actions{
		do_map_30012_2;
	}
}

action do_map_30012_2() {
	bit_and(meta_map_init_30012.dIP, meta_map_init_30012.dIP, 0xfff00000);
}

table map_init_10012{
	actions{
		do_map_init_10012;
	}
}

action do_map_init_10012(){
	modify_field(meta_map_init_10012.qid, 10012);
	modify_field(meta_map_init_10012.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10012.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_10012.proto, ipv4.protocol);
}

header_type meta_map_init_10012_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_10012_t meta_map_init_10012;

table map_10012_1{
	actions{
		do_map_10012_1;
	}
}

action do_map_10012_1() {
	bit_and(meta_map_init_10012.dIP, meta_map_init_10012.dIP, 0xfff00000);
}

header_type meta_distinct_3_10012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_10012_t meta_distinct_3_10012;

header_type hash_meta_distinct_3_10012_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_10012_t hash_meta_distinct_3_10012;

field_list distinct_3_10012_fields {
	hash_meta_distinct_3_10012.sIP;
	hash_meta_distinct_3_10012.dIP;
}

field_list_calculation distinct_3_10012_fields_hash {
	input {
		distinct_3_10012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_10012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_10012_regs() {
	bit_or(meta_distinct_3_10012.val,meta_distinct_3_10012.val, 1);
	register_write(distinct_3_10012,meta_distinct_3_10012.idx,meta_distinct_3_10012.val);
}

table update_distinct_3_10012_counts {
	actions {update_distinct_3_10012_regs;}
	size : 1;
}

action do_distinct_3_10012_hashes() {
	modify_field(hash_meta_distinct_3_10012.sIP, meta_map_init_10012.sIP);
	modify_field(hash_meta_distinct_3_10012.dIP, meta_map_init_10012.dIP);
	modify_field(meta_distinct_3_10012.qid, 10012);
	modify_field_with_hash_based_offset(meta_distinct_3_10012.idx, 0, distinct_3_10012_fields_hash, 4096);
	register_read(meta_distinct_3_10012.val, distinct_3_10012, meta_distinct_3_10012.idx);
}

table start_distinct_3_10012 {
	actions {do_distinct_3_10012_hashes;}
	size : 1;
}

action set_distinct_3_10012_count() {
	modify_field(meta_distinct_3_10012.val, 1);
}

table set_distinct_3_10012_count {
	actions {set_distinct_3_10012_count;}
        size: 1;
}

header_type meta_reduce_4_10012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_10012_t meta_reduce_4_10012;

header_type hash_meta_reduce_4_10012_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_10012_t hash_meta_reduce_4_10012;

field_list reduce_4_10012_fields {
	hash_meta_reduce_4_10012.dIP;
}

field_list_calculation reduce_4_10012_fields_hash {
	input {
		reduce_4_10012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_10012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_10012_regs() {
	add_to_field(meta_reduce_4_10012.val, 1);
	register_write(reduce_4_10012,meta_reduce_4_10012.idx,meta_reduce_4_10012.val);
}

table update_reduce_4_10012_counts {
	actions {update_reduce_4_10012_regs;}
	size : 1;
}

action do_reduce_4_10012_hashes() {
	modify_field(hash_meta_reduce_4_10012.dIP, meta_map_init_10012.dIP);
	modify_field(meta_reduce_4_10012.qid, 10012);
	modify_field_with_hash_based_offset(meta_reduce_4_10012.idx, 0, reduce_4_10012_fields_hash, 4096);
	register_read(meta_reduce_4_10012.val, reduce_4_10012, meta_reduce_4_10012.idx);
}

table start_reduce_4_10012 {
	actions {do_reduce_4_10012_hashes;}
	size : 1;
}

action set_reduce_4_10012_count() {
	modify_field(meta_reduce_4_10012.val, 1);
}

table set_reduce_4_10012_count {
	actions {set_reduce_4_10012_count;}
        size: 1;
}

table map_init_10028{
	actions{
		do_map_init_10028;
	}
}

action do_map_init_10028(){
	modify_field(meta_map_init_10028.qid, 10028);
	modify_field(meta_map_init_10028.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10028.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_10028.proto, ipv4.protocol);
}

header_type meta_map_init_10028_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_10028_t meta_map_init_10028;

table map_10028_2{
	actions{
		do_map_10028_2;
	}
}

action do_map_10028_2() {
	bit_and(meta_map_init_10028.dIP, meta_map_init_10028.dIP, 0xfffffff0);
}

header_type meta_distinct_4_10028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_4_10028_t meta_distinct_4_10028;

header_type hash_meta_distinct_4_10028_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_4_10028_t hash_meta_distinct_4_10028;

field_list distinct_4_10028_fields {
	hash_meta_distinct_4_10028.sIP;
	hash_meta_distinct_4_10028.dIP;
}

field_list_calculation distinct_4_10028_fields_hash {
	input {
		distinct_4_10028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_4_10028{
	width : 32;
	instance_count : 4096;
}

action update_distinct_4_10028_regs() {
	bit_or(meta_distinct_4_10028.val,meta_distinct_4_10028.val, 1);
	register_write(distinct_4_10028,meta_distinct_4_10028.idx,meta_distinct_4_10028.val);
}

table update_distinct_4_10028_counts {
	actions {update_distinct_4_10028_regs;}
	size : 1;
}

action do_distinct_4_10028_hashes() {
	modify_field(hash_meta_distinct_4_10028.sIP, meta_map_init_10028.sIP);
	modify_field(hash_meta_distinct_4_10028.dIP, meta_map_init_10028.dIP);
	modify_field(meta_distinct_4_10028.qid, 10028);
	modify_field_with_hash_based_offset(meta_distinct_4_10028.idx, 0, distinct_4_10028_fields_hash, 4096);
	register_read(meta_distinct_4_10028.val, distinct_4_10028, meta_distinct_4_10028.idx);
}

table start_distinct_4_10028 {
	actions {do_distinct_4_10028_hashes;}
	size : 1;
}

action set_distinct_4_10028_count() {
	modify_field(meta_distinct_4_10028.val, 1);
}

table set_distinct_4_10028_count {
	actions {set_distinct_4_10028_count;}
        size: 1;
}

header_type meta_reduce_5_10028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_10028_t meta_reduce_5_10028;

header_type hash_meta_reduce_5_10028_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_5_10028_t hash_meta_reduce_5_10028;

field_list reduce_5_10028_fields {
	hash_meta_reduce_5_10028.dIP;
}

field_list_calculation reduce_5_10028_fields_hash {
	input {
		reduce_5_10028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_10028{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_10028_regs() {
	add_to_field(meta_reduce_5_10028.val, 1);
	register_write(reduce_5_10028,meta_reduce_5_10028.idx,meta_reduce_5_10028.val);
}

table update_reduce_5_10028_counts {
	actions {update_reduce_5_10028_regs;}
	size : 1;
}

action do_reduce_5_10028_hashes() {
	modify_field(hash_meta_reduce_5_10028.dIP, meta_map_init_10028.dIP);
	modify_field(meta_reduce_5_10028.qid, 10028);
	modify_field_with_hash_based_offset(meta_reduce_5_10028.idx, 0, reduce_5_10028_fields_hash, 4096);
	register_read(meta_reduce_5_10028.val, reduce_5_10028, meta_reduce_5_10028.idx);
}

table start_reduce_5_10028 {
	actions {do_reduce_5_10028_hashes;}
	size : 1;
}

action set_reduce_5_10028_count() {
	modify_field(meta_reduce_5_10028.val, 1);
}

table set_reduce_5_10028_count {
	actions {set_reduce_5_10028_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_30032 : 1;
		qid_10032 : 1;
		qid_30012 : 1;
		qid_10012 : 1;
		qid_10028 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_30032, 1);
	modify_field(meta_fm.qid_10032, 1);
	modify_field(meta_fm.qid_30012, 1);
	modify_field(meta_fm.qid_10012, 1);
	modify_field(meta_fm.qid_10028, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_30032(){
	modify_field(meta_fm.qid_30032, 1);
}

action set_meta_fm_10032(){
	modify_field(meta_fm.qid_10032, 1);
}

action set_meta_fm_30012(){
	modify_field(meta_fm.qid_30012, 1);
}

action set_meta_fm_10012(){
	modify_field(meta_fm.qid_10012, 1);
}

action set_meta_fm_10028(){
	modify_field(meta_fm.qid_10028, 1);
}

action reset_meta_fm_30032(){
	modify_field(meta_fm.qid_30032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10032(){
	modify_field(meta_fm.qid_10032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_30012(){
	modify_field(meta_fm.qid_30012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10012(){
	modify_field(meta_fm.qid_10012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10028(){
	modify_field(meta_fm.qid_10028, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_30032_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_30032;
		reset_meta_fm_30032;
	}
}

table filter_30032_3{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_30032;
		reset_meta_fm_30032;
	}
}

table filter_10032_3{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_10032;
		reset_meta_fm_10032;
	}
}

table filter_10032_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_10032;
		reset_meta_fm_10032;
	}
}

table filter_30012_3{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_30012;
		reset_meta_fm_30012;
	}
}

table filter_30012_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_30012;
		reset_meta_fm_30012;
	}
}

table filter_10012_2{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_10012;
		reset_meta_fm_10012;
	}
}

table filter_10028_3{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_10028;
		reset_meta_fm_10028;
	}
}

table filter_10028_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_10028;
		reset_meta_fm_10028;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_30032== 1){
			apply(filter_30032_1);
		}
		apply(filter_30032_3);
		if (meta_fm.qid_30032 == 1){
					apply(map_init_30032);
			apply(map_30032_2);
			apply(copy_to_cpu_30032);
		}
	}
	if (meta_fm.f1 == 1){
		apply(filter_10032_3);
		if (meta_fm.qid_10032== 1){
			apply(filter_10032_1);
		}
		if (meta_fm.qid_10032 == 1){
					apply(map_init_10032);
			apply(map_10032_2);
			apply(start_distinct_4_10032);
			if(meta_distinct_4_10032.val > 0) {
				apply(drop_distinct_4_10032_1);
			}
			else if(meta_distinct_4_10032.val == 0) {
				apply(skip_distinct_4_10032_1);
			}
			else {
				apply(drop_distinct_4_10032_2);
			}

			apply(update_distinct_4_10032_counts);
			apply(copy_to_cpu_10032);
		}
	}
	if (meta_fm.f1 == 2){
		apply(filter_30012_3);
		if (meta_fm.qid_30012== 1){
			apply(filter_30012_1);
		}
		if (meta_fm.qid_30012 == 1){
					apply(map_init_30012);
			apply(map_30012_2);
			apply(copy_to_cpu_30012);
		}
	}
	if (meta_fm.f1 == 3){
		apply(filter_10012_2);
		if (meta_fm.qid_10012 == 1){
					apply(map_init_10012);
			apply(map_10012_1);
			apply(start_distinct_3_10012);
			apply(start_reduce_4_10012);
			if(meta_distinct_3_10012.val > 0) {
				apply(drop_distinct_3_10012_1);
			}
			else if(meta_distinct_3_10012.val == 0) {
				apply(skip_distinct_3_10012_1);
			}
			else {
				apply(drop_distinct_3_10012_2);
			}

			apply(update_distinct_3_10012_counts);
			apply(update_reduce_4_10012_counts);
			if(meta_reduce_4_10012.val > 1) {
				apply(set_reduce_4_10012_count);			}
			else if(meta_reduce_4_10012.val == 1) {
				apply(skip_reduce_4_10012_1);
			}
			else {
				apply(drop_reduce_4_10012_1);
			}

			apply(copy_to_cpu_10012);
		}
	}
	if (meta_fm.f1 == 4){
		apply(filter_10028_3);
		if (meta_fm.qid_10028== 1){
			apply(filter_10028_1);
		}
		if (meta_fm.qid_10028 == 1){
					apply(map_init_10028);
			apply(map_10028_2);
			apply(start_distinct_4_10028);
			apply(start_reduce_5_10028);
			if(meta_distinct_4_10028.val > 0) {
				apply(drop_distinct_4_10028_1);
			}
			else if(meta_distinct_4_10028.val == 0) {
				apply(skip_distinct_4_10028_1);
			}
			else {
				apply(drop_distinct_4_10028_2);
			}

			apply(update_distinct_4_10028_counts);
			apply(update_reduce_5_10028_counts);
			if(meta_reduce_5_10028.val > 1) {
				apply(set_reduce_5_10028_count);			}
			else if(meta_reduce_5_10028.val == 1) {
				apply(skip_reduce_5_10028_1);
			}
			else {
				apply(drop_reduce_5_10028_1);
			}

			apply(copy_to_cpu_10028);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 5) {
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
				apply(encap_30032);
			}
			if (meta_fm.f1 == 1){
				apply(encap_10032);
			}
			if (meta_fm.f1 == 2){
				apply(encap_30012);
			}
			if (meta_fm.f1 == 3){
				apply(encap_10012);
			}
			if (meta_fm.f1 == 4){
				apply(encap_10028);
			}
		}


	}
}

