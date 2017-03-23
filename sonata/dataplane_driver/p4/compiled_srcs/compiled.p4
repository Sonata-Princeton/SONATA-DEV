#include "includes/headers.p4"
#include "includes/parser.p4"

parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}

parser parse_out_header {
	extract(out_header_10016);
	extract(out_header_10032);
	return parse_final_header;
}

parser parse_final_header {
	extract(<p4.p4_elements.Header object at 0x7fe00cc1b490>);
	return parse_ethernet;
}

header_type final_header_t {
	fields {
		delimiter: 32;
	}
}

header final_header_t final_header;

header_type meta_app_data_t {
	fields {
		drop_10016: 1;
		satisfied_10016: 1;
		drop_10032: 1;
		satisfied_10032: 1;
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;

action _nop(){
	no_op();
}

field_list report_packet_fields {
	meta_app_data;
	meta_MapInit;
	meta_MapInit;
}

action do_report_packet(){
	clone_ingress_pkt_to_egress(8001, report_packet_fields);
}

table report_packet {
	actions {
		do_report_packet;
	}
	size : 1;
}

// query 10016
header_type out_header_10016_t {
	fields {
		qid: 16;
		dIP: 32;
	}
}

header out_header_10016_t out_header_10016;

action drop_10016(){
	modify_field(meta_app_data.drop_10016, 1);
}

action do_mark_satisfied_10016(){
	modify_field(meta_app_data.satisfied_10016, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_10016(){
	add_header(out_header_10016);
	modify_field(out_header_10016.qid, meta_MapInit.qid);
	modify_field(out_header_10016.dIP, meta_MapInit.dIP);
}

table add_out_header_10016 {
	actions {
		do_add_out_header_10016;
	}
	size : 1;
}

table mark_satisfied_10016 {
	actions {
		do_mark_satisfied_10016;
	}
	size : 1;
}

// MapInit of query 10016
header_type meta_MapInit_t {
	fields {
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

metadata meta_MapInit_t meta_MapInit;

action do_MapInit(){
	modify_field(meta_MapInit.dMac, ethernet.dstAddr);
	modify_field(meta_MapInit.sIP, ipv4.srcAddr);
	modify_field(meta_MapInit.proto, ipv4.protocol);
	modify_field(meta_MapInit.sMac, ethernet.srcAddr);
	modify_field(meta_MapInit.nBytes, ipv4.totalLen);
	modify_field(meta_MapInit.dPort, tcp.dstPort);
	modify_field(meta_MapInit.sPort, tcp.srcPort);
	modify_field(meta_MapInit.dIP, ipv4.dstAddr);
}

table mapinit_10016_1 {
	actions {
		do_MapInit;
	}
	size : 1;
}


// Map 2 of query 10016
action do_map_10016_2(){
	bit_and(meta_MapInit.dIP, meta_MapInit.dIP, 0xffffffffffffffff0000000000000000);
}

table map_10016_2 {
	actions {
		do_map_10016_2;
	}
	size : 1;
}


// Distinct 4 of query 10016
header_type meta_distinct_10016_4_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_10016_4_t meta_distinct_10016_4;

field_list hash_distinct_10016_4_fields {
	meta_MapInit.dIP;
	meta_MapInit.sIP;
}

field_list_calculation hash_distinct_10016_4 {
	input {
		hash_distinct_10016_4_fields_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

action do_init_distinct_10016_4(){
	modify_field_with_hash_based_offset(meta_distinct_10016_4.index, 0, hash_distinct_10016_4, 4096);
	register_read(meta_distinct_10016_4.value, distinct_10016_4, meta_distinct_10016_4.index);
	modify_field(meta_distinct_10016_4.value, meta_distinct_10016_4.value & 1);
	register_write(distinct_10016_4, meta_distinct_10016_4.index, meta_distinct_10016_4.value);
}

table init_distinct_10016_4 {
	actions {
		do_init_distinct_10016_4;
	}
	size : 1;
}

table pass_distinct_10016_4 {
	actions {
		_nop;
	}
	size : 1;
}

table drop_distinct_10016_4 {
	actions {
		drop_10016;
	}
	size : 1;
}


// Map 5 of query 10016
action do_map_10016_5(){
}

table map_10016_5 {
	actions {
		do_map_10016_5;
	}
	size : 1;
}


// Reduce 6 of query 10016
header_type meta_reduce_10016_6_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_reduce_10016_6_t meta_reduce_10016_6;

field_list hash_reduce_10016_6_fields {
	meta_MapInit.dIP;
}

field_list_calculation hash_reduce_10016_6 {
	input {
		hash_reduce_10016_6_fields_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

action do_init_reduce_10016_6(){
	modify_field_with_hash_based_offset(meta_reduce_10016_6.index, 0, hash_reduce_10016_6, 4096);
	register_read(meta_reduce_10016_6.value, reduce_10016_6, meta_reduce_10016_6.index);
	modify_field(meta_reduce_10016_6.value, meta_reduce_10016_6.value + 1);
	register_write(reduce_10016_6, meta_reduce_10016_6.index, meta_reduce_10016_6.value);
}

action set_count_reduce_10016_6(){
	modify_field(meta_MapInit.count, meta_reduce_10016_6.value);
}

action reset_count_reduce_10016_6(){
	modify_field(meta_MapInit.count, 1);
}

table init_reduce_10016_6 {
	actions {
		do_init_reduce_10016_6;
	}
	size : 1;
}

table first_pass_reduce_10016_6 {
	actions {
		set_count_reduce_10016_6;
	}
	size : 1;
}

table pass_reduce_10016_6 {
	actions {
		reset_count_reduce_10016_6;
	}
	size : 1;
}

table drop_reduce_10016_6 {
	actions {
		drop_10016;
	}
	size : 1;
}


// Filter 7 of query 10016
table filter_10016_7 {
	actions {
		drop_10016;
		_nop;
	}
	size : 64;
}


// query 10032
header_type out_header_10032_t {
	fields {
		qid: 16;
		dIP: 32;
		sIP: 32;
	}
}

header out_header_10032_t out_header_10032;

action drop_10032(){
	modify_field(meta_app_data.drop_10032, 1);
}

action do_mark_satisfied_10032(){
	modify_field(meta_app_data.satisfied_10032, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_10032(){
	add_header(out_header_10032);
	modify_field(out_header_10032.qid, meta_MapInit.qid);
	modify_field(out_header_10032.dIP, meta_MapInit.dIP);
	modify_field(out_header_10032.sIP, meta_MapInit.sIP);
}

table add_out_header_10032 {
	actions {
		do_add_out_header_10032;
	}
	size : 1;
}

table mark_satisfied_10032 {
	actions {
		do_mark_satisfied_10032;
	}
	size : 1;
}

// MapInit of query 10032
header_type meta_MapInit_t {
	fields {
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

metadata meta_MapInit_t meta_MapInit;

action do_MapInit(){
	modify_field(meta_MapInit.dMac, ethernet.dstAddr);
	modify_field(meta_MapInit.sIP, ipv4.srcAddr);
	modify_field(meta_MapInit.proto, ipv4.protocol);
	modify_field(meta_MapInit.sMac, ethernet.srcAddr);
	modify_field(meta_MapInit.nBytes, ipv4.totalLen);
	modify_field(meta_MapInit.dPort, tcp.dstPort);
	modify_field(meta_MapInit.sPort, tcp.srcPort);
	modify_field(meta_MapInit.dIP, ipv4.dstAddr);
}

table mapinit_10032_1 {
	actions {
		do_MapInit;
	}
	size : 1;
}


// Map 2 of query 10032
action do_map_10032_2(){
	bit_and(meta_MapInit.dIP, meta_MapInit.dIP, 0xffffffffffffffffffffffffffffffff);
}

table map_10032_2 {
	actions {
		do_map_10032_2;
	}
	size : 1;
}


// Distinct 4 of query 10032
header_type meta_distinct_10032_4_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_10032_4_t meta_distinct_10032_4;

field_list hash_distinct_10032_4_fields {
	meta_MapInit.dIP;
	meta_MapInit.sIP;
}

field_list_calculation hash_distinct_10032_4 {
	input {
		hash_distinct_10032_4_fields_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

action do_init_distinct_10032_4(){
	modify_field_with_hash_based_offset(meta_distinct_10032_4.index, 0, hash_distinct_10032_4, 4096);
	register_read(meta_distinct_10032_4.value, distinct_10032_4, meta_distinct_10032_4.index);
	modify_field(meta_distinct_10032_4.value, meta_distinct_10032_4.value & 1);
	register_write(distinct_10032_4, meta_distinct_10032_4.index, meta_distinct_10032_4.value);
}

table init_distinct_10032_4 {
	actions {
		do_init_distinct_10032_4;
	}
	size : 1;
}

table pass_distinct_10032_4 {
	actions {
		_nop;
	}
	size : 1;
}

table drop_distinct_10032_4 {
	actions {
		drop_10032;
	}
	size : 1;
}


control ingress {
	apply(init_meta_fm);
		// query 10016
		if (meta_app_data.drop_10016 != 1) {
			apply(mapinit_10016_1);
			if (meta_app_data.drop_10016 != 1) {
				apply(map_10016_2);
				if (meta_app_data.drop_10016 != 1) {
					apply(init_distinct_10016_4);
					if (meta_distinct_10016_4.value <= 1) {
						apply(pass_distinct_10016_4);
					}
					else {
						apply(drop_distinct_10016_4);
					}
					if (meta_app_data.drop_10016 != 1) {
						apply(map_10016_5);
						if (meta_app_data.drop_10016 != 1) {
							apply(init_reduce_10016_6);
							if (meta_reduce_10016_6.value == 2) {
								apply(first_pass_reduce_10016_6);
							}
							elif (meta_reduce_10016_6.value > 2) {
								apply(pass_reduce_10016_6);
							}
							else {
								apply(drop_reduce_10016_6);
							}
							if (meta_app_data.drop_10016 != 1) {
								apply(filter_10016_7);
								if (meta_app_data.drop_10016 != 1) {
									apply(mark_satisfied_10016);
								}
							}
						}
					}
				}
			}
		}
		// query 10032
		if (meta_app_data.drop_10032 != 1) {
			apply(mapinit_10032_1);
			if (meta_app_data.drop_10032 != 1) {
				apply(map_10032_2);
				if (meta_app_data.drop_10032 != 1) {
					apply(init_distinct_10032_4);
					if (meta_distinct_10032_4.value <= 1) {
						apply(pass_distinct_10032_4);
					}
					else {
						apply(drop_distinct_10032_4);
					}
					if (meta_app_data.drop_10032 != 1) {
						apply(mark_satisfied_10032);
					}
				}
			}
		}

	if (meta_app_data.clone == 1) {
		apply(report_packet)
	}
}

control egress {
	if (standard_metadata.instance_type == 0) {
		// original packet, apply forwarding	}

	else if (standard_metadata.instance_type == 1) {
		if (meta_app_data.satisfied_10016 == 1) {
			apply(add_out_header_10016);
		}
		if (meta_app_data.satisfied_10032 == 1) {
			apply(add_out_header_10032);
		}
	}
	apply(add_final_header);
}

