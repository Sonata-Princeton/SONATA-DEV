#include "includes/headers.p4"
#include "includes/parser.p4"

parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}

parser parse_out_header {
	extract(out_header_30016);
	extract(out_header_30032);
	return parse_final_header;
}

parser parse_final_header {
	extract(final_header);
	return parse_ethernet;
}

action do_init_app_metadata(){
	modify_field(meta_app_data.drop_30016, 0);
	modify_field(meta_app_data.satisfied_30016, 0);
	modify_field(meta_app_data.drop_30032, 0);
	modify_field(meta_app_data.satisfied_30032, 0);
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
		drop_30016: 1;
		satisfied_30016: 1;
		drop_30032: 1;
		satisfied_30032: 1;
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;

action _nop(){
	no_op();
}

field_list report_packet_fields {
	meta_app_data;
	meta_mapinit_30016_1;
	meta_mapinit_30032_1;
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

// query 30016
header_type out_header_30016_t {
	fields {
		qid: 16;
		sIP: 32;
	}
}

header out_header_30016_t out_header_30016;

action drop_30016(){
	modify_field(meta_app_data.drop_30016, 1);
}

action do_mark_satisfied_30016(){
	modify_field(meta_app_data.satisfied_30016, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_30016(){
	add_header(out_header_30016);
	modify_field(out_header_30016.qid, meta_mapinit_30016_1.qid);
	modify_field(out_header_30016.sIP, meta_mapinit_30016_1.sIP);
}

table add_out_header_30016 {
	actions {
		do_add_out_header_30016;
	}
	size : 1;
}

table mark_satisfied_30016 {
	actions {
		do_mark_satisfied_30016;
	}
	size : 1;
}

// MapInit of query 30016
header_type meta_mapinit_30016_1_t {
	fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
	}
}

metadata meta_mapinit_30016_1_t meta_mapinit_30016_1;

action do_mapinit_30016_1(){
	modify_field(meta_mapinit_30016_1.qid, 30016);
	modify_field(meta_mapinit_30016_1.sIP, ipv4.srcAddr);
	modify_field(meta_mapinit_30016_1.dIP, ipv4.dstAddr);
}

table mapinit_30016_1 {
	actions {
		do_mapinit_30016_1;
	}
	size : 1;
}


// Map 2 of query 30016
action do_map_30016_2(){
	bit_and(meta_mapinit_30016_1.sIP, meta_mapinit_30016_1.sIP, 0xffff0000);
}

table map_30016_2 {
	actions {
		do_map_30016_2;
	}
	size : 1;
}


// Map 3 of query 30016
action do_map_30016_3(){
}

table map_30016_3 {
	actions {
		do_map_30016_3;
	}
	size : 1;
}


// Distinct 4 of query 30016
header_type meta_distinct_30016_4_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_30016_4_t meta_distinct_30016_4;

field_list hash_distinct_30016_4_fields {
	meta_mapinit_30016_1.dIP;
	meta_mapinit_30016_1.sIP;
}

field_list_calculation hash_distinct_30016_4 {
	input {
		hash_distinct_30016_4_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

register distinct_30016_4 {
	width: 32;
	instance_count: 4096;
}

action do_init_distinct_30016_4(){
	modify_field_with_hash_based_offset(meta_distinct_30016_4.index, 0, hash_distinct_30016_4, 4096);
	register_read(meta_distinct_30016_4.value, distinct_30016_4, meta_distinct_30016_4.index);
	bit_or(meta_distinct_30016_4.value, meta_distinct_30016_4.value, 1);
	register_write(distinct_30016_4, meta_distinct_30016_4.index, meta_distinct_30016_4.value);
}

table init_distinct_30016_4 {
	actions {
		do_init_distinct_30016_4;
	}
	size : 1;
}

table pass_distinct_30016_4 {
	actions {
		_nop;
	}
	size : 1;
}

table drop_distinct_30016_4 {
	actions {
		drop_30016;
	}
	size : 1;
}


// Map 5 of query 30016
action do_map_30016_5(){
}

table map_30016_5 {
	actions {
		do_map_30016_5;
	}
	size : 1;
}


// query 30032
header_type out_header_30032_t {
	fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
	}
}

header out_header_30032_t out_header_30032;

action drop_30032(){
	modify_field(meta_app_data.drop_30032, 1);
}

action do_mark_satisfied_30032(){
	modify_field(meta_app_data.satisfied_30032, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_30032(){
	add_header(out_header_30032);
	modify_field(out_header_30032.qid, meta_mapinit_30032_1.qid);
	modify_field(out_header_30032.sIP, meta_mapinit_30032_1.sIP);
	modify_field(out_header_30032.dIP, meta_mapinit_30032_1.dIP);
}

table add_out_header_30032 {
	actions {
		do_add_out_header_30032;
	}
	size : 1;
}

table mark_satisfied_30032 {
	actions {
		do_mark_satisfied_30032;
	}
	size : 1;
}

// MapInit of query 30032
header_type meta_mapinit_30032_1_t {
	fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
	}
}

metadata meta_mapinit_30032_1_t meta_mapinit_30032_1;

action do_mapinit_30032_1(){
	modify_field(meta_mapinit_30032_1.qid, 30032);
	modify_field(meta_mapinit_30032_1.sIP, ipv4.srcAddr);
	modify_field(meta_mapinit_30032_1.dIP, ipv4.dstAddr);
}

table mapinit_30032_1 {
	actions {
		do_mapinit_30032_1;
	}
	size : 1;
}


// Filter 2 of query 30032
table filter_30032_2 {
	reads {
		ipv4.srcAddr: lpm;
	}
	actions {
		drop_30032;
		_nop;
	}
	size : 64;
}


// Map 3 of query 30032
action do_map_30032_3(){
	bit_and(meta_mapinit_30032_1.sIP, meta_mapinit_30032_1.sIP, 0xffffffff);
}

table map_30032_3 {
	actions {
		do_map_30032_3;
	}
	size : 1;
}


control ingress {
	apply(init_app_metadata);
		// query 30016
		if (meta_app_data.drop_30016 != 1) {
			apply(mapinit_30016_1);
			if (meta_app_data.drop_30016 != 1) {
				apply(map_30016_2);
				if (meta_app_data.drop_30016 != 1) {
					apply(map_30016_3);
					if (meta_app_data.drop_30016 != 1) {
						apply(init_distinct_30016_4);
						if (meta_distinct_30016_4.value <= 1) {
							apply(pass_distinct_30016_4);
						}
						else {
							apply(drop_distinct_30016_4);
						}
						if (meta_app_data.drop_30016 != 1) {
							apply(map_30016_5);
							if (meta_app_data.drop_30016 != 1) {
								apply(mark_satisfied_30016);
							}
						}
					}
				}
			}
		}
		// query 30032
		if (meta_app_data.drop_30032 != 1) {
			apply(mapinit_30032_1);
			if (meta_app_data.drop_30032 != 1) {
				apply(filter_30032_2);
				if (meta_app_data.drop_30032 != 1) {
					apply(map_30032_3);
					if (meta_app_data.drop_30032 != 1) {
						apply(mark_satisfied_30032);
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
		if (meta_app_data.satisfied_30016 == 1) {
			apply(add_out_header_30016);
		}
		if (meta_app_data.satisfied_30032 == 1) {
			apply(add_out_header_30032);
		}
		apply(add_final_header);
	}
}

