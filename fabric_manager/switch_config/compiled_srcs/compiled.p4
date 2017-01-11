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
	extract(out_header_40001);
	extract(out_header_40002);
	extract(out_header_40003);
	extract(out_header_20001);
	extract(out_header_20002);
	extract(out_header_10001);
	extract(out_header_10002);
	return parse_ethernet;
}

header_type out_header_40001_t {
	fields {
		qid : 16;
		dIP : 32;
		dPort : 16;}
}

header out_header_40001_t out_header_40001;

field_list copy_to_cpu_fields_40001{
	standard_metadata;
	hash_meta_distinct_2_40001;
	meta_distinct_2_40001;
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
	modify_field(out_header_40001.qid, meta_distinct_2_40001.qid);
	modify_field(out_header_40001.dIP, meta_map_init_40001.dIP);
	modify_field(out_header_40001.dPort, meta_map_init_40001.dPort);
}

header_type out_header_40002_t {
	fields {
		qid : 16;
		dIP : 32;
		dPort : 16;}
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
	modify_field(out_header_40002.dPort, meta_map_init_40002.dPort);
}

header_type out_header_40003_t {
	fields {
		qid : 16;
		dPort : 16;
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
	modify_field(out_header_40003.dPort, meta_map_init_40003.dPort);
	modify_field(out_header_40003.dIP, meta_map_init_40003.dIP);
}

header_type out_header_20001_t {
	fields {
		qid : 16;
		dIP : 32;
		sPort : 16;
		proto : 16;
		sMac : 48;
		sIP : 32;
		count : 16;
	}
}

header out_header_20001_t out_header_20001;

field_list copy_to_cpu_fields_20001{
	standard_metadata;
	hash_meta_reduce_4_20001;
	meta_reduce_4_20001;
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
	modify_field(out_header_20001.qid, meta_reduce_4_20001.qid);
	modify_field(out_header_20001.dIP, meta_map_init_20001.dIP);
	modify_field(out_header_20001.sPort, meta_map_init_20001.sPort);
	modify_field(out_header_20001.proto, meta_map_init_20001.proto);
	modify_field(out_header_20001.sMac, meta_map_init_20001.sMac);
	modify_field(out_header_20001.sIP, meta_map_init_20001.sIP);
	modify_field(out_header_20001.count, meta_reduce_4_20001.val);
}

header_type out_header_20002_t {
	fields {
		qid : 16;
		dIP : 32;
		sPort : 16;
		proto : 16;
		sMac : 48;
		sIP : 32;
		count : 16;
	}
}

header out_header_20002_t out_header_20002;

field_list copy_to_cpu_fields_20002{
	standard_metadata;
	hash_meta_reduce_5_20002;
	meta_reduce_5_20002;
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
	modify_field(out_header_20002.qid, meta_reduce_5_20002.qid);
	modify_field(out_header_20002.dIP, meta_map_init_20002.dIP);
	modify_field(out_header_20002.sPort, meta_map_init_20002.sPort);
	modify_field(out_header_20002.proto, meta_map_init_20002.proto);
	modify_field(out_header_20002.sMac, meta_map_init_20002.sMac);
	modify_field(out_header_20002.sIP, meta_map_init_20002.sIP);
	modify_field(out_header_20002.count, meta_reduce_5_20002.val);
}

header_type out_header_10001_t {
	fields {
		qid : 16;
		sMac : 48;
		sIP : 32;
		proto : 16;
		dPort : 16;
		sPort : 16;
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
	modify_field(out_header_10001.sMac, meta_map_init_10001.sMac);
	modify_field(out_header_10001.sIP, meta_map_init_10001.sIP);
	modify_field(out_header_10001.proto, meta_map_init_10001.proto);
	modify_field(out_header_10001.dPort, meta_map_init_10001.dPort);
	modify_field(out_header_10001.sPort, meta_map_init_10001.sPort);
	modify_field(out_header_10001.dIP, meta_map_init_10001.dIP);
}

header_type out_header_10002_t {
	fields {
		qid : 16;
		sMac : 48;
		sIP : 32;
		proto : 16;
		dPort : 16;
		sPort : 16;
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
	modify_field(out_header_10002.sMac, meta_map_init_10002.sMac);
	modify_field(out_header_10002.sIP, meta_map_init_10002.sIP);
	modify_field(out_header_10002.proto, meta_map_init_10002.proto);
	modify_field(out_header_10002.dPort, meta_map_init_10002.dPort);
	modify_field(out_header_10002.sPort, meta_map_init_10002.sPort);
	modify_field(out_header_10002.dIP, meta_map_init_10002.dIP);
}

table drop_distinct_2_40001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_40001_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_40001_2 {
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

table skip_reduce_3_20001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_20001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_20001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_20001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_20002_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_20002_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_20002_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_20002_1 {
	actions {mark_drop;}
	size : 1;
}

table map_init_40001{
	actions{
		do_map_init_40001;
	}
}

action do_map_init_40001(){
	modify_field(meta_map_init_40001.qid, 40001);
	modify_field(meta_map_init_40001.dPort, tcp.dstPort);
	modify_field(meta_map_init_40001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40001_t {
	 fields {
		qid: 16;
		dPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40001_t meta_map_init_40001;

table map_40001_1{
	actions{
		do_map_40001_1;
	}
}

action do_map_40001_1() {
	bit_and(meta_map_init_40001.dIP, meta_map_init_40001.dIP, 0xff000000);
}

header_type meta_distinct_2_40001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_40001_t meta_distinct_2_40001;

header_type hash_meta_distinct_2_40001_t {
	fields {
		dPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_40001_t hash_meta_distinct_2_40001;

field_list distinct_2_40001_fields {
	hash_meta_distinct_2_40001.dPort;
	hash_meta_distinct_2_40001.dIP;
}

field_list_calculation distinct_2_40001_fields_hash {
	input {
		distinct_2_40001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_40001{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_40001_regs() {
	bit_or(meta_distinct_2_40001.val,meta_distinct_2_40001.val, 1);
	register_write(distinct_2_40001,meta_distinct_2_40001.idx,meta_distinct_2_40001.val);
}

table update_distinct_2_40001_counts {
	actions {update_distinct_2_40001_regs;}
	size : 1;
}

action do_distinct_2_40001_hashes() {
	modify_field(hash_meta_distinct_2_40001.dPort, meta_map_init_40001.dPort);
	modify_field(hash_meta_distinct_2_40001.dIP, meta_map_init_40001.dIP);
	modify_field(meta_distinct_2_40001.qid, 40001);
	modify_field_with_hash_based_offset(meta_distinct_2_40001.idx, 0, distinct_2_40001_fields_hash, 4096);
	register_read(meta_distinct_2_40001.val, distinct_2_40001, meta_distinct_2_40001.idx);
}

table start_distinct_2_40001 {
	actions {do_distinct_2_40001_hashes;}
	size : 1;
}

action set_distinct_2_40001_count() {
	modify_field(meta_distinct_2_40001.val, 1);
}

table set_distinct_2_40001_count {
	actions {set_distinct_2_40001_count;}
        size: 1;
}

table map_init_40002{
	actions{
		do_map_init_40002;
	}
}

action do_map_init_40002(){
	modify_field(meta_map_init_40002.qid, 40002);
	modify_field(meta_map_init_40002.dPort, tcp.dstPort);
	modify_field(meta_map_init_40002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40002_t {
	 fields {
		qid: 16;
		dPort: 16;
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
	bit_and(meta_map_init_40002.dIP, meta_map_init_40002.dIP, 0xffff0000);
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
		dPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_40002_t hash_meta_distinct_2_40002;

field_list distinct_2_40002_fields {
	hash_meta_distinct_2_40002.dPort;
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
	modify_field(hash_meta_distinct_2_40002.dPort, meta_map_init_40002.dPort);
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
	modify_field(meta_map_init_40003.dPort, tcp.dstPort);
	modify_field(meta_map_init_40003.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40003_t {
	 fields {
		qid: 16;
		dPort: 16;
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
	bit_and(meta_map_init_40003.dIP, meta_map_init_40003.dIP, 0xffffffff);
}

table map_init_20001{
	actions{
		do_map_init_20001;
	}
}

action do_map_init_20001(){
	modify_field(meta_map_init_20001.qid, 20001);
	modify_field(meta_map_init_20001.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_20001.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_20001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20001.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_20001.proto, ipv4.protocol);
	modify_field(meta_map_init_20001.sPort, tcp.srcPort);
	modify_field(meta_map_init_20001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_20001_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
		nBytes: 16;
		proto: 16;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_20001_t meta_map_init_20001;

table map_20001_2{
	actions{
		do_map_20001_2;
	}
}

action do_map_20001_2() {
	bit_and(meta_map_init_20001.dIP, meta_map_init_20001.dIP, 0xff000000);
}

header_type meta_reduce_3_20001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_20001_t meta_reduce_3_20001;

header_type hash_meta_reduce_3_20001_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_20001_t hash_meta_reduce_3_20001;

field_list reduce_3_20001_fields {
	hash_meta_reduce_3_20001.dMac;
	hash_meta_reduce_3_20001.sIP;
	hash_meta_reduce_3_20001.proto;
	hash_meta_reduce_3_20001.sMac;
	hash_meta_reduce_3_20001.nBytes;
	hash_meta_reduce_3_20001.sPort;
	hash_meta_reduce_3_20001.dIP;
}

field_list_calculation reduce_3_20001_fields_hash {
	input {
		reduce_3_20001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_20001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_20001_regs() {
	add_to_field(meta_reduce_3_20001.val, 1);
	register_write(reduce_3_20001,meta_reduce_3_20001.idx,meta_reduce_3_20001.val);
}

table update_reduce_3_20001_counts {
	actions {update_reduce_3_20001_regs;}
	size : 1;
}

action do_reduce_3_20001_hashes() {
	modify_field(hash_meta_reduce_3_20001.dMac, meta_map_init_20001.dMac);
	modify_field(hash_meta_reduce_3_20001.sIP, meta_map_init_20001.sIP);
	modify_field(hash_meta_reduce_3_20001.proto, meta_map_init_20001.proto);
	modify_field(hash_meta_reduce_3_20001.sMac, meta_map_init_20001.sMac);
	modify_field(hash_meta_reduce_3_20001.nBytes, meta_map_init_20001.nBytes);
	modify_field(hash_meta_reduce_3_20001.sPort, meta_map_init_20001.sPort);
	modify_field(hash_meta_reduce_3_20001.dIP, meta_map_init_20001.dIP);
	modify_field(meta_reduce_3_20001.qid, 20001);
	modify_field_with_hash_based_offset(meta_reduce_3_20001.idx, 0, reduce_3_20001_fields_hash, 4096);
	register_read(meta_reduce_3_20001.val, reduce_3_20001, meta_reduce_3_20001.idx);
}

table start_reduce_3_20001 {
	actions {do_reduce_3_20001_hashes;}
	size : 1;
}

action set_reduce_3_20001_count() {
	modify_field(meta_reduce_3_20001.val, 1);
}

table set_reduce_3_20001_count {
	actions {set_reduce_3_20001_count;}
        size: 1;
}

header_type meta_reduce_4_20001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_20001_t meta_reduce_4_20001;

header_type hash_meta_reduce_4_20001_t {
	fields {
		sMac : 48;
		sIP : 32;
		sPort : 16;
		dIP : 32;
		proto : 16;
	}
}

metadata hash_meta_reduce_4_20001_t hash_meta_reduce_4_20001;

field_list reduce_4_20001_fields {
	hash_meta_reduce_4_20001.sMac;
	hash_meta_reduce_4_20001.sIP;
	hash_meta_reduce_4_20001.sPort;
	hash_meta_reduce_4_20001.dIP;
	hash_meta_reduce_4_20001.proto;
}

field_list_calculation reduce_4_20001_fields_hash {
	input {
		reduce_4_20001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_20001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_20001_regs() {
	add_to_field(meta_reduce_4_20001.val, 1);
	register_write(reduce_4_20001,meta_reduce_4_20001.idx,meta_reduce_4_20001.val);
}

table update_reduce_4_20001_counts {
	actions {update_reduce_4_20001_regs;}
	size : 1;
}

action do_reduce_4_20001_hashes() {
	modify_field(hash_meta_reduce_4_20001.sMac, meta_map_init_20001.sMac);
	modify_field(hash_meta_reduce_4_20001.sIP, meta_map_init_20001.sIP);
	modify_field(hash_meta_reduce_4_20001.sPort, meta_map_init_20001.sPort);
	modify_field(hash_meta_reduce_4_20001.dIP, meta_map_init_20001.dIP);
	modify_field(hash_meta_reduce_4_20001.proto, meta_map_init_20001.proto);
	modify_field(meta_reduce_4_20001.qid, 20001);
	modify_field_with_hash_based_offset(meta_reduce_4_20001.idx, 0, reduce_4_20001_fields_hash, 4096);
	register_read(meta_reduce_4_20001.val, reduce_4_20001, meta_reduce_4_20001.idx);
}

table start_reduce_4_20001 {
	actions {do_reduce_4_20001_hashes;}
	size : 1;
}

action set_reduce_4_20001_count() {
	modify_field(meta_reduce_4_20001.val, 1);
}

table set_reduce_4_20001_count {
	actions {set_reduce_4_20001_count;}
        size: 1;
}

table map_init_20002{
	actions{
		do_map_init_20002;
	}
}

action do_map_init_20002(){
	modify_field(meta_map_init_20002.qid, 20002);
	modify_field(meta_map_init_20002.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_20002.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_20002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20002.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_20002.proto, ipv4.protocol);
	modify_field(meta_map_init_20002.sPort, tcp.srcPort);
	modify_field(meta_map_init_20002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_20002_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
		nBytes: 16;
		proto: 16;
		sPort: 16;
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
	bit_and(meta_map_init_20002.dIP, meta_map_init_20002.dIP, 0xffffffff);
}

header_type meta_reduce_4_20002_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_20002_t meta_reduce_4_20002;

header_type hash_meta_reduce_4_20002_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_20002_t hash_meta_reduce_4_20002;

field_list reduce_4_20002_fields {
	hash_meta_reduce_4_20002.dMac;
	hash_meta_reduce_4_20002.sIP;
	hash_meta_reduce_4_20002.proto;
	hash_meta_reduce_4_20002.sMac;
	hash_meta_reduce_4_20002.nBytes;
	hash_meta_reduce_4_20002.sPort;
	hash_meta_reduce_4_20002.dIP;
}

field_list_calculation reduce_4_20002_fields_hash {
	input {
		reduce_4_20002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_20002{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_20002_regs() {
	add_to_field(meta_reduce_4_20002.val, 1);
	register_write(reduce_4_20002,meta_reduce_4_20002.idx,meta_reduce_4_20002.val);
}

table update_reduce_4_20002_counts {
	actions {update_reduce_4_20002_regs;}
	size : 1;
}

action do_reduce_4_20002_hashes() {
	modify_field(hash_meta_reduce_4_20002.dMac, meta_map_init_20002.dMac);
	modify_field(hash_meta_reduce_4_20002.sIP, meta_map_init_20002.sIP);
	modify_field(hash_meta_reduce_4_20002.proto, meta_map_init_20002.proto);
	modify_field(hash_meta_reduce_4_20002.sMac, meta_map_init_20002.sMac);
	modify_field(hash_meta_reduce_4_20002.nBytes, meta_map_init_20002.nBytes);
	modify_field(hash_meta_reduce_4_20002.sPort, meta_map_init_20002.sPort);
	modify_field(hash_meta_reduce_4_20002.dIP, meta_map_init_20002.dIP);
	modify_field(meta_reduce_4_20002.qid, 20002);
	modify_field_with_hash_based_offset(meta_reduce_4_20002.idx, 0, reduce_4_20002_fields_hash, 4096);
	register_read(meta_reduce_4_20002.val, reduce_4_20002, meta_reduce_4_20002.idx);
}

table start_reduce_4_20002 {
	actions {do_reduce_4_20002_hashes;}
	size : 1;
}

action set_reduce_4_20002_count() {
	modify_field(meta_reduce_4_20002.val, 1);
}

table set_reduce_4_20002_count {
	actions {set_reduce_4_20002_count;}
        size: 1;
}

header_type meta_reduce_5_20002_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_20002_t meta_reduce_5_20002;

header_type hash_meta_reduce_5_20002_t {
	fields {
		sMac : 48;
		sIP : 32;
		sPort : 16;
		dIP : 32;
		proto : 16;
	}
}

metadata hash_meta_reduce_5_20002_t hash_meta_reduce_5_20002;

field_list reduce_5_20002_fields {
	hash_meta_reduce_5_20002.sMac;
	hash_meta_reduce_5_20002.sIP;
	hash_meta_reduce_5_20002.sPort;
	hash_meta_reduce_5_20002.dIP;
	hash_meta_reduce_5_20002.proto;
}

field_list_calculation reduce_5_20002_fields_hash {
	input {
		reduce_5_20002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_20002{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_20002_regs() {
	add_to_field(meta_reduce_5_20002.val, 1);
	register_write(reduce_5_20002,meta_reduce_5_20002.idx,meta_reduce_5_20002.val);
}

table update_reduce_5_20002_counts {
	actions {update_reduce_5_20002_regs;}
	size : 1;
}

action do_reduce_5_20002_hashes() {
	modify_field(hash_meta_reduce_5_20002.sMac, meta_map_init_20002.sMac);
	modify_field(hash_meta_reduce_5_20002.sIP, meta_map_init_20002.sIP);
	modify_field(hash_meta_reduce_5_20002.sPort, meta_map_init_20002.sPort);
	modify_field(hash_meta_reduce_5_20002.dIP, meta_map_init_20002.dIP);
	modify_field(hash_meta_reduce_5_20002.proto, meta_map_init_20002.proto);
	modify_field(meta_reduce_5_20002.qid, 20002);
	modify_field_with_hash_based_offset(meta_reduce_5_20002.idx, 0, reduce_5_20002_fields_hash, 4096);
	register_read(meta_reduce_5_20002.val, reduce_5_20002, meta_reduce_5_20002.idx);
}

table start_reduce_5_20002 {
	actions {do_reduce_5_20002_hashes;}
	size : 1;
}

action set_reduce_5_20002_count() {
	modify_field(meta_reduce_5_20002.val, 1);
}

table set_reduce_5_20002_count {
	actions {set_reduce_5_20002_count;}
        size: 1;
}

table map_init_10001{
	actions{
		do_map_init_10001;
	}
}

action do_map_init_10001(){
	modify_field(meta_map_init_10001.qid, 10001);
	modify_field(meta_map_init_10001.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_10001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10001.proto, ipv4.protocol);
	modify_field(meta_map_init_10001.dPort, tcp.dstPort);
	modify_field(meta_map_init_10001.sPort, tcp.srcPort);
	modify_field(meta_map_init_10001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10001_t {
	 fields {
		qid: 16;
		sMac: 48;
		sIP: 32;
		proto: 16;
		dPort: 16;
		sPort: 16;
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
	bit_and(meta_map_init_10001.dIP, meta_map_init_10001.dIP, 0xff000000);
}

table map_init_10002{
	actions{
		do_map_init_10002;
	}
}

action do_map_init_10002(){
	modify_field(meta_map_init_10002.qid, 10002);
	modify_field(meta_map_init_10002.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_10002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10002.proto, ipv4.protocol);
	modify_field(meta_map_init_10002.dPort, tcp.dstPort);
	modify_field(meta_map_init_10002.sPort, tcp.srcPort);
	modify_field(meta_map_init_10002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10002_t {
	 fields {
		qid: 16;
		sMac: 48;
		sIP: 32;
		proto: 16;
		dPort: 16;
		sPort: 16;
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
	bit_and(meta_map_init_10002.dIP, meta_map_init_10002.dIP, 0xffffffff);
}

header_type meta_fm_t {
	fields {
		qid_40001 : 1;
		qid_40002 : 1;
		qid_40003 : 1;
		qid_20001 : 1;
		qid_20002 : 1;
		qid_10001 : 1;
		qid_10002 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_40001, 1);
	modify_field(meta_fm.qid_40002, 1);
	modify_field(meta_fm.qid_40003, 1);
	modify_field(meta_fm.qid_20001, 1);
	modify_field(meta_fm.qid_20002, 1);
	modify_field(meta_fm.qid_10001, 1);
	modify_field(meta_fm.qid_10002, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_40001(){
	modify_field(meta_fm.qid_40001, 1);
}

action set_meta_fm_40002(){
	modify_field(meta_fm.qid_40002, 1);
}

action set_meta_fm_40003(){
	modify_field(meta_fm.qid_40003, 1);
}

action set_meta_fm_20001(){
	modify_field(meta_fm.qid_20001, 1);
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

action reset_meta_fm_40001(){
	modify_field(meta_fm.qid_40001, 0);
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

action reset_meta_fm_20001(){
	modify_field(meta_fm.qid_20001, 0);
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

table filter_40003_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_40003;
		reset_meta_fm_40003;
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

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_40001 == 1){
					apply(map_init_40001);
			apply(map_40001_1);
			apply(start_distinct_2_40001);
			if(meta_distinct_2_40001.val > 0) {
				apply(drop_distinct_2_40001_1);
			}
			else if(meta_distinct_2_40001.val == 0) {
				apply(skip_distinct_2_40001_1);
			}
			else {
				apply(drop_distinct_2_40001_2);
			}

			apply(update_distinct_2_40001_counts);
			apply(copy_to_cpu_40001);
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
		if (meta_fm.qid_20001== 1){
			apply(filter_20001_1);
		}
		if (meta_fm.qid_20001 == 1){
					apply(map_init_20001);
			apply(map_20001_2);
			apply(start_reduce_3_20001);
			apply(start_reduce_4_20001);
			apply(update_reduce_3_20001_counts);
			if(meta_reduce_3_20001.val > 2) {
				apply(set_reduce_3_20001_count);			}
			else if(meta_reduce_3_20001.val == 2) {
				apply(skip_reduce_3_20001_1);
			}
			else {
				apply(drop_reduce_3_20001_1);
			}

			apply(update_reduce_4_20001_counts);
			if(meta_reduce_4_20001.val > 2) {
				apply(set_reduce_4_20001_count);			}
			else if(meta_reduce_4_20001.val == 2) {
				apply(skip_reduce_4_20001_1);
			}
			else {
				apply(drop_reduce_4_20001_1);
			}

			apply(copy_to_cpu_20001);
		}
	}
	if (meta_fm.f1 == 4){
		if (meta_fm.qid_20002== 1){
			apply(filter_20002_2);
		}
		if (meta_fm.qid_20002== 1){
			apply(filter_20002_1);
		}
		if (meta_fm.qid_20002 == 1){
					apply(map_init_20002);
			apply(map_20002_3);
			apply(start_reduce_4_20002);
			apply(start_reduce_5_20002);
			apply(update_reduce_4_20002_counts);
			if(meta_reduce_4_20002.val > 2) {
				apply(set_reduce_4_20002_count);			}
			else if(meta_reduce_4_20002.val == 2) {
				apply(skip_reduce_4_20002_1);
			}
			else {
				apply(drop_reduce_4_20002_1);
			}

			apply(update_reduce_5_20002_counts);
			if(meta_reduce_5_20002.val > 2) {
				apply(set_reduce_5_20002_count);			}
			else if(meta_reduce_5_20002.val == 2) {
				apply(skip_reduce_5_20002_1);
			}
			else {
				apply(drop_reduce_5_20002_1);
			}

			apply(copy_to_cpu_20002);
		}
	}
	if (meta_fm.f1 == 5){
		if (meta_fm.qid_10001== 1){
			apply(filter_10001_1);
		}
		if (meta_fm.qid_10001 == 1){
					apply(map_init_10001);
			apply(map_10001_2);
			apply(copy_to_cpu_10001);
		}
	}
	if (meta_fm.f1 == 6){
		if (meta_fm.qid_10002== 1){
			apply(filter_10002_1);
		}
		if (meta_fm.qid_10002 == 1){
					apply(map_init_10002);
			apply(map_10002_2);
			apply(copy_to_cpu_10002);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 7) {
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
				apply(encap_40001);
			}
			if (meta_fm.f1 == 1){
				apply(encap_40002);
			}
			if (meta_fm.f1 == 2){
				apply(encap_40003);
			}
			if (meta_fm.f1 == 3){
				apply(encap_20001);
			}
			if (meta_fm.f1 == 4){
				apply(encap_20002);
			}
			if (meta_fm.f1 == 5){
				apply(encap_10001);
			}
			if (meta_fm.f1 == 6){
				apply(encap_10002);
			}
		}


	}
}

