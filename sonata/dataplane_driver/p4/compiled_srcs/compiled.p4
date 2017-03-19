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
	extract(out_header_10016);
	extract(out_header_10032);
	return parse_ethernet;
}

header_type out_header_10016_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_10016_t out_header_10016;

field_list copy_to_cpu_fields_10016{
	standard_metadata;
	hash_meta_reduce_3_10016;
	meta_reduce_3_10016;
	meta_map_init_10016;
	meta_fm;
}

action do_copy_to_cpu_10016() {
	clone_ingress_pkt_to_egress(10216, copy_to_cpu_fields_10016);
}

table copy_to_cpu_10016 {
	actions {do_copy_to_cpu_10016;}
	size : 1;
}

table encap_10016 {
	actions { do_encap_10016; }
	size : 1;
}

action do_encap_10016() {
	add_header(out_header_10016);
	modify_field(out_header_10016.qid, meta_reduce_3_10016.qid);
	modify_field(out_header_10016.dIP, meta_map_init_10016.dIP);
	modify_field(out_header_10016.count, meta_reduce_3_10016.val);
}

header_type out_header_10032_t {
	fields {
		qid : 16;
		sIP : 32;
		sPort : 16;
		dIP : 32;
		dPort : 16;
		nBytes : 16;
		proto : 16;
		sMac : 48;
		dMac : 48;}
}

header out_header_10032_t out_header_10032;

field_list copy_to_cpu_fields_10032{
	standard_metadata;
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
	modify_field(out_header_10032.qid, meta_map_init_10032.qid);
	modify_field(out_header_10032.sIP, meta_map_init_10032.sIP);
	modify_field(out_header_10032.sPort, meta_map_init_10032.sPort);
	modify_field(out_header_10032.dIP, meta_map_init_10032.dIP);
	modify_field(out_header_10032.dPort, meta_map_init_10032.dPort);
	modify_field(out_header_10032.nBytes, meta_map_init_10032.nBytes);
	modify_field(out_header_10032.proto, meta_map_init_10032.proto);
	modify_field(out_header_10032.sMac, meta_map_init_10032.sMac);
	modify_field(out_header_10032.dMac, meta_map_init_10032.dMac);
}

table drop_distinct_2_10016_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_10016_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_10016_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_10016_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_10016_1 {
	actions {mark_drop;}
	size : 1;
}

table map_init_10016{
	actions{
		do_map_init_10016;
	}
}

action do_map_init_10016(){
	modify_field(meta_map_init_10016.qid, 10016);
	modify_field(meta_map_init_10016.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_10016.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10016.proto, ipv4.protocol);
	modify_field(meta_map_init_10016.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_10016.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_10016.dPort, tcp.dstPort);
	modify_field(meta_map_init_10016.sPort, tcp.srcPort);
	modify_field(meta_map_init_10016.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10016_t {
	 fields {
		qid: 16;
		dMac: 48;
		sIP: 32;
		proto: 16;
		sMac: 48;
		nBytes: 16;
		dPort: 16;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_10016_t meta_map_init_10016;

table map_10016_1{
	actions{
		do_map_10016_1;
	}
}

action do_map_10016_1() {
	bit_and(meta_map_init_10016.dIP, meta_map_init_10016.dIP, 0xffff0000);
}

header_type meta_distinct_2_10016_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_10016_t meta_distinct_2_10016;

header_type hash_meta_distinct_2_10016_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_10016_t hash_meta_distinct_2_10016;

field_list distinct_2_10016_fields {
	hash_meta_distinct_2_10016.sIP;
	hash_meta_distinct_2_10016.dIP;
}

field_list_calculation distinct_2_10016_fields_hash {
	input {
		distinct_2_10016_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_10016{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_10016_regs() {
	bit_or(meta_distinct_2_10016.val,meta_distinct_2_10016.val, 1);
	register_write(distinct_2_10016,meta_distinct_2_10016.idx,meta_distinct_2_10016.val);
}

table update_distinct_2_10016_counts {
	actions {update_distinct_2_10016_regs;}
	size : 1;
}

action do_distinct_2_10016_hashes() {
	modify_field(hash_meta_distinct_2_10016.sIP, meta_map_init_10016.sIP);
	modify_field(hash_meta_distinct_2_10016.dIP, meta_map_init_10016.dIP);
	modify_field(meta_distinct_2_10016.qid, 10016);
	modify_field_with_hash_based_offset(meta_distinct_2_10016.idx, 0, distinct_2_10016_fields_hash, 4096);
	register_read(meta_distinct_2_10016.val, distinct_2_10016, meta_distinct_2_10016.idx);
}

table start_distinct_2_10016 {
	actions {do_distinct_2_10016_hashes;}
	size : 1;
}

action set_distinct_2_10016_count() {
	modify_field(meta_distinct_2_10016.val, 1);
}

table set_distinct_2_10016_count {
	actions {set_distinct_2_10016_count;}
        size: 1;
}

header_type meta_reduce_3_10016_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_10016_t meta_reduce_3_10016;

header_type hash_meta_reduce_3_10016_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_10016_t hash_meta_reduce_3_10016;

field_list reduce_3_10016_fields {
	hash_meta_reduce_3_10016.dIP;
}

field_list_calculation reduce_3_10016_fields_hash {
	input {
		reduce_3_10016_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_10016{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_10016_regs() {
	add_to_field(meta_reduce_3_10016.val, 1);
	register_write(reduce_3_10016,meta_reduce_3_10016.idx,meta_reduce_3_10016.val);
}

table update_reduce_3_10016_counts {
	actions {update_reduce_3_10016_regs;}
	size : 1;
}

action do_reduce_3_10016_hashes() {
	modify_field(hash_meta_reduce_3_10016.dIP, meta_map_init_10016.dIP);
	modify_field(meta_reduce_3_10016.qid, 10016);
	modify_field_with_hash_based_offset(meta_reduce_3_10016.idx, 0, reduce_3_10016_fields_hash, 4096);
	register_read(meta_reduce_3_10016.val, reduce_3_10016, meta_reduce_3_10016.idx);
}

table start_reduce_3_10016 {
	actions {do_reduce_3_10016_hashes;}
	size : 1;
}

action set_reduce_3_10016_count() {
	modify_field(meta_reduce_3_10016.val, 1);
}

table set_reduce_3_10016_count {
	actions {set_reduce_3_10016_count;}
        size: 1;
}

table map_init_10032{
	actions{
		do_map_init_10032;
	}
}

action do_map_init_10032(){
	modify_field(meta_map_init_10032.qid, 10032);
	modify_field(meta_map_init_10032.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_10032.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10032.proto, ipv4.protocol);
	modify_field(meta_map_init_10032.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_10032.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_10032.dPort, tcp.dstPort);
	modify_field(meta_map_init_10032.sPort, tcp.srcPort);
	modify_field(meta_map_init_10032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_10032_t {
	 fields {
		qid: 16;
		dMac: 48;
		sIP: 32;
		proto: 16;
		sMac: 48;
		nBytes: 16;
		dPort: 16;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_10032_t meta_map_init_10032;

table map_10032_1{
	actions{
		do_map_10032_1;
	}
}

action do_map_10032_1() {
	bit_and(meta_map_init_10032.dIP, meta_map_init_10032.dIP, 0xffffffff);
}

header_type meta_fm_t {
	fields {
		qid_10016 : 1;
		qid_10032 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_10016, 1);
	modify_field(meta_fm.qid_10032, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_10016(){
	modify_field(meta_fm.qid_10016, 1);
}

action set_meta_fm_10032(){
	modify_field(meta_fm.qid_10032, 1);
}

action reset_meta_fm_10016(){
	modify_field(meta_fm.qid_10016, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10032(){
	modify_field(meta_fm.qid_10032, 0);
	modify_field(meta_fm.is_drop, 1);
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_10016 == 1){
					apply(map_init_10016);
			apply(map_10016_1);
			apply(start_distinct_2_10016);
			apply(start_reduce_3_10016);
			if(meta_distinct_2_10016.val > 0) {
				apply(drop_distinct_2_10016_1);
			}
			else if(meta_distinct_2_10016.val == 0) {
				apply(skip_distinct_2_10016_1);
			}
			else {
				apply(drop_distinct_2_10016_2);
			}

			apply(update_distinct_2_10016_counts);
			apply(update_reduce_3_10016_counts);
			if(meta_reduce_3_10016.val > 2) {
				apply(set_reduce_3_10016_count);			}
			else if(meta_reduce_3_10016.val == 2) {
				apply(skip_reduce_3_10016_1);
			}
			else {
				apply(drop_reduce_3_10016_1);
			}

			apply(copy_to_cpu_10016);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_10032 == 1){
					apply(map_init_10032);
			apply(map_10032_1);
			apply(copy_to_cpu_10032);
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
				apply(encap_10016);
			}
			if (meta_fm.f1 == 1){
				apply(encap_10032);
			}
		}


	}
}

