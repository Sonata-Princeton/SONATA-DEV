header_type ethernet_t {
	fields {
		dstMac : 48;
		srcMac : 48;
		ethType : 16;
	}
}

header ethernet_t ethernet;

parser parse_ethernet {
	extract(ethernet);
	return select(latest.ethType) {
		0x0800 : parse_ipv4;
		default: ingress;
	}
}

header_type tcp_t {
	fields {
		sport : 16;
		dport : 16;
		seqNo : 32;
		ackNo : 32;
		dataOffset : 4;
		res : 4;
		flags : 8;
		window : 16;
		checksum : 16;
		urgentPtr : 16;
	}
}

header tcp_t tcp;

parser parse_tcp {
	extract(tcp);
	return ingress;
}

header_type ipv4_t {
	fields {
		version : 4;
		ihl : 4;
		diffserv : 8;
		totalLen : 16;
		identification : 16;
		flags : 3;
		fragOffset : 13;
		ttl : 8;
		protocol : 8;
		hdrChecksum : 16;
		srcIP : 32;
		dstIP : 32;
	}
}

header ipv4_t ipv4;

parser parse_ipv4 {
	extract(ipv4);
	return select(latest.protocol) {
		6 : parse_tcp;
		default: ingress;
	}
}

parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}

parser parse_out_header {
	extract(out_header_10008);
	extract(out_header_10032);
	extract(final_header);
	return parse_ethernet;
}

action do_init_app_metadata(){
	modify_field(meta_app_data.drop_10008, 0);
	modify_field(meta_app_data.satisfied_10008, 0);
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
		drop_10008: 1;
		satisfied_10008: 1;
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
	meta_mapinit_10008_1;
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
		delimiter : 32;
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

// query 10008
header_type out_header_10008_t {
	fields {
		qid : 16;
		ipv4_dstIP : 32;
		index : 16;
	}
}
header out_header_10008_t out_header_10008;

action drop_10008(){
	modify_field(meta_app_data.drop_10008, 1);
}

action do_mark_satisfied_10008(){
	modify_field(meta_app_data.satisfied_10008, 1);
	modify_field(meta_app_data.clone, 1);
}

action do_add_out_header_10008(){
	add_header(out_header_10008);
	modify_field(out_header_10008.qid, meta_mapinit_10008_1.qid);
	modify_field(out_header_10008.ipv4_dstIP, meta_mapinit_10008_1.ipv4_dstIP);
	modify_field(out_header_10008.index, meta_mapinit_10008_1.index);
}

table add_out_header_10008 {
	actions {
		do_add_out_header_10008;
	}
	size : 1;
}

table mark_satisfied_10008 {
	actions {
		do_mark_satisfied_10008;
	}
	size : 1;
}

// MapInit of query 10008
header_type meta_mapinit_10008_1_t {
	fields {
		qid: 16;
		count: 16;
		tcp_flags: 8;
		ipv4_protocol: 8;
		ipv4_dstIP: 32;
		index: 16;
	}
}

metadata meta_mapinit_10008_1_t meta_mapinit_10008_1;

action do_mapinit_10008_1(){
	modify_field(meta_mapinit_10008_1.qid, 10008);
	modify_field(meta_mapinit_10008_1.count, 0);
	modify_field(meta_mapinit_10008_1.tcp_flags, tcp.flags);
	modify_field(meta_mapinit_10008_1.ipv4_protocol, ipv4.protocol);
	modify_field(meta_mapinit_10008_1.ipv4_dstIP, ipv4.dstIP);
	modify_field(meta_mapinit_10008_1.index, 0);
}

table mapinit_10008_1 {
	actions {
		do_mapinit_10008_1;
	}
	size : 1;
}


// Map 2 of query 10008
action do_map_10008_2(){
	bit_and(meta_mapinit_10008_1.ipv4_dstIP, meta_mapinit_10008_1.ipv4_dstIP, 0xff000000);
}

table map_10008_2 {
	actions {
		do_map_10008_2;
	}
	size : 1;
}


// Filter 3 of query 10008
table filter_10008_3 {
	reads {
		ipv4.protocol: exact;
	}
	actions {
		drop_10008;
		_nop;
	}
	size : 64;
}


// Filter 4 of query 10008
table filter_10008_4 {
	reads {
		tcp.flags: exact;
	}
	actions {
		drop_10008;
		_nop;
	}
	size : 64;
}


// Map 5 of query 10008
action do_map_10008_5(){
}

table map_10008_5 {
	actions {
		do_map_10008_5;
	}
	size : 1;
}


// Reduce 6 of query 10008
header_type meta_reduce_10008_6_t {
	fields {
		value: 32;
		index: 16;
	}
}

metadata meta_reduce_10008_6_t meta_reduce_10008_6;

field_list hash_reduce_10008_6_fields {
	meta_mapinit_10008_1.ipv4_dstIP;
}

field_list_calculation hash_reduce_10008_6 {
	input {
		hash_reduce_10008_6_fields;
	}
	algorithm: crc16;
	output_width: 16;
}

register reduce_10008_6 {
	width: 32;
	instance_count: 65536;
}

action do_init_reduce_10008_6(){
	modify_field_with_hash_based_offset(meta_reduce_10008_6.index, 0, hash_reduce_10008_6, 65536);
	register_read(meta_reduce_10008_6.value, reduce_10008_6, meta_reduce_10008_6.index);
	modify_field(meta_reduce_10008_6.value, meta_reduce_10008_6.value + 1);
	register_write(reduce_10008_6, meta_reduce_10008_6.index, meta_reduce_10008_6.value);
}

action set_count_reduce_10008_6(){
	modify_field(meta_mapinit_10008_1.index, meta_reduce_10008_6.index);
}

table init_reduce_10008_6 {
	actions {
		do_init_reduce_10008_6;
	}
	size : 1;
}

table first_pass_reduce_10008_6 {
	actions {
		set_count_reduce_10008_6;
	}
	size : 1;
}

table drop_reduce_10008_6 {
	actions {
		drop_10008;
	}
	size : 1;
}


// query 10032
header_type out_header_10032_t {
	fields {
		qid : 16;
		ipv4_dstIP : 32;
		index : 16;
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
	modify_field(out_header_10032.ipv4_dstIP, meta_mapinit_10032_1.ipv4_dstIP);
	modify_field(out_header_10032.index, meta_mapinit_10032_1.index);
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
		qid: 16;
		count: 16;
		tcp_flags: 8;
		ipv4_protocol: 8;
		ipv4_dstIP: 32;
		index: 16;
	}
}

metadata meta_mapinit_10032_1_t meta_mapinit_10032_1;

action do_mapinit_10032_1(){
	modify_field(meta_mapinit_10032_1.qid, 10032);
	modify_field(meta_mapinit_10032_1.count, 0);
	modify_field(meta_mapinit_10032_1.tcp_flags, tcp.flags);
	modify_field(meta_mapinit_10032_1.ipv4_protocol, ipv4.protocol);
	modify_field(meta_mapinit_10032_1.ipv4_dstIP, ipv4.dstIP);
	modify_field(meta_mapinit_10032_1.index, 0);
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
		ipv4.dstIP: lpm;
	}
	actions {
		drop_10032;
		_nop;
	}
	size : 64;
}


// Map 3 of query 10032
action do_map_10032_3(){
	bit_and(meta_mapinit_10032_1.ipv4_dstIP, meta_mapinit_10032_1.ipv4_dstIP, 0xffffffff);
}

table map_10032_3 {
	actions {
		do_map_10032_3;
	}
	size : 1;
}


// Filter 4 of query 10032
table filter_10032_4 {
	reads {
		ipv4.protocol: exact;
	}
	actions {
		drop_10032;
		_nop;
	}
	size : 64;
}


// Filter 5 of query 10032
table filter_10032_5 {
	reads {
		tcp.flags: exact;
	}
	actions {
		drop_10032;
		_nop;
	}
	size : 64;
}


// Map 6 of query 10032
action do_map_10032_6(){
}

table map_10032_6 {
	actions {
		do_map_10032_6;
	}
	size : 1;
}


// Reduce 7 of query 10032
header_type meta_reduce_10032_7_t {
	fields {
		value: 32;
		index: 16;
	}
}

metadata meta_reduce_10032_7_t meta_reduce_10032_7;

field_list hash_reduce_10032_7_fields {
	meta_mapinit_10032_1.ipv4_dstIP;
}

field_list_calculation hash_reduce_10032_7 {
	input {
		hash_reduce_10032_7_fields;
	}
	algorithm: crc16;
	output_width: 16;
}

register reduce_10032_7 {
	width: 32;
	instance_count: 65536;
}

action do_init_reduce_10032_7(){
	modify_field_with_hash_based_offset(meta_reduce_10032_7.index, 0, hash_reduce_10032_7, 65536);
	register_read(meta_reduce_10032_7.value, reduce_10032_7, meta_reduce_10032_7.index);
	modify_field(meta_reduce_10032_7.value, meta_reduce_10032_7.value + 1);
	register_write(reduce_10032_7, meta_reduce_10032_7.index, meta_reduce_10032_7.value);
}

action set_count_reduce_10032_7(){
	modify_field(meta_mapinit_10032_1.index, meta_reduce_10032_7.index);
}

table init_reduce_10032_7 {
	actions {
		do_init_reduce_10032_7;
	}
	size : 1;
}

table first_pass_reduce_10032_7 {
	actions {
		set_count_reduce_10032_7;
	}
	size : 1;
}

table drop_reduce_10032_7 {
	actions {
		drop_10032;
	}
	size : 1;
}


control ingress {
	apply(init_app_metadata);
		// query 10008
		if (meta_app_data.drop_10008 != 1) {
			apply(mapinit_10008_1);
			if (meta_app_data.drop_10008 != 1) {
				apply(map_10008_2);
				if (meta_app_data.drop_10008 != 1) {
					apply(filter_10008_3);
					if (meta_app_data.drop_10008 != 1) {
						apply(filter_10008_4);
						if (meta_app_data.drop_10008 != 1) {
							apply(map_10008_5);
							if (meta_app_data.drop_10008 != 1) {
								apply(init_reduce_10008_6);
								if (meta_reduce_10008_6.value == 1) {
									apply(first_pass_reduce_10008_6);
								}
								else {
									apply(drop_reduce_10008_6);
								}
								if (meta_app_data.drop_10008 != 1) {
									apply(mark_satisfied_10008);
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
						apply(filter_10032_4);
						if (meta_app_data.drop_10032 != 1) {
							apply(filter_10032_5);
							if (meta_app_data.drop_10032 != 1) {
								apply(map_10032_6);
								if (meta_app_data.drop_10032 != 1) {
									apply(init_reduce_10032_7);
									if (meta_reduce_10032_7.value == 1) {
										apply(first_pass_reduce_10032_7);
									}
									else {
										apply(drop_reduce_10032_7);
									}
									if (meta_app_data.drop_10032 != 1) {
										apply(mark_satisfied_10032);
									}
								}
							}
						}
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
		if (meta_app_data.satisfied_10008 == 1) {
			apply(add_out_header_10008);
		}
		if (meta_app_data.satisfied_10032 == 1) {
			apply(add_out_header_10032);
		}
		apply(add_final_header);
	}
}
