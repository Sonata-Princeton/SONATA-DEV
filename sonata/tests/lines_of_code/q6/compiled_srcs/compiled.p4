#include "includes/headers.p4"
#include "includes/parser.p4"

parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}

parser parse_out_header {
	extract(out_header_60016);
	extract(out_header_60032);
	return parse_final_header;
}

parser parse_final_header {
	extract(final_header);
	return parse_ethernet;
}

action do_init_app_metadata(){
	modify_field(meta_app_data.drop_60016, 0);
	modify_field(meta_app_data.satisfied_60016, 0);
	modify_field(meta_app_data.drop_60032, 0);
	modify_field(meta_app_data.satisfied_60032, 0);
	modify_field(meta_app_data.clone, 0);
}

table init_app_metadata {
	actions {
		do_init_app_metadata;
	}
	size : 1;
}

header_type meta_app_data_t {
	fields {
		drop_60016: 1;
		satisfied_60016: 1;
		drop_60032: 1;
		satisfied_60032: 1;
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;

action _nop(){
	no_op();
}

field_list report_packet_fields {
	meta_app_data;
	meta_mapinit_60016_1;
	meta_mapinit_60032_1;
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

header_type final_header_t {
	fields {
		delimiter: 32;
	}
}

header final_header_t final_header;

action do_add_final_header(){
	add_header(final_header);
	modify_field(final_header.delimiter, 0);
}

table add_final_header {
	actions {
		do_add_final_header;
	}
	size : 1;
}

// query 60016
header_type out_header_60016_t {
	fields {
		qid: 16;
		sIP: 32;
	}
}

header out_header_60016_t out_header_60016;

action drop_60016(){
	modify_field(meta_app_data.drop_60016, 1);
}

action do_mark_satisfied_60016(){
	modify_field(meta_app_data.satisfied_60016, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_60016(){
	add_header(out_header_60016);
	modify_field(out_header_60016.qid, meta_mapinit_60016_1.qid);
	modify_field(out_header_60016.sIP, meta_mapinit_60016_1.sIP);
}

table add_out_header_60016 {
	actions {
		do_add_out_header_60016;
	}
	size : 1;
}

table mark_satisfied_60016 {
	actions {
		do_mark_satisfied_60016;
	}
	size : 1;
}

// MapInit of query 60016
header_type meta_mapinit_60016_1_t {
	fields {
		dPort: 16;
		qid: 16;
		sIP: 32;
	}
}

metadata meta_mapinit_60016_1_t meta_mapinit_60016_1;

action do_mapinit_60016_1(){
	modify_field(meta_mapinit_60016_1.dPort, tcp.dstPort);
	modify_field(meta_mapinit_60016_1.qid, 60016);
	modify_field(meta_mapinit_60016_1.sIP, ipv4.srcAddr);
}

table mapinit_60016_1 {
	actions {
		do_mapinit_60016_1;
	}
	size : 1;
}


// Map 2 of query 60016
action do_map_60016_2(){
	bit_and(meta_mapinit_60016_1.sIP, meta_mapinit_60016_1.sIP, 0xffff0000);
}

table map_60016_2 {
	actions {
		do_map_60016_2;
	}
	size : 1;
}


// Map 3 of query 60016
action do_map_60016_3(){
}

table map_60016_3 {
	actions {
		do_map_60016_3;
	}
	size : 1;
}


// Distinct 4 of query 60016
header_type meta_distinct_60016_4_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_60016_4_t meta_distinct_60016_4;

field_list hash_distinct_60016_4_fields {
	meta_mapinit_60016_1.sIP;
	meta_mapinit_60016_1.dPort;
}

field_list_calculation hash_distinct_60016_4 {
	input {
		hash_distinct_60016_4_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

register distinct_60016_4 {
	width: 32;
	instance_count: 4096;
}

action do_init_distinct_60016_4(){
	modify_field_with_hash_based_offset(meta_distinct_60016_4.index, 0, hash_distinct_60016_4, 4096);
	register_read(meta_distinct_60016_4.value, distinct_60016_4, meta_distinct_60016_4.index);
	bit_or(meta_distinct_60016_4.value, meta_distinct_60016_4.value, 1);
	register_write(distinct_60016_4, meta_distinct_60016_4.index, meta_distinct_60016_4.value);
}

table init_distinct_60016_4 {
	actions {
		do_init_distinct_60016_4;
	}
	size : 1;
}

table pass_distinct_60016_4 {
	actions {
		_nop;
	}
	size : 1;
}

table drop_distinct_60016_4 {
	actions {
		drop_60016;
	}
	size : 1;
}


// Map 5 of query 60016
action do_map_60016_5(){
}

table map_60016_5 {
	actions {
		do_map_60016_5;
	}
	size : 1;
}


// query 60032
header_type out_header_60032_t {
	fields {
		qid: 16;
		dPort: 16;
		sIP: 32;
	}
}

header out_header_60032_t out_header_60032;

action drop_60032(){
	modify_field(meta_app_data.drop_60032, 1);
}

action do_mark_satisfied_60032(){
	modify_field(meta_app_data.satisfied_60032, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_60032(){
	add_header(out_header_60032);
	modify_field(out_header_60032.qid, meta_mapinit_60032_1.qid);
	modify_field(out_header_60032.dPort, meta_mapinit_60032_1.dPort);
	modify_field(out_header_60032.sIP, meta_mapinit_60032_1.sIP);
}

table add_out_header_60032 {
	actions {
		do_add_out_header_60032;
	}
	size : 1;
}

table mark_satisfied_60032 {
	actions {
		do_mark_satisfied_60032;
	}
	size : 1;
}

// MapInit of query 60032
header_type meta_mapinit_60032_1_t {
	fields {
		dPort: 16;
		qid: 16;
		sIP: 32;
	}
}

metadata meta_mapinit_60032_1_t meta_mapinit_60032_1;

action do_mapinit_60032_1(){
	modify_field(meta_mapinit_60032_1.dPort, tcp.dstPort);
	modify_field(meta_mapinit_60032_1.qid, 60032);
	modify_field(meta_mapinit_60032_1.sIP, ipv4.srcAddr);
}

table mapinit_60032_1 {
	actions {
		do_mapinit_60032_1;
	}
	size : 1;
}


// Filter 2 of query 60032
table filter_60032_2 {
	reads {
		ipv4.srcAddr: lpm;
	}
	actions {
		drop_60032;
		_nop;
	}
	size : 64;
}


// Map 3 of query 60032
action do_map_60032_3(){
	bit_and(meta_mapinit_60032_1.sIP, meta_mapinit_60032_1.sIP, 0xffffffff);
}

table map_60032_3 {
	actions {
		do_map_60032_3;
	}
	size : 1;
}


control ingress {
	apply(init_app_metadata);
		// query 60016
		if (meta_app_data.drop_60016 != 1) {
			apply(mapinit_60016_1);
			if (meta_app_data.drop_60016 != 1) {
				apply(map_60016_2);
				if (meta_app_data.drop_60016 != 1) {
					apply(map_60016_3);
					if (meta_app_data.drop_60016 != 1) {
						apply(init_distinct_60016_4);
						if (meta_distinct_60016_4.value <= 1) {
							apply(pass_distinct_60016_4);
						}
						else {
							apply(drop_distinct_60016_4);
						}
						if (meta_app_data.drop_60016 != 1) {
							apply(map_60016_5);
							if (meta_app_data.drop_60016 != 1) {
								apply(mark_satisfied_60016);
							}
						}
					}
				}
			}
		}
		// query 60032
		if (meta_app_data.drop_60032 != 1) {
			apply(mapinit_60032_1);
			if (meta_app_data.drop_60032 != 1) {
				apply(filter_60032_2);
				if (meta_app_data.drop_60032 != 1) {
					apply(map_60032_3);
					if (meta_app_data.drop_60032 != 1) {
						apply(mark_satisfied_60032);
					}
				}
			}
		}

	if (meta_app_data.clone == 1) {
		apply(report_packet);
	}
}

control egress {
	if (standard_metadata.instance_type == 0) {
		// original packet, apply forwarding
	}

	else if (standard_metadata.instance_type == 1) {
		if (meta_app_data.satisfied_60016 == 1) {
			apply(add_out_header_60016);
		}
		if (meta_app_data.satisfied_60032 == 1) {
			apply(add_out_header_60032);
		}
		apply(add_final_header);
	}
}

