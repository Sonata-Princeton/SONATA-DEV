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
	extract(out_header_20001);
	extract(out_header_40002);
	extract(out_header_40003);
	extract(out_header_20004);
	extract(out_header_40005);
	extract(out_header_40006);
	extract(out_header_40001);
	extract(out_header_20002);
	extract(out_header_10001);
	extract(out_header_10002);
	extract(out_header_20003);
	extract(out_header_10003);
	extract(out_header_40004);
	return parse_ethernet;
}

header_type out_header_20001_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_20001_t out_header_20001;

field_list copy_to_cpu_fields_20001{
	standard_metadata;
	hash_meta_distinct_4_20001;
	meta_distinct_4_20001;
	meta_map_init_20001;
	meta_fm;
}

action do_copy_to_cpu_20001() {
	clone_ingress_pkt_to_egress(20201, copy_to_cpu_fields_20001);
}

table copy_to_cpu_20001 {
	actions {do_copy_to_cpu_20001;}
	size : 1;
}

table encap_20001 {
	actions { do_encap_20001; }
	size : 1;
}

action do_encap_20001() {
	add_header(out_header_20001);
	modify_field(out_header_20001.qid, meta_distinct_4_20001.qid);
	modify_field(out_header_20001.dIP, meta_map_init_20001.dIP);
}

header_type out_header_40002_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_40002_t out_header_40002;

field_list copy_to_cpu_fields_40002{
	standard_metadata;
	hash_meta_distinct_2_40002;
	meta_distinct_2_40002;
	meta_map_init_40002;
	meta_fm;
}

action do_copy_to_cpu_40002() {
	clone_ingress_pkt_to_egress(40202, copy_to_cpu_fields_40002);
}

table copy_to_cpu_40002 {
	actions {do_copy_to_cpu_40002;}
	size : 1;
}

table encap_40002 {
	actions { do_encap_40002; }
	size : 1;
}

action do_encap_40002() {
	add_header(out_header_40002);
	modify_field(out_header_40002.qid, meta_distinct_2_40002.qid);
	modify_field(out_header_40002.dIP, meta_map_init_40002.dIP);
}

header_type out_header_40003_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_40003_t out_header_40003;

field_list copy_to_cpu_fields_40003{
	standard_metadata;
	meta_map_init_40003;
	meta_fm;
}

action do_copy_to_cpu_40003() {
	clone_ingress_pkt_to_egress(40203, copy_to_cpu_fields_40003);
}

table copy_to_cpu_40003 {
	actions {do_copy_to_cpu_40003;}
	size : 1;
}

table encap_40003 {
	actions { do_encap_40003; }
	size : 1;
}

action do_encap_40003() {
	add_header(out_header_40003);
	modify_field(out_header_40003.qid, meta_map_init_40003.qid);
	modify_field(out_header_40003.dIP, meta_map_init_40003.dIP);
}

header_type out_header_20004_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_20004_t out_header_20004;

field_list copy_to_cpu_fields_20004{
	standard_metadata;
	hash_meta_distinct_3_20004;
	meta_distinct_3_20004;
	meta_map_init_20004;
	meta_fm;
}

action do_copy_to_cpu_20004() {
	clone_ingress_pkt_to_egress(20204, copy_to_cpu_fields_20004);
}

table copy_to_cpu_20004 {
	actions {do_copy_to_cpu_20004;}
	size : 1;
}

table encap_20004 {
	actions { do_encap_20004; }
	size : 1;
}

action do_encap_20004() {
	add_header(out_header_20004);
	modify_field(out_header_20004.qid, meta_distinct_3_20004.qid);
	modify_field(out_header_20004.dIP, meta_map_init_20004.dIP);
}

header_type out_header_40005_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_40005_t out_header_40005;

field_list copy_to_cpu_fields_40005{
	standard_metadata;
	meta_map_init_40005;
	meta_fm;
}

action do_copy_to_cpu_40005() {
	clone_ingress_pkt_to_egress(40205, copy_to_cpu_fields_40005);
}

table copy_to_cpu_40005 {
	actions {do_copy_to_cpu_40005;}
	size : 1;
}

table encap_40005 {
	actions { do_encap_40005; }
	size : 1;
}

action do_encap_40005() {
	add_header(out_header_40005);
	modify_field(out_header_40005.qid, meta_map_init_40005.qid);
	modify_field(out_header_40005.dIP, meta_map_init_40005.dIP);
}

header_type out_header_40006_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_40006_t out_header_40006;

field_list copy_to_cpu_fields_40006{
	standard_metadata;
	hash_meta_distinct_3_40006;
	meta_distinct_3_40006;
	meta_map_init_40006;
	meta_fm;
}

action do_copy_to_cpu_40006() {
	clone_ingress_pkt_to_egress(40206, copy_to_cpu_fields_40006);
}

table copy_to_cpu_40006 {
	actions {do_copy_to_cpu_40006;}
	size : 1;
}

table encap_40006 {
	actions { do_encap_40006; }
	size : 1;
}

action do_encap_40006() {
	add_header(out_header_40006);
	modify_field(out_header_40006.qid, meta_distinct_3_40006.qid);
	modify_field(out_header_40006.dIP, meta_map_init_40006.dIP);
}

header_type out_header_40001_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_40001_t out_header_40001;

field_list copy_to_cpu_fields_40001{
	standard_metadata;
	hash_meta_distinct_3_40001;
	meta_distinct_3_40001;
	meta_map_init_40001;
	meta_fm;
}

action do_copy_to_cpu_40001() {
	clone_ingress_pkt_to_egress(40201, copy_to_cpu_fields_40001);
}

table copy_to_cpu_40001 {
	actions {do_copy_to_cpu_40001;}
	size : 1;
}

table encap_40001 {
	actions { do_encap_40001; }
	size : 1;
}

action do_encap_40001() {
	add_header(out_header_40001);
	modify_field(out_header_40001.qid, meta_distinct_3_40001.qid);
	modify_field(out_header_40001.dIP, meta_map_init_40001.dIP);
}

header_type out_header_20002_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_20002_t out_header_20002;

field_list copy_to_cpu_fields_20002{
	standard_metadata;
	hash_meta_distinct_4_20002;
	meta_distinct_4_20002;
	meta_map_init_20002;
	meta_fm;
}

action do_copy_to_cpu_20002() {
	clone_ingress_pkt_to_egress(20202, copy_to_cpu_fields_20002);
}

table copy_to_cpu_20002 {
	actions {do_copy_to_cpu_20002;}
	size : 1;
}

table encap_20002 {
	actions { do_encap_20002; }
	size : 1;
}

action do_encap_20002() {
	add_header(out_header_20002);
	modify_field(out_header_20002.qid, meta_distinct_4_20002.qid);
	modify_field(out_header_20002.dIP, meta_map_init_20002.dIP);
}

header_type out_header_10001_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_10001_t out_header_10001;

field_list copy_to_cpu_fields_10001{
	standard_metadata;
	meta_map_init_10001;
	meta_fm;
}

action do_copy_to_cpu_10001() {
	clone_ingress_pkt_to_egress(10201, copy_to_cpu_fields_10001);
}

table copy_to_cpu_10001 {
	actions {do_copy_to_cpu_10001;}
	size : 1;
}

table encap_10001 {
	actions { do_encap_10001; }
	size : 1;
}

action do_encap_10001() {
	add_header(out_header_10001);
	modify_field(out_header_10001.qid, meta_map_init_10001.qid);
	modify_field(out_header_10001.dIP, meta_map_init_10001.dIP);
}

header_type out_header_10002_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_10002_t out_header_10002;

field_list copy_to_cpu_fields_10002{
	standard_metadata;
	meta_map_init_10002;
	meta_fm;
}

action do_copy_to_cpu_10002() {
	clone_ingress_pkt_to_egress(10202, copy_to_cpu_fields_10002);
}

table copy_to_cpu_10002 {
	actions {do_copy_to_cpu_10002;}
	size : 1;
}

table encap_10002 {
	actions { do_encap_10002; }
	size : 1;
}

action do_encap_10002() {
	add_header(out_header_10002);
	modify_field(out_header_10002.qid, meta_map_init_10002.qid);
	modify_field(out_header_10002.dIP, meta_map_init_10002.dIP);
}

header_type out_header_20003_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_20003_t out_header_20003;

field_list copy_to_cpu_fields_20003{
	standard_metadata;
	hash_meta_distinct_3_20003;
	meta_distinct_3_20003;
	meta_map_init_20003;
	meta_fm;
}

action do_copy_to_cpu_20003() {
	clone_ingress_pkt_to_egress(20203, copy_to_cpu_fields_20003);
}

table copy_to_cpu_20003 {
	actions {do_copy_to_cpu_20003;}
	size : 1;
}

table encap_20003 {
	actions { do_encap_20003; }
	size : 1;
}

action do_encap_20003() {
	add_header(out_header_20003);
	modify_field(out_header_20003.qid, meta_distinct_3_20003.qid);
	modify_field(out_header_20003.dIP, meta_map_init_20003.dIP);
}

header_type out_header_10003_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_10003_t out_header_10003;

field_list copy_to_cpu_fields_10003{
	standard_metadata;
	hash_meta_distinct_3_10003;
	meta_distinct_3_10003;
	meta_map_init_10003;
	meta_fm;
}

action do_copy_to_cpu_10003() {
	clone_ingress_pkt_to_egress(10203, copy_to_cpu_fields_10003);
}

table copy_to_cpu_10003 {
	actions {do_copy_to_cpu_10003;}
	size : 1;
}

table encap_10003 {
	actions { do_encap_10003; }
	size : 1;
}

action do_encap_10003() {
	add_header(out_header_10003);
	modify_field(out_header_10003.qid, meta_distinct_3_10003.qid);
	modify_field(out_header_10003.dIP, meta_map_init_10003.dIP);
}

header_type out_header_40004_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_40004_t out_header_40004;

field_list copy_to_cpu_fields_40004{
	standard_metadata;
	meta_map_init_40004;
	meta_fm;
}

action do_copy_to_cpu_40004() {
	clone_ingress_pkt_to_egress(40204, copy_to_cpu_fields_40004);
}

table copy_to_cpu_40004 {
	actions {do_copy_to_cpu_40004;}
	size : 1;
}

table encap_40004 {
	actions { do_encap_40004; }
	size : 1;
}

action do_encap_40004() {
	add_header(out_header_40004);
	modify_field(out_header_40004.qid, meta_map_init_40004.qid);
	modify_field(out_header_40004.dIP, meta_map_init_40004.dIP);
}

table drop_distinct_4_20001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_4_20001_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_4_20001_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_2_40002_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_40002_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_40002_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_20004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_20004_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_20004_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_40006_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_40006_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_40006_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_40001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_40001_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_40001_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_4_20002_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_4_20002_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_4_20002_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_20003_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_20003_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_20003_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_10003_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_10003_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_10003_2 {
	actions {mark_drop;}
	size : 1;
}

table map_init_20001{
	actions{
		do_map_init_20001;
	}
}

action do_map_init_20001(){
	modify_field(meta_map_init_20001.qid, 20001);
	modify_field(meta_map_init_20001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_20001_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_20001_t meta_map_init_20001;

table map_20001_3{
	actions{
		do_map_20001_3;
	}
}

action do_map_20001_3() {
	bit_and(meta_map_init_20001.dIP, meta_map_init_20001.dIP, 0xffff0000);
}

header_type meta_distinct_4_20001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_4_20001_t meta_distinct_4_20001;

header_type hash_meta_distinct_4_20001_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_4_20001_t hash_meta_distinct_4_20001;

field_list distinct_4_20001_fields {
	hash_meta_distinct_4_20001.dIP;
}

field_list_calculation distinct_4_20001_fields_hash {
	input {
		distinct_4_20001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_4_20001{
	width : 32;
	instance_count : 4096;
}

action update_distinct_4_20001_regs() {
	bit_or(meta_distinct_4_20001.val,meta_distinct_4_20001.val, 1);
	register_write(distinct_4_20001,meta_distinct_4_20001.idx,meta_distinct_4_20001.val);
}

table update_distinct_4_20001_counts {
	actions {update_distinct_4_20001_regs;}
	size : 1;
}

action do_distinct_4_20001_hashes() {
	modify_field(hash_meta_distinct_4_20001.dIP, meta_map_init_20001.dIP);
	modify_field(meta_distinct_4_20001.qid, 20001);
	modify_field_with_hash_based_offset(meta_distinct_4_20001.idx, 0, distinct_4_20001_fields_hash, 4096);
	register_read(meta_distinct_4_20001.val, distinct_4_20001, meta_distinct_4_20001.idx);
}

table start_distinct_4_20001 {
	actions {do_distinct_4_20001_hashes;}
	size : 1;
}

action set_distinct_4_20001_count() {
	modify_field(meta_distinct_4_20001.val, 1);
}

table set_distinct_4_20001_count {
	actions {set_distinct_4_20001_count;}
        size: 1;
}

table map_init_40002{
	actions{
		do_map_init_40002;
	}
}

action do_map_init_40002(){
	modify_field(meta_map_init_40002.qid, 40002);
	modify_field(meta_map_init_40002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40002_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40002_t meta_map_init_40002;

table map_40002_1{
	actions{
		do_map_40002_1;
	}
}

action do_map_40002_1() {
	bit_and(meta_map_init_40002.dIP, meta_map_init_40002.dIP, 0xf0000000);
}

header_type meta_distinct_2_40002_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_40002_t meta_distinct_2_40002;

header_type hash_meta_distinct_2_40002_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_40002_t hash_meta_distinct_2_40002;

field_list distinct_2_40002_fields {
	hash_meta_distinct_2_40002.dIP;
}

field_list_calculation distinct_2_40002_fields_hash {
	input {
		distinct_2_40002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_40002{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_40002_regs() {
	bit_or(meta_distinct_2_40002.val,meta_distinct_2_40002.val, 1);
	register_write(distinct_2_40002,meta_distinct_2_40002.idx,meta_distinct_2_40002.val);
}

table update_distinct_2_40002_counts {
	actions {update_distinct_2_40002_regs;}
	size : 1;
}

action do_distinct_2_40002_hashes() {
	modify_field(hash_meta_distinct_2_40002.dIP, meta_map_init_40002.dIP);
	modify_field(meta_distinct_2_40002.qid, 40002);
	modify_field_with_hash_based_offset(meta_distinct_2_40002.idx, 0, distinct_2_40002_fields_hash, 4096);
	register_read(meta_distinct_2_40002.val, distinct_2_40002, meta_distinct_2_40002.idx);
}

table start_distinct_2_40002 {
	actions {do_distinct_2_40002_hashes;}
	size : 1;
}

action set_distinct_2_40002_count() {
	modify_field(meta_distinct_2_40002.val, 1);
}

table set_distinct_2_40002_count {
	actions {set_distinct_2_40002_count;}
        size: 1;
}

table map_init_40003{
	actions{
		do_map_init_40003;
	}
}

action do_map_init_40003(){
	modify_field(meta_map_init_40003.qid, 40003);
	modify_field(meta_map_init_40003.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40003_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40003_t meta_map_init_40003;

table map_40003_2{
	actions{
		do_map_40003_2;
	}
}

action do_map_40003_2() {
	bit_and(meta_map_init_40003.dIP, meta_map_init_40003.dIP, 0xff000000);
}

table map_init_20004{
	actions{
		do_map_init_20004;
	}
}

action do_map_init_20004(){
	modify_field(meta_map_init_20004.qid, 20004);
	modify_field(meta_map_init_20004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_20004_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_20004_t meta_map_init_20004;

table map_20004_2{
	actions{
		do_map_20004_2;
	}
}

action do_map_20004_2() {
	bit_and(meta_map_init_20004.dIP, meta_map_init_20004.dIP, 0xffffffff);
}

header_type meta_distinct_3_20004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_20004_t meta_distinct_3_20004;

header_type hash_meta_distinct_3_20004_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_20004_t hash_meta_distinct_3_20004;

field_list distinct_3_20004_fields {
	hash_meta_distinct_3_20004.dIP;
}

field_list_calculation distinct_3_20004_fields_hash {
	input {
		distinct_3_20004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_20004{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_20004_regs() {
	bit_or(meta_distinct_3_20004.val,meta_distinct_3_20004.val, 1);
	register_write(distinct_3_20004,meta_distinct_3_20004.idx,meta_distinct_3_20004.val);
}

table update_distinct_3_20004_counts {
	actions {update_distinct_3_20004_regs;}
	size : 1;
}

action do_distinct_3_20004_hashes() {
	modify_field(hash_meta_distinct_3_20004.dIP, meta_map_init_20004.dIP);
	modify_field(meta_distinct_3_20004.qid, 20004);
	modify_field_with_hash_based_offset(meta_distinct_3_20004.idx, 0, distinct_3_20004_fields_hash, 4096);
	register_read(meta_distinct_3_20004.val, distinct_3_20004, meta_distinct_3_20004.idx);
}

table start_distinct_3_20004 {
	actions {do_distinct_3_20004_hashes;}
	size : 1;
}

action set_distinct_3_20004_count() {
	modify_field(meta_distinct_3_20004.val, 1);
}

table set_distinct_3_20004_count {
	actions {set_distinct_3_20004_count;}
        size: 1;
}

table map_init_40005{
	actions{
		do_map_init_40005;
	}
}

action do_map_init_40005(){
	modify_field(meta_map_init_40005.qid, 40005);
	modify_field(meta_map_init_40005.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40005_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40005_t meta_map_init_40005;

table map_40005_2{
	actions{
		do_map_40005_2;
	}
}

action do_map_40005_2() {
	bit_and(meta_map_init_40005.dIP, meta_map_init_40005.dIP, 0xffff0000);
}

table map_init_40006{
	actions{
		do_map_init_40006;
	}
}

action do_map_init_40006(){
	modify_field(meta_map_init_40006.qid, 40006);
	modify_field(meta_map_init_40006.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40006_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40006_t meta_map_init_40006;

table map_40006_2{
	actions{
		do_map_40006_2;
	}
}

action do_map_40006_2() {
	bit_and(meta_map_init_40006.dIP, meta_map_init_40006.dIP, 0xfffffff0);
}

header_type meta_distinct_3_40006_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_40006_t meta_distinct_3_40006;

header_type hash_meta_distinct_3_40006_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_40006_t hash_meta_distinct_3_40006;

field_list distinct_3_40006_fields {
	hash_meta_distinct_3_40006.dIP;
}

field_list_calculation distinct_3_40006_fields_hash {
	input {
		distinct_3_40006_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_40006{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_40006_regs() {
	bit_or(meta_distinct_3_40006.val,meta_distinct_3_40006.val, 1);
	register_write(distinct_3_40006,meta_distinct_3_40006.idx,meta_distinct_3_40006.val);
}

table update_distinct_3_40006_counts {
	actions {update_distinct_3_40006_regs;}
	size : 1;
}

action do_distinct_3_40006_hashes() {
	modify_field(hash_meta_distinct_3_40006.dIP, meta_map_init_40006.dIP);
	modify_field(meta_distinct_3_40006.qid, 40006);
	modify_field_with_hash_based_offset(meta_distinct_3_40006.idx, 0, distinct_3_40006_fields_hash, 4096);
	register_read(meta_distinct_3_40006.val, distinct_3_40006, meta_distinct_3_40006.idx);
}

table start_distinct_3_40006 {
	actions {do_distinct_3_40006_hashes;}
	size : 1;
}

action set_distinct_3_40006_count() {
	modify_field(meta_distinct_3_40006.val, 1);
}

table set_distinct_3_40006_count {
	actions {set_distinct_3_40006_count;}
        size: 1;
}

table map_init_40001{
	actions{
		do_map_init_40001;
	}
}

action do_map_init_40001(){
	modify_field(meta_map_init_40001.qid, 40001);
	modify_field(meta_map_init_40001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40001_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40001_t meta_map_init_40001;

table map_40001_2{
	actions{
		do_map_40001_2;
	}
}

action do_map_40001_2() {
	bit_and(meta_map_init_40001.dIP, meta_map_init_40001.dIP, 0xffffffff);
}

header_type meta_distinct_3_40001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_40001_t meta_distinct_3_40001;

header_type hash_meta_distinct_3_40001_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_40001_t hash_meta_distinct_3_40001;

field_list distinct_3_40001_fields {
	hash_meta_distinct_3_40001.dIP;
}

field_list_calculation distinct_3_40001_fields_hash {
	input {
		distinct_3_40001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_40001{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_40001_regs() {
	bit_or(meta_distinct_3_40001.val,meta_distinct_3_40001.val, 1);
	register_write(distinct_3_40001,meta_distinct_3_40001.idx,meta_distinct_3_40001.val);
}

table update_distinct_3_40001_counts {
	actions {update_distinct_3_40001_regs;}
	size : 1;
}

action do_distinct_3_40001_hashes() {
	modify_field(hash_meta_distinct_3_40001.dIP, meta_map_init_40001.dIP);
	modify_field(meta_distinct_3_40001.qid, 40001);
	modify_field_with_hash_based_offset(meta_distinct_3_40001.idx, 0, distinct_3_40001_fields_hash, 4096);
	register_read(meta_distinct_3_40001.val, distinct_3_40001, meta_distinct_3_40001.idx);
}

table start_distinct_3_40001 {
	actions {do_distinct_3_40001_hashes;}
	size : 1;
}

action set_distinct_3_40001_count() {
	modify_field(meta_distinct_3_40001.val, 1);
}

table set_distinct_3_40001_count {
	actions {set_distinct_3_40001_count;}
        size: 1;
}

table map_init_20002{
	actions{
		do_map_init_20002;
	}
}

action do_map_init_20002(){
	modify_field(meta_map_init_20002.qid, 20002);
	modify_field(meta_map_init_20002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_20002_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_20002_t meta_map_init_20002;

table map_20002_3{
	actions{
		do_map_20002_3;
	}
}

action do_map_20002_3() {
	bit_and(meta_map_init_20002.dIP, meta_map_init_20002.dIP, 0xfff00000);
}

header_type meta_distinct_4_20002_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_4_20002_t meta_distinct_4_20002;

header_type hash_meta_distinct_4_20002_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_4_20002_t hash_meta_distinct_4_20002;

field_list distinct_4_20002_fields {
	hash_meta_distinct_4_20002.dIP;
}

field_list_calculation distinct_4_20002_fields_hash {
	input {
		distinct_4_20002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_4_20002{
	width : 32;
	instance_count : 4096;
}

action update_distinct_4_20002_regs() {
	bit_or(meta_distinct_4_20002.val,meta_distinct_4_20002.val, 1);
	register_write(distinct_4_20002,meta_distinct_4_20002.idx,meta_distinct_4_20002.val);
}

table update_distinct_4_20002_counts {
	actions {update_distinct_4_20002_regs;}
	size : 1;
}

action do_distinct_4_20002_hashes() {
	modify_field(hash_meta_distinct_4_20002.dIP, meta_map_init_20002.dIP);
	modify_field(meta_distinct_4_20002.qid, 20002);
	modify_field_with_hash_based_offset(meta_distinct_4_20002.idx, 0, distinct_4_20002_fields_hash, 4096);
	register_read(meta_distinct_4_20002.val, distinct_4_20002, meta_distinct_4_20002.idx);
}

table start_distinct_4_20002 {
	actions {do_distinct_4_20002_hashes;}
	size : 1;
}

action set_distinct_4_20002_count() {
	modify_field(meta_distinct_4_20002.val, 1);
}

table set_distinct_4_20002_count {
	actions {set_distinct_4_20002_count;}
        size: 1;
}

table map_init_10001{
	actions{
		do_map_init_10001;
	}
}

action do_map_init_10001(){
	modify_field(meta_map_init_10001.qid, 10001);
	modify_field(meta_map_init_10001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10001_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_10001_t meta_map_init_10001;

table map_10001_2{
	actions{
		do_map_10001_2;
	}
}

action do_map_10001_2() {
	bit_and(meta_map_init_10001.dIP, meta_map_init_10001.dIP, 0xffffffff);
}

table map_init_10002{
	actions{
		do_map_init_10002;
	}
}

action do_map_init_10002(){
	modify_field(meta_map_init_10002.qid, 10002);
	modify_field(meta_map_init_10002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10002_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_10002_t meta_map_init_10002;

table map_10002_2{
	actions{
		do_map_10002_2;
	}
}

action do_map_10002_2() {
	bit_and(meta_map_init_10002.dIP, meta_map_init_10002.dIP, 0xfff00000);
}

table map_init_20003{
	actions{
		do_map_init_20003;
	}
}

action do_map_init_20003(){
	modify_field(meta_map_init_20003.qid, 20003);
	modify_field(meta_map_init_20003.dIP, ipv4.dstAddr);
}

header_type meta_map_init_20003_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_20003_t meta_map_init_20003;

table map_20003_2{
	actions{
		do_map_20003_2;
	}
}

action do_map_20003_2() {
	bit_and(meta_map_init_20003.dIP, meta_map_init_20003.dIP, 0xf0000000);
}

header_type meta_distinct_3_20003_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_20003_t meta_distinct_3_20003;

header_type hash_meta_distinct_3_20003_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_20003_t hash_meta_distinct_3_20003;

field_list distinct_3_20003_fields {
	hash_meta_distinct_3_20003.dIP;
}

field_list_calculation distinct_3_20003_fields_hash {
	input {
		distinct_3_20003_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_20003{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_20003_regs() {
	bit_or(meta_distinct_3_20003.val,meta_distinct_3_20003.val, 1);
	register_write(distinct_3_20003,meta_distinct_3_20003.idx,meta_distinct_3_20003.val);
}

table update_distinct_3_20003_counts {
	actions {update_distinct_3_20003_regs;}
	size : 1;
}

action do_distinct_3_20003_hashes() {
	modify_field(hash_meta_distinct_3_20003.dIP, meta_map_init_20003.dIP);
	modify_field(meta_distinct_3_20003.qid, 20003);
	modify_field_with_hash_based_offset(meta_distinct_3_20003.idx, 0, distinct_3_20003_fields_hash, 4096);
	register_read(meta_distinct_3_20003.val, distinct_3_20003, meta_distinct_3_20003.idx);
}

table start_distinct_3_20003 {
	actions {do_distinct_3_20003_hashes;}
	size : 1;
}

action set_distinct_3_20003_count() {
	modify_field(meta_distinct_3_20003.val, 1);
}

table set_distinct_3_20003_count {
	actions {set_distinct_3_20003_count;}
        size: 1;
}

table map_init_10003{
	actions{
		do_map_init_10003;
	}
}

action do_map_init_10003(){
	modify_field(meta_map_init_10003.qid, 10003);
	modify_field(meta_map_init_10003.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10003_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_10003_t meta_map_init_10003;

table map_10003_2{
	actions{
		do_map_10003_2;
	}
}

action do_map_10003_2() {
	bit_and(meta_map_init_10003.dIP, meta_map_init_10003.dIP, 0xf0000000);
}

header_type meta_distinct_3_10003_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_10003_t meta_distinct_3_10003;

header_type hash_meta_distinct_3_10003_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_10003_t hash_meta_distinct_3_10003;

field_list distinct_3_10003_fields {
	hash_meta_distinct_3_10003.dIP;
}

field_list_calculation distinct_3_10003_fields_hash {
	input {
		distinct_3_10003_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_10003{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_10003_regs() {
	bit_or(meta_distinct_3_10003.val,meta_distinct_3_10003.val, 1);
	register_write(distinct_3_10003,meta_distinct_3_10003.idx,meta_distinct_3_10003.val);
}

table update_distinct_3_10003_counts {
	actions {update_distinct_3_10003_regs;}
	size : 1;
}

action do_distinct_3_10003_hashes() {
	modify_field(hash_meta_distinct_3_10003.dIP, meta_map_init_10003.dIP);
	modify_field(meta_distinct_3_10003.qid, 10003);
	modify_field_with_hash_based_offset(meta_distinct_3_10003.idx, 0, distinct_3_10003_fields_hash, 4096);
	register_read(meta_distinct_3_10003.val, distinct_3_10003, meta_distinct_3_10003.idx);
}

table start_distinct_3_10003 {
	actions {do_distinct_3_10003_hashes;}
	size : 1;
}

action set_distinct_3_10003_count() {
	modify_field(meta_distinct_3_10003.val, 1);
}

table set_distinct_3_10003_count {
	actions {set_distinct_3_10003_count;}
        size: 1;
}

table map_init_40004{
	actions{
		do_map_init_40004;
	}
}

action do_map_init_40004(){
	modify_field(meta_map_init_40004.qid, 40004);
	modify_field(meta_map_init_40004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40004_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40004_t meta_map_init_40004;

table map_40004_2{
	actions{
		do_map_40004_2;
	}
}

action do_map_40004_2() {
	bit_and(meta_map_init_40004.dIP, meta_map_init_40004.dIP, 0xfff00000);
}

header_type meta_fm_t {
	fields {
		qid_20001 : 1;
		qid_40002 : 1;
		qid_40003 : 1;
		qid_20004 : 1;
		qid_40005 : 1;
		qid_40006 : 1;
		qid_40001 : 1;
		qid_20002 : 1;
		qid_10001 : 1;
		qid_10002 : 1;
		qid_20003 : 1;
		qid_10003 : 1;
		qid_40004 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_20001, 1);
	modify_field(meta_fm.qid_40002, 1);
	modify_field(meta_fm.qid_40003, 1);
	modify_field(meta_fm.qid_20004, 1);
	modify_field(meta_fm.qid_40005, 1);
	modify_field(meta_fm.qid_40006, 1);
	modify_field(meta_fm.qid_40001, 1);
	modify_field(meta_fm.qid_20002, 1);
	modify_field(meta_fm.qid_10001, 1);
	modify_field(meta_fm.qid_10002, 1);
	modify_field(meta_fm.qid_20003, 1);
	modify_field(meta_fm.qid_10003, 1);
	modify_field(meta_fm.qid_40004, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_20001(){
	modify_field(meta_fm.qid_20001, 1);
}

action set_meta_fm_40002(){
	modify_field(meta_fm.qid_40002, 1);
}

action set_meta_fm_40003(){
	modify_field(meta_fm.qid_40003, 1);
}

action set_meta_fm_20004(){
	modify_field(meta_fm.qid_20004, 1);
}

action set_meta_fm_40005(){
	modify_field(meta_fm.qid_40005, 1);
}

action set_meta_fm_40006(){
	modify_field(meta_fm.qid_40006, 1);
}

action set_meta_fm_40001(){
	modify_field(meta_fm.qid_40001, 1);
}

action set_meta_fm_20002(){
	modify_field(meta_fm.qid_20002, 1);
}

action set_meta_fm_10001(){
	modify_field(meta_fm.qid_10001, 1);
}

action set_meta_fm_10002(){
	modify_field(meta_fm.qid_10002, 1);
}

action set_meta_fm_20003(){
	modify_field(meta_fm.qid_20003, 1);
}

action set_meta_fm_10003(){
	modify_field(meta_fm.qid_10003, 1);
}

action set_meta_fm_40004(){
	modify_field(meta_fm.qid_40004, 1);
}

action reset_meta_fm_20001(){
	modify_field(meta_fm.qid_20001, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40002(){
	modify_field(meta_fm.qid_40002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40003(){
	modify_field(meta_fm.qid_40003, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_20004(){
	modify_field(meta_fm.qid_20004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40005(){
	modify_field(meta_fm.qid_40005, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40006(){
	modify_field(meta_fm.qid_40006, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40001(){
	modify_field(meta_fm.qid_40001, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_20002(){
	modify_field(meta_fm.qid_20002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10001(){
	modify_field(meta_fm.qid_10001, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10002(){
	modify_field(meta_fm.qid_10002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_20003(){
	modify_field(meta_fm.qid_20003, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10003(){
	modify_field(meta_fm.qid_10003, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40004(){
	modify_field(meta_fm.qid_40004, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_20001_2{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_20001;
		reset_meta_fm_20001;
	}
}

table filter_20001_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_20001;
		reset_meta_fm_20001;
	}
}

table filter_40003_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_40003;
		reset_meta_fm_40003;
	}
}

table filter_20004_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_20004;
		reset_meta_fm_20004;
	}
}

table filter_40005_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_40005;
		reset_meta_fm_40005;
	}
}

table filter_40006_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_40006;
		reset_meta_fm_40006;
	}
}

table filter_40001_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_40001;
		reset_meta_fm_40001;
	}
}

table filter_20002_2{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_20002;
		reset_meta_fm_20002;
	}
}

table filter_20002_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_20002;
		reset_meta_fm_20002;
	}
}

table filter_10001_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_10001;
		reset_meta_fm_10001;
	}
}

table filter_10002_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_10002;
		reset_meta_fm_10002;
	}
}

table filter_20003_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_20003;
		reset_meta_fm_20003;
	}
}

table filter_10003_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_10003;
		reset_meta_fm_10003;
	}
}

table filter_40004_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_40004;
		reset_meta_fm_40004;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_20001== 1){
			apply(filter_20001_2);
		}
		if (meta_fm.qid_20001== 1){
			apply(filter_20001_1);
		}
		if (meta_fm.qid_20001 == 1){
					apply(map_init_20001);
			apply(map_20001_3);
			apply(start_distinct_4_20001);
			if(meta_distinct_4_20001.val > 0) {
				apply(drop_distinct_4_20001_1);
			}
			else if(meta_distinct_4_20001.val == 0) {
				apply(skip_distinct_4_20001_1);
			}
			else {
				apply(drop_distinct_4_20001_2);
			}

			apply(update_distinct_4_20001_counts);
			apply(copy_to_cpu_20001);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_40002 == 1){
					apply(map_init_40002);
			apply(map_40002_1);
			apply(start_distinct_2_40002);
			if(meta_distinct_2_40002.val > 0) {
				apply(drop_distinct_2_40002_1);
			}
			else if(meta_distinct_2_40002.val == 0) {
				apply(skip_distinct_2_40002_1);
			}
			else {
				apply(drop_distinct_2_40002_2);
			}

			apply(update_distinct_2_40002_counts);
			apply(copy_to_cpu_40002);
		}
	}
	if (meta_fm.f1 == 2){
		if (meta_fm.qid_40003== 1){
			apply(filter_40003_1);
		}
		if (meta_fm.qid_40003 == 1){
					apply(map_init_40003);
			apply(map_40003_2);
			apply(copy_to_cpu_40003);
		}
	}
	if (meta_fm.f1 == 3){
		if (meta_fm.qid_20004== 1){
			apply(filter_20004_1);
		}
		if (meta_fm.qid_20004 == 1){
					apply(map_init_20004);
			apply(map_20004_2);
			apply(start_distinct_3_20004);
			if(meta_distinct_3_20004.val > 0) {
				apply(drop_distinct_3_20004_1);
			}
			else if(meta_distinct_3_20004.val == 0) {
				apply(skip_distinct_3_20004_1);
			}
			else {
				apply(drop_distinct_3_20004_2);
			}

			apply(update_distinct_3_20004_counts);
			apply(copy_to_cpu_20004);
		}
	}
	if (meta_fm.f1 == 4){
		if (meta_fm.qid_40005== 1){
			apply(filter_40005_1);
		}
		if (meta_fm.qid_40005 == 1){
					apply(map_init_40005);
			apply(map_40005_2);
			apply(copy_to_cpu_40005);
		}
	}
	if (meta_fm.f1 == 5){
		if (meta_fm.qid_40006== 1){
			apply(filter_40006_1);
		}
		if (meta_fm.qid_40006 == 1){
					apply(map_init_40006);
			apply(map_40006_2);
			apply(start_distinct_3_40006);
			if(meta_distinct_3_40006.val > 0) {
				apply(drop_distinct_3_40006_1);
			}
			else if(meta_distinct_3_40006.val == 0) {
				apply(skip_distinct_3_40006_1);
			}
			else {
				apply(drop_distinct_3_40006_2);
			}

			apply(update_distinct_3_40006_counts);
			apply(copy_to_cpu_40006);
		}
	}
	if (meta_fm.f1 == 6){
		if (meta_fm.qid_40001== 1){
			apply(filter_40001_1);
		}
		if (meta_fm.qid_40001 == 1){
					apply(map_init_40001);
			apply(map_40001_2);
			apply(start_distinct_3_40001);
			if(meta_distinct_3_40001.val > 0) {
				apply(drop_distinct_3_40001_1);
			}
			else if(meta_distinct_3_40001.val == 0) {
				apply(skip_distinct_3_40001_1);
			}
			else {
				apply(drop_distinct_3_40001_2);
			}

			apply(update_distinct_3_40001_counts);
			apply(copy_to_cpu_40001);
		}
	}
	if (meta_fm.f1 == 7){
		if (meta_fm.qid_20002== 1){
			apply(filter_20002_2);
		}
		if (meta_fm.qid_20002== 1){
			apply(filter_20002_1);
		}
		if (meta_fm.qid_20002 == 1){
					apply(map_init_20002);
			apply(map_20002_3);
			apply(start_distinct_4_20002);
			if(meta_distinct_4_20002.val > 0) {
				apply(drop_distinct_4_20002_1);
			}
			else if(meta_distinct_4_20002.val == 0) {
				apply(skip_distinct_4_20002_1);
			}
			else {
				apply(drop_distinct_4_20002_2);
			}

			apply(update_distinct_4_20002_counts);
			apply(copy_to_cpu_20002);
		}
	}
	if (meta_fm.f1 == 8){
		if (meta_fm.qid_10001== 1){
			apply(filter_10001_1);
		}
		if (meta_fm.qid_10001 == 1){
					apply(map_init_10001);
			apply(map_10001_2);
			apply(copy_to_cpu_10001);
		}
	}
	if (meta_fm.f1 == 9){
		if (meta_fm.qid_10002== 1){
			apply(filter_10002_1);
		}
		if (meta_fm.qid_10002 == 1){
					apply(map_init_10002);
			apply(map_10002_2);
			apply(copy_to_cpu_10002);
		}
	}
	if (meta_fm.f1 == 10){
		if (meta_fm.qid_20003== 1){
			apply(filter_20003_1);
		}
		if (meta_fm.qid_20003 == 1){
					apply(map_init_20003);
			apply(map_20003_2);
			apply(start_distinct_3_20003);
			if(meta_distinct_3_20003.val > 0) {
				apply(drop_distinct_3_20003_1);
			}
			else if(meta_distinct_3_20003.val == 0) {
				apply(skip_distinct_3_20003_1);
			}
			else {
				apply(drop_distinct_3_20003_2);
			}

			apply(update_distinct_3_20003_counts);
			apply(copy_to_cpu_20003);
		}
	}
	if (meta_fm.f1 == 11){
		if (meta_fm.qid_10003== 1){
			apply(filter_10003_1);
		}
		if (meta_fm.qid_10003 == 1){
					apply(map_init_10003);
			apply(map_10003_2);
			apply(start_distinct_3_10003);
			if(meta_distinct_3_10003.val > 0) {
				apply(drop_distinct_3_10003_1);
			}
			else if(meta_distinct_3_10003.val == 0) {
				apply(skip_distinct_3_10003_1);
			}
			else {
				apply(drop_distinct_3_10003_2);
			}

			apply(update_distinct_3_10003_counts);
			apply(copy_to_cpu_10003);
		}
	}
	if (meta_fm.f1 == 12){
		if (meta_fm.qid_40004== 1){
			apply(filter_40004_1);
		}
		if (meta_fm.qid_40004 == 1){
					apply(map_init_40004);
			apply(map_40004_2);
			apply(copy_to_cpu_40004);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 13) {
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
				apply(encap_20001);
			}
			if (meta_fm.f1 == 1){
				apply(encap_40002);
			}
			if (meta_fm.f1 == 2){
				apply(encap_40003);
			}
			if (meta_fm.f1 == 3){
				apply(encap_20004);
			}
			if (meta_fm.f1 == 4){
				apply(encap_40005);
			}
			if (meta_fm.f1 == 5){
				apply(encap_40006);
			}
			if (meta_fm.f1 == 6){
				apply(encap_40001);
			}
			if (meta_fm.f1 == 7){
				apply(encap_20002);
			}
			if (meta_fm.f1 == 8){
				apply(encap_10001);
			}
			if (meta_fm.f1 == 9){
				apply(encap_10002);
			}
			if (meta_fm.f1 == 10){
				apply(encap_20003);
			}
			if (meta_fm.f1 == 11){
				apply(encap_10003);
			}
			if (meta_fm.f1 == 12){
				apply(encap_40004);
			}
		}


	}
}

