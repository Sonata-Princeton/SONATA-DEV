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
	extract(out_header_10002);
	extract(out_header_20003);
	extract(out_header_20002);
	extract(out_header_10001);
	return parse_ethernet;
}

header_type out_header_20001_t {
	fields {
		qid : 16;
		sIP : 32;
		dIP : 32;
		dPort : 16;
		proto : 16;
		count : 16;
	}
}

header out_header_20001_t out_header_20001;

field_list copy_to_cpu_fields_20001{
	standard_metadata;
	hash_meta_reduce_2_20001;
	meta_reduce_2_20001;
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
	modify_field(out_header_20001.qid, meta_reduce_2_20001.qid);
	modify_field(out_header_20001.sIP, meta_map_init_20001.sIP);
	modify_field(out_header_20001.dIP, meta_map_init_20001.dIP);
	modify_field(out_header_20001.dPort, meta_map_init_20001.dPort);
	modify_field(out_header_20001.proto, meta_map_init_20001.proto);
	modify_field(out_header_20001.count, meta_reduce_2_20001.val);
}

header_type out_header_10002_t {
	fields {
		qid : 16;
		sMac : 48;
		dMac : 48;
		sIP : 32;
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
	modify_field(out_header_10002.dMac, meta_map_init_10002.dMac);
	modify_field(out_header_10002.sIP, meta_map_init_10002.sIP);
	modify_field(out_header_10002.dPort, meta_map_init_10002.dPort);
	modify_field(out_header_10002.sPort, meta_map_init_10002.sPort);
	modify_field(out_header_10002.dIP, meta_map_init_10002.dIP);
}

header_type out_header_20003_t {
	fields {
		qid : 16;
		sIP : 32;
		dIP : 32;
		dPort : 16;
		proto : 16;
		count : 16;
	}
}

header out_header_20003_t out_header_20003;

field_list copy_to_cpu_fields_20003{
	standard_metadata;
	hash_meta_reduce_3_20003;
	meta_reduce_3_20003;
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
	modify_field(out_header_20003.qid, meta_reduce_3_20003.qid);
	modify_field(out_header_20003.sIP, meta_map_init_20003.sIP);
	modify_field(out_header_20003.dIP, meta_map_init_20003.dIP);
	modify_field(out_header_20003.dPort, meta_map_init_20003.dPort);
	modify_field(out_header_20003.proto, meta_map_init_20003.proto);
	modify_field(out_header_20003.count, meta_reduce_3_20003.val);
}

header_type out_header_20002_t {
	fields {
		qid : 16;
		sIP : 32;
		dIP : 32;
		dPort : 16;
		proto : 16;
		count : 16;
	}
}

header out_header_20002_t out_header_20002;

field_list copy_to_cpu_fields_20002{
	standard_metadata;
	hash_meta_reduce_3_20002;
	meta_reduce_3_20002;
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
	modify_field(out_header_20002.qid, meta_reduce_3_20002.qid);
	modify_field(out_header_20002.sIP, meta_map_init_20002.sIP);
	modify_field(out_header_20002.dIP, meta_map_init_20002.dIP);
	modify_field(out_header_20002.dPort, meta_map_init_20002.dPort);
	modify_field(out_header_20002.proto, meta_map_init_20002.proto);
	modify_field(out_header_20002.count, meta_reduce_3_20002.val);
}

header_type out_header_10001_t {
	fields {
		qid : 16;
		dIP : 32;
		sMac : 48;
		dPort : 16;
		sPort : 16;
		dMac : 48;
		sIP : 32;
		count : 16;
	}
}

header out_header_10001_t out_header_10001;

field_list copy_to_cpu_fields_10001{
	standard_metadata;
	hash_meta_reduce_3_10001;
	meta_reduce_3_10001;
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
	modify_field(out_header_10001.qid, meta_reduce_3_10001.qid);
	modify_field(out_header_10001.dIP, meta_map_init_10001.dIP);
	modify_field(out_header_10001.sMac, meta_map_init_10001.sMac);
	modify_field(out_header_10001.dPort, meta_map_init_10001.dPort);
	modify_field(out_header_10001.sPort, meta_map_init_10001.sPort);
	modify_field(out_header_10001.dMac, meta_map_init_10001.dMac);
	modify_field(out_header_10001.sIP, meta_map_init_10001.sIP);
	modify_field(out_header_10001.count, meta_reduce_3_10001.val);
}

table skip_reduce_2_20001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_2_20001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_20003_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_20003_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_20002_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_20002_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_10001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_10001_1 {
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
	modify_field(meta_map_init_20001.dPort, tcp.dstPort);
	modify_field(meta_map_init_20001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20001.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_20001.proto, ipv4.protocol);
}

header_type meta_map_init_20001_t {
	 fields {
		qid: 16;
		dPort: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_20001_t meta_map_init_20001;

table map_20001_1{
	actions{
		do_map_20001_1;
	}
}

action do_map_20001_1() {
	bit_and(meta_map_init_20001.sIP, meta_map_init_20001.sIP, 0xff000000);
}

header_type meta_reduce_2_20001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_20001_t meta_reduce_2_20001;

header_type hash_meta_reduce_2_20001_t {
	fields {
		dPort : 16;
		sIP : 32;
		dIP : 32;
		proto : 16;
	}
}

metadata hash_meta_reduce_2_20001_t hash_meta_reduce_2_20001;

field_list reduce_2_20001_fields {
	hash_meta_reduce_2_20001.dPort;
	hash_meta_reduce_2_20001.sIP;
	hash_meta_reduce_2_20001.dIP;
	hash_meta_reduce_2_20001.proto;
}

field_list_calculation reduce_2_20001_fields_hash {
	input {
		reduce_2_20001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_2_20001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_2_20001_regs() {
	add_to_field(meta_reduce_2_20001.val, 1);
	register_write(reduce_2_20001,meta_reduce_2_20001.idx,meta_reduce_2_20001.val);
}

table update_reduce_2_20001_counts {
	actions {update_reduce_2_20001_regs;}
	size : 1;
}

action do_reduce_2_20001_hashes() {
	modify_field(hash_meta_reduce_2_20001.dPort, meta_map_init_20001.dPort);
	modify_field(hash_meta_reduce_2_20001.sIP, meta_map_init_20001.sIP);
	modify_field(hash_meta_reduce_2_20001.dIP, meta_map_init_20001.dIP);
	modify_field(hash_meta_reduce_2_20001.proto, meta_map_init_20001.proto);
	modify_field(meta_reduce_2_20001.qid, 20001);
	modify_field_with_hash_based_offset(meta_reduce_2_20001.idx, 0, reduce_2_20001_fields_hash, 4096);
	register_read(meta_reduce_2_20001.val, reduce_2_20001, meta_reduce_2_20001.idx);
}

table start_reduce_2_20001 {
	actions {do_reduce_2_20001_hashes;}
	size : 1;
}

action set_reduce_2_20001_count() {
	modify_field(meta_reduce_2_20001.val, 1);
}

table set_reduce_2_20001_count {
	actions {set_reduce_2_20001_count;}
        size: 1;
}

table map_init_10002{
	actions{
		do_map_init_10002;
	}
}

action do_map_init_10002(){
	modify_field(meta_map_init_10002.qid, 10002);
	modify_field(meta_map_init_10002.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_10002.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_10002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10002.dPort, tcp.dstPort);
	modify_field(meta_map_init_10002.sPort, tcp.srcPort);
	modify_field(meta_map_init_10002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10002_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
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
	bit_and(meta_map_init_10002.sIP, meta_map_init_10002.sIP, 0xffffffff);
}

table map_init_20003{
	actions{
		do_map_init_20003;
	}
}

action do_map_init_20003(){
	modify_field(meta_map_init_20003.qid, 20003);
	modify_field(meta_map_init_20003.dPort, tcp.dstPort);
	modify_field(meta_map_init_20003.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20003.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_20003.proto, ipv4.protocol);
}

header_type meta_map_init_20003_t {
	 fields {
		qid: 16;
		dPort: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_20003_t meta_map_init_20003;

table map_20003_2{
	actions{
		do_map_20003_2;
	}
}

action do_map_20003_2() {
	bit_and(meta_map_init_20003.sIP, meta_map_init_20003.sIP, 0xffffffff);
}

header_type meta_reduce_3_20003_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_20003_t meta_reduce_3_20003;

header_type hash_meta_reduce_3_20003_t {
	fields {
		dPort : 16;
		sIP : 32;
		dIP : 32;
		proto : 16;
	}
}

metadata hash_meta_reduce_3_20003_t hash_meta_reduce_3_20003;

field_list reduce_3_20003_fields {
	hash_meta_reduce_3_20003.dPort;
	hash_meta_reduce_3_20003.sIP;
	hash_meta_reduce_3_20003.dIP;
	hash_meta_reduce_3_20003.proto;
}

field_list_calculation reduce_3_20003_fields_hash {
	input {
		reduce_3_20003_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_20003{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_20003_regs() {
	add_to_field(meta_reduce_3_20003.val, 1);
	register_write(reduce_3_20003,meta_reduce_3_20003.idx,meta_reduce_3_20003.val);
}

table update_reduce_3_20003_counts {
	actions {update_reduce_3_20003_regs;}
	size : 1;
}

action do_reduce_3_20003_hashes() {
	modify_field(hash_meta_reduce_3_20003.dPort, meta_map_init_20003.dPort);
	modify_field(hash_meta_reduce_3_20003.sIP, meta_map_init_20003.sIP);
	modify_field(hash_meta_reduce_3_20003.dIP, meta_map_init_20003.dIP);
	modify_field(hash_meta_reduce_3_20003.proto, meta_map_init_20003.proto);
	modify_field(meta_reduce_3_20003.qid, 20003);
	modify_field_with_hash_based_offset(meta_reduce_3_20003.idx, 0, reduce_3_20003_fields_hash, 4096);
	register_read(meta_reduce_3_20003.val, reduce_3_20003, meta_reduce_3_20003.idx);
}

table start_reduce_3_20003 {
	actions {do_reduce_3_20003_hashes;}
	size : 1;
}

action set_reduce_3_20003_count() {
	modify_field(meta_reduce_3_20003.val, 1);
}

table set_reduce_3_20003_count {
	actions {set_reduce_3_20003_count;}
        size: 1;
}

table map_init_20002{
	actions{
		do_map_init_20002;
	}
}

action do_map_init_20002(){
	modify_field(meta_map_init_20002.qid, 20002);
	modify_field(meta_map_init_20002.dPort, tcp.dstPort);
	modify_field(meta_map_init_20002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20002.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_20002.proto, ipv4.protocol);
}

header_type meta_map_init_20002_t {
	 fields {
		qid: 16;
		dPort: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_20002_t meta_map_init_20002;

table map_20002_2{
	actions{
		do_map_20002_2;
	}
}

action do_map_20002_2() {
	bit_and(meta_map_init_20002.sIP, meta_map_init_20002.sIP, 0xffffff00);
}

header_type meta_reduce_3_20002_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_20002_t meta_reduce_3_20002;

header_type hash_meta_reduce_3_20002_t {
	fields {
		dPort : 16;
		sIP : 32;
		dIP : 32;
		proto : 16;
	}
}

metadata hash_meta_reduce_3_20002_t hash_meta_reduce_3_20002;

field_list reduce_3_20002_fields {
	hash_meta_reduce_3_20002.dPort;
	hash_meta_reduce_3_20002.sIP;
	hash_meta_reduce_3_20002.dIP;
	hash_meta_reduce_3_20002.proto;
}

field_list_calculation reduce_3_20002_fields_hash {
	input {
		reduce_3_20002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_20002{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_20002_regs() {
	add_to_field(meta_reduce_3_20002.val, 1);
	register_write(reduce_3_20002,meta_reduce_3_20002.idx,meta_reduce_3_20002.val);
}

table update_reduce_3_20002_counts {
	actions {update_reduce_3_20002_regs;}
	size : 1;
}

action do_reduce_3_20002_hashes() {
	modify_field(hash_meta_reduce_3_20002.dPort, meta_map_init_20002.dPort);
	modify_field(hash_meta_reduce_3_20002.sIP, meta_map_init_20002.sIP);
	modify_field(hash_meta_reduce_3_20002.dIP, meta_map_init_20002.dIP);
	modify_field(hash_meta_reduce_3_20002.proto, meta_map_init_20002.proto);
	modify_field(meta_reduce_3_20002.qid, 20002);
	modify_field_with_hash_based_offset(meta_reduce_3_20002.idx, 0, reduce_3_20002_fields_hash, 4096);
	register_read(meta_reduce_3_20002.val, reduce_3_20002, meta_reduce_3_20002.idx);
}

table start_reduce_3_20002 {
	actions {do_reduce_3_20002_hashes;}
	size : 1;
}

action set_reduce_3_20002_count() {
	modify_field(meta_reduce_3_20002.val, 1);
}

table set_reduce_3_20002_count {
	actions {set_reduce_3_20002_count;}
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
	modify_field(meta_map_init_10001.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_10001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10001.dPort, tcp.dstPort);
	modify_field(meta_map_init_10001.sPort, tcp.srcPort);
	modify_field(meta_map_init_10001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10001_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
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
	bit_and(meta_map_init_10001.sIP, meta_map_init_10001.sIP, 0xff000000);
}

header_type meta_reduce_3_10001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_10001_t meta_reduce_3_10001;

header_type hash_meta_reduce_3_10001_t {
	fields {
		dMac : 48;
		sIP : 32;
		sMac : 48;
		dPort : 16;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_10001_t hash_meta_reduce_3_10001;

field_list reduce_3_10001_fields {
	hash_meta_reduce_3_10001.dMac;
	hash_meta_reduce_3_10001.sIP;
	hash_meta_reduce_3_10001.sMac;
	hash_meta_reduce_3_10001.dPort;
	hash_meta_reduce_3_10001.sPort;
	hash_meta_reduce_3_10001.dIP;
}

field_list_calculation reduce_3_10001_fields_hash {
	input {
		reduce_3_10001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_10001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_10001_regs() {
	add_to_field(meta_reduce_3_10001.val, 1);
	register_write(reduce_3_10001,meta_reduce_3_10001.idx,meta_reduce_3_10001.val);
}

table update_reduce_3_10001_counts {
	actions {update_reduce_3_10001_regs;}
	size : 1;
}

action do_reduce_3_10001_hashes() {
	modify_field(hash_meta_reduce_3_10001.dMac, meta_map_init_10001.dMac);
	modify_field(hash_meta_reduce_3_10001.sIP, meta_map_init_10001.sIP);
	modify_field(hash_meta_reduce_3_10001.sMac, meta_map_init_10001.sMac);
	modify_field(hash_meta_reduce_3_10001.dPort, meta_map_init_10001.dPort);
	modify_field(hash_meta_reduce_3_10001.sPort, meta_map_init_10001.sPort);
	modify_field(hash_meta_reduce_3_10001.dIP, meta_map_init_10001.dIP);
	modify_field(meta_reduce_3_10001.qid, 10001);
	modify_field_with_hash_based_offset(meta_reduce_3_10001.idx, 0, reduce_3_10001_fields_hash, 4096);
	register_read(meta_reduce_3_10001.val, reduce_3_10001, meta_reduce_3_10001.idx);
}

table start_reduce_3_10001 {
	actions {do_reduce_3_10001_hashes;}
	size : 1;
}

action set_reduce_3_10001_count() {
	modify_field(meta_reduce_3_10001.val, 1);
}

table set_reduce_3_10001_count {
	actions {set_reduce_3_10001_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_20001 : 1;
		qid_10002 : 1;
		qid_20003 : 1;
		qid_20002 : 1;
		qid_10001 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_20001, 1);
	modify_field(meta_fm.qid_10002, 1);
	modify_field(meta_fm.qid_20003, 1);
	modify_field(meta_fm.qid_20002, 1);
	modify_field(meta_fm.qid_10001, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_20001(){
	modify_field(meta_fm.qid_20001, 1);
}

action set_meta_fm_10002(){
	modify_field(meta_fm.qid_10002, 1);
}

action set_meta_fm_20003(){
	modify_field(meta_fm.qid_20003, 1);
}

action set_meta_fm_20002(){
	modify_field(meta_fm.qid_20002, 1);
}

action set_meta_fm_10001(){
	modify_field(meta_fm.qid_10001, 1);
}

action reset_meta_fm_20001(){
	modify_field(meta_fm.qid_20001, 0);
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

action reset_meta_fm_20002(){
	modify_field(meta_fm.qid_20002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10001(){
	modify_field(meta_fm.qid_10001, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_10002_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_10002;
		reset_meta_fm_10002;
	}
}

table filter_20003_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_20003;
		reset_meta_fm_20003;
	}
}

table filter_20002_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_20002;
		reset_meta_fm_20002;
	}
}

table filter_10001_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_10001;
		reset_meta_fm_10001;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_20001 == 1){
					apply(map_init_20001);
			apply(map_20001_1);
			apply(start_reduce_2_20001);
			apply(update_reduce_2_20001_counts);
			if(meta_reduce_2_20001.val > 2) {
				apply(set_reduce_2_20001_count);			}
			else if(meta_reduce_2_20001.val == 2) {
				apply(skip_reduce_2_20001_1);
			}
			else {
				apply(drop_reduce_2_20001_1);
			}

			apply(copy_to_cpu_20001);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_10002== 1){
			apply(filter_10002_1);
		}
		if (meta_fm.qid_10002 == 1){
					apply(map_init_10002);
			apply(map_10002_2);
			apply(copy_to_cpu_10002);
		}
	}
	if (meta_fm.f1 == 2){
		if (meta_fm.qid_20003== 1){
			apply(filter_20003_1);
		}
		if (meta_fm.qid_20003 == 1){
					apply(map_init_20003);
			apply(map_20003_2);
			apply(start_reduce_3_20003);
			apply(update_reduce_3_20003_counts);
			if(meta_reduce_3_20003.val > 2) {
				apply(set_reduce_3_20003_count);			}
			else if(meta_reduce_3_20003.val == 2) {
				apply(skip_reduce_3_20003_1);
			}
			else {
				apply(drop_reduce_3_20003_1);
			}

			apply(copy_to_cpu_20003);
		}
	}
	if (meta_fm.f1 == 3){
		if (meta_fm.qid_20002== 1){
			apply(filter_20002_1);
		}
		if (meta_fm.qid_20002 == 1){
					apply(map_init_20002);
			apply(map_20002_2);
			apply(start_reduce_3_20002);
			apply(update_reduce_3_20002_counts);
			if(meta_reduce_3_20002.val > 2) {
				apply(set_reduce_3_20002_count);			}
			else if(meta_reduce_3_20002.val == 2) {
				apply(skip_reduce_3_20002_1);
			}
			else {
				apply(drop_reduce_3_20002_1);
			}

			apply(copy_to_cpu_20002);
		}
	}
	if (meta_fm.f1 == 4){
		if (meta_fm.qid_10001== 1){
			apply(filter_10001_1);
		}
		if (meta_fm.qid_10001 == 1){
					apply(map_init_10001);
			apply(map_10001_2);
			apply(start_reduce_3_10001);
			apply(update_reduce_3_10001_counts);
			if(meta_reduce_3_10001.val > 2) {
				apply(set_reduce_3_10001_count);			}
			else if(meta_reduce_3_10001.val == 2) {
				apply(skip_reduce_3_10001_1);
			}
			else {
				apply(drop_reduce_3_10001_1);
			}

			apply(copy_to_cpu_10001);
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
				apply(encap_20001);
			}
			if (meta_fm.f1 == 1){
				apply(encap_10002);
			}
			if (meta_fm.f1 == 2){
				apply(encap_20003);
			}
			if (meta_fm.f1 == 3){
				apply(encap_20002);
			}
			if (meta_fm.f1 == 4){
				apply(encap_10001);
			}
		}


	}
}

