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
	extract(final_header);
	return parse_ethernet;
}

action do_init_app_metadata(){
	modify_field(meta_app_data.drop_10016, 0);
	modify_field(meta_app_data.satisfied_10016, 0);
	modify_field(meta_app_data.drop_10032, 0);
	modify_field(meta_app_data.satisfied_10032, 0);
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
	meta_mapinit_10016_1;
	meta_mapinit_10032_1;
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
	modify_field(out_header_10016.qid, meta_mapinit_10016_1.qid);
	modify_field(out_header_10016.dIP, meta_mapinit_10016_1.dIP);
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
header_type meta_mapinit_10016_1_t {
	fields {
		dMac: 48;
		sIP: 32;
		proto: 16;
		qid: 16;
		sMac: 48;
		nBytes: 16;
		dPort: 16;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_mapinit_10016_1_t meta_mapinit_10016_1;

action do_mapinit_10016_1(){
	modify_field(meta_mapinit_10016_1.dMac, ethernet.dstAddr);
	modify_field(meta_mapinit_10016_1.sIP, ipv4.srcAddr);
	modify_field(meta_mapinit_10016_1.proto, ipv4.protocol);
	modify_field(meta_mapinit_10016_1.qid, 10016);
	modify_field(meta_mapinit_10016_1.sMac, ethernet.srcAddr);
	modify_field(meta_mapinit_10016_1.nBytes, ipv4.totalLen);
	modify_field(meta_mapinit_10016_1.dPort, tcp.dstPort);
	modify_field(meta_mapinit_10016_1.sPort, tcp.srcPort);
	modify_field(meta_mapinit_10016_1.dIP, ipv4.dstAddr);
}

table mapinit_10016_1 {
	actions {
		do_mapinit_10016_1;
	}
	size : 1;
}


// Map 2 of query 10016
action do_map_10016_2(){
	bit_and(meta_mapinit_10016_1.dIP, meta_mapinit_10016_1.dIP, 0xffff0000);
}

table map_10016_2 {
	actions {
		do_map_10016_2;
	}
	size : 1;
}


// Filter 3 of query 10016
table filter_10016_3 {
	reads {
		ipv4.protocol: exact;
	}
	actions {
		drop_10016;
		_nop;
	}
	size : 64;
}


// Map 4 of query 10016
action do_map_10016_4(){
}

table map_10016_4 {
	actions {
		do_map_10016_4;
	}
	size : 1;
}


// Distinct 5 of query 10016
header_type meta_distinct_10016_5_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_10016_5_t meta_distinct_10016_5;

field_list hash_distinct_10016_5_fields {
	meta_mapinit_10016_1.dIP;
	meta_mapinit_10016_1.sIP;
}

field_list_calculation hash_distinct_10016_5 {
	input {
		hash_distinct_10016_5_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

register distinct_10016_5 {
	width: 32;
	instance_count: 4096;
}

action do_init_distinct_10016_5(){
	modify_field_with_hash_based_offset(meta_distinct_10016_5.index, 0, hash_distinct_10016_5, 4096);
	register_read(meta_distinct_10016_5.value, distinct_10016_5, meta_distinct_10016_5.index);
	bit_or(meta_distinct_10016_5.value, meta_distinct_10016_5.value, 1);
	register_write(distinct_10016_5, meta_distinct_10016_5.index, meta_distinct_10016_5.value);
}

table init_distinct_10016_5 {
	actions {
		do_init_distinct_10016_5;
	}
	size : 1;
}

table pass_distinct_10016_5 {
	actions {
		_nop;
	}
	size : 1;
}

table drop_distinct_10016_5 {
	actions {
		drop_10016;
	}
	size : 1;
}


// Map 6 of query 10016
action do_map_10016_6(){
}

table map_10016_6 {
	actions {
		do_map_10016_6;
	}
	size : 1;
}


// query 10032
header_type out_header_10032_t {
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
	modify_field(out_header_10032.qid, meta_mapinit_10032_1.qid);
	modify_field(out_header_10032.dMac, meta_mapinit_10032_1.dMac);
	modify_field(out_header_10032.sIP, meta_mapinit_10032_1.sIP);
	modify_field(out_header_10032.proto, meta_mapinit_10032_1.proto);
	modify_field(out_header_10032.sMac, meta_mapinit_10032_1.sMac);
	modify_field(out_header_10032.nBytes, meta_mapinit_10032_1.nBytes);
	modify_field(out_header_10032.dPort, meta_mapinit_10032_1.dPort);
	modify_field(out_header_10032.sPort, meta_mapinit_10032_1.sPort);
	modify_field(out_header_10032.dIP, meta_mapinit_10032_1.dIP);
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
header_type meta_mapinit_10032_1_t {
	fields {
		dMac: 48;
		sIP: 32;
		proto: 16;
		qid: 16;
		sMac: 48;
		nBytes: 16;
		dPort: 16;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_mapinit_10032_1_t meta_mapinit_10032_1;

action do_mapinit_10032_1(){
	modify_field(meta_mapinit_10032_1.dMac, ethernet.dstAddr);
	modify_field(meta_mapinit_10032_1.sIP, ipv4.srcAddr);
	modify_field(meta_mapinit_10032_1.proto, ipv4.protocol);
	modify_field(meta_mapinit_10032_1.qid, 10032);
	modify_field(meta_mapinit_10032_1.sMac, ethernet.srcAddr);
	modify_field(meta_mapinit_10032_1.nBytes, ipv4.totalLen);
	modify_field(meta_mapinit_10032_1.dPort, tcp.dstPort);
	modify_field(meta_mapinit_10032_1.sPort, tcp.srcPort);
	modify_field(meta_mapinit_10032_1.dIP, ipv4.dstAddr);
}

table mapinit_10032_1 {
	actions {
		do_mapinit_10032_1;
	}
	size : 1;
}


// Filter 2 of query 10032
table filter_10032_2 {
	reads {
		ipv4.dstAddr: lpm;
	}
	actions {
		drop_10032;
		_nop;
	}
	size : 64;
}


// Map 3 of query 10032
action do_map_10032_3(){
	bit_and(meta_mapinit_10032_1.dIP, meta_mapinit_10032_1.dIP, 0xffffffff);
}

table map_10032_3 {
	actions {
		do_map_10032_3;
	}
	size : 1;
}


control ingress {
	apply(init_app_metadata);
		// query 10016
		if (meta_app_data.drop_10016 != 1) {
			apply(mapinit_10016_1);
			if (meta_app_data.drop_10016 != 1) {
				apply(map_10016_2);
				if (meta_app_data.drop_10016 != 1) {
					apply(filter_10016_3);
					if (meta_app_data.drop_10016 != 1) {
						apply(map_10016_4);
						if (meta_app_data.drop_10016 != 1) {
							apply(init_distinct_10016_5);
							if (meta_distinct_10016_5.value <= 1) {
								apply(pass_distinct_10016_5);
							}
							else {
								apply(drop_distinct_10016_5);
							}
							if (meta_app_data.drop_10016 != 1) {
								apply(map_10016_6);
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
				apply(filter_10032_2);
				if (meta_app_data.drop_10032 != 1) {
					apply(map_10032_3);
					if (meta_app_data.drop_10032 != 1) {
						apply(mark_satisfied_10032);
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
		if (meta_app_data.satisfied_10016 == 1) {
			apply(add_out_header_10016);
		}
		if (meta_app_data.satisfied_10032 == 1) {
			apply(add_out_header_10032);
		}
		apply(add_final_header);
	}
}

