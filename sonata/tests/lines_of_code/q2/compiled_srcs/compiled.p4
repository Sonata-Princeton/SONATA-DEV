#include "includes/headers.p4"
#include "includes/parser.p4"

parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}

parser parse_out_header {
	extract(out_header_20016);
	extract(out_header_20032);
	return parse_final_header;
}

parser parse_final_header {
	extract(final_header);
	return parse_ethernet;
}

action do_init_app_metadata(){
	modify_field(meta_app_data.drop_20016, 0);
	modify_field(meta_app_data.satisfied_20016, 0);
	modify_field(meta_app_data.drop_20032, 0);
	modify_field(meta_app_data.satisfied_20032, 0);
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
		drop_20016: 1;
		satisfied_20016: 1;
		drop_20032: 1;
		satisfied_20032: 1;
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;

action _nop(){
	no_op();
}

field_list report_packet_fields {
	meta_app_data;
	meta_mapinit_20016_1;
	meta_mapinit_20032_1;
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

// query 20016
header_type out_header_20016_t {
	fields {
		qid: 16;
	}
}

header out_header_20016_t out_header_20016;

action drop_20016(){
	modify_field(meta_app_data.drop_20016, 1);
}

action do_mark_satisfied_20016(){
	modify_field(meta_app_data.satisfied_20016, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_20016(){
	add_header(out_header_20016);
	modify_field(out_header_20016.qid, meta_mapinit_20016_1.qid);
}

table add_out_header_20016 {
	actions {
		do_add_out_header_20016;
	}
	size : 1;
}

table mark_satisfied_20016 {
	actions {
		do_mark_satisfied_20016;
	}
	size : 1;
}

// MapInit of query 20016
header_type meta_mapinit_20016_1_t {
	fields {
		dPort: 16;
		qid: 16;
		sIP: 32;
		dIP: 32;
		sPort: 16;
	}
}

metadata meta_mapinit_20016_1_t meta_mapinit_20016_1;

action do_mapinit_20016_1(){
	modify_field(meta_mapinit_20016_1.dPort, tcp.dstPort);
	modify_field(meta_mapinit_20016_1.qid, 20016);
	modify_field(meta_mapinit_20016_1.sIP, ipv4.srcAddr);
	modify_field(meta_mapinit_20016_1.dIP, ipv4.dstAddr);
	modify_field(meta_mapinit_20016_1.sPort, tcp.srcPort);
}

table mapinit_20016_1 {
	actions {
		do_mapinit_20016_1;
	}
	size : 1;
}


// Map 2 of query 20016
action do_map_20016_2(){
	bit_and(meta_mapinit_20016_1.dPort, meta_mapinit_20016_1.dPort, 0xffff);
}

table map_20016_2 {
	actions {
		do_map_20016_2;
	}
	size : 1;
}


// Map 3 of query 20016
action do_map_20016_3(){
}

table map_20016_3 {
	actions {
		do_map_20016_3;
	}
	size : 1;
}


// query 20032
header_type out_header_20032_t {
	fields {
		qid: 16;
		dPort: 16;
		sIP: 32;
		dIP: 32;
		sPort: 16;
	}
}

header out_header_20032_t out_header_20032;

action drop_20032(){
	modify_field(meta_app_data.drop_20032, 1);
}

action do_mark_satisfied_20032(){
	modify_field(meta_app_data.satisfied_20032, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_20032(){
	add_header(out_header_20032);
	modify_field(out_header_20032.qid, meta_mapinit_20032_1.qid);
	modify_field(out_header_20032.dPort, meta_mapinit_20032_1.dPort);
	modify_field(out_header_20032.sIP, meta_mapinit_20032_1.sIP);
	modify_field(out_header_20032.dIP, meta_mapinit_20032_1.dIP);
	modify_field(out_header_20032.sPort, meta_mapinit_20032_1.sPort);
}

table add_out_header_20032 {
	actions {
		do_add_out_header_20032;
	}
	size : 1;
}

table mark_satisfied_20032 {
	actions {
		do_mark_satisfied_20032;
	}
	size : 1;
}

// MapInit of query 20032
header_type meta_mapinit_20032_1_t {
	fields {
		sIP: 32;
		qid: 16;
		dPort: 16;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_mapinit_20032_1_t meta_mapinit_20032_1;

action do_mapinit_20032_1(){
	modify_field(meta_mapinit_20032_1.sIP, ipv4.srcAddr);
	modify_field(meta_mapinit_20032_1.qid, 20032);
	modify_field(meta_mapinit_20032_1.dPort, tcp.dstPort);
	modify_field(meta_mapinit_20032_1.sPort, tcp.srcPort);
	modify_field(meta_mapinit_20032_1.dIP, ipv4.dstAddr);
}

table mapinit_20032_1 {
	actions {
		do_mapinit_20032_1;
	}
	size : 1;
}


// Filter 2 of query 20032
table filter_20032_2 {
	reads {
		tcp.dstPort: lpm;
	}
	actions {
		drop_20032;
		_nop;
	}
	size : 64;
}


// Map 3 of query 20032
action do_map_20032_3(){
	bit_and(meta_mapinit_20032_1.dPort, meta_mapinit_20032_1.dPort, 0xffffffff);
}

table map_20032_3 {
	actions {
		do_map_20032_3;
	}
	size : 1;
}


control ingress {
	apply(init_app_metadata);
		// query 20016
		if (meta_app_data.drop_20016 != 1) {
			apply(mapinit_20016_1);
			if (meta_app_data.drop_20016 != 1) {
				apply(map_20016_2);
				if (meta_app_data.drop_20016 != 1) {
					apply(map_20016_3);
					if (meta_app_data.drop_20016 != 1) {
						apply(mark_satisfied_20016);
					}
				}
			}
		}
		// query 20032
		if (meta_app_data.drop_20032 != 1) {
			apply(mapinit_20032_1);
			if (meta_app_data.drop_20032 != 1) {
				apply(filter_20032_2);
				if (meta_app_data.drop_20032 != 1) {
					apply(map_20032_3);
					if (meta_app_data.drop_20032 != 1) {
						apply(mark_satisfied_20032);
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
		if (meta_app_data.satisfied_20016 == 1) {
			apply(add_out_header_20016);
		}
		if (meta_app_data.satisfied_20032 == 1) {
			apply(add_out_header_20032);
		}
		apply(add_final_header);
	}
}

