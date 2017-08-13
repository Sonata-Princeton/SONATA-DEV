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
		srcAddr : 32;
		dstAddr : 32;
	}
}

header ipv4_t ipv4;

parser parse_ipv4 {
	extract(ipv4);
	return select(latest.protocol) {
		default: ingress;
	}
}

header_type ethernet_t {
	fields {
		dstAddr : 48;
		srcAddr : 48;
		etherType : 16;
	}
}

header ethernet_t ethernet;

parser parse_ethernet {
	extract(ethernet);
	return select(latest.etherType) {
		0x0800 : parse_ipv4;
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
	extract(out_header_10032);
	extract(final_header);
	return parse_ethernet;
}

action do_init_app_metadata(){
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

// query 10032
header_type out_header_10032_t {
	fields {
		qid : 16;
		ipv4_dstIP : 32;
		ipv4_srcIP : 32;
		ipv4_totalLen : 16;
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
	modify_field(out_header_10032.ipv4_srcIP, meta_mapinit_10032_1.ipv4_srcIP);
	modify_field(out_header_10032.ipv4_totalLen, meta_mapinit_10032_1.ipv4_totalLen);
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
		ipv4_totalLen: 16;
		ipv4_srcIP: 32;
		ipv4_dstIP: 32;
	}
}

metadata meta_mapinit_10032_1_t meta_mapinit_10032_1;

action do_mapinit_10032_1(){
	modify_field(meta_mapinit_10032_1.qid, 10032);
	modify_field(meta_mapinit_10032_1.ipv4_totalLen, ipv4.totalLen);
	modify_field(meta_mapinit_10032_1.ipv4_srcIP, ipv4.srcAddr);
	modify_field(meta_mapinit_10032_1.ipv4_dstIP, ipv4.dstAddr);
}

table mapinit_10032_1 {
	actions {
		do_mapinit_10032_1;
	}
	size : 1;
}


// Map 2 of query 10032
action do_map_10032_2(){
	bit_and(meta_mapinit_10032_1.ipv4_dstIP, meta_mapinit_10032_1.ipv4_dstIP, 0xffffffff);
}

table map_10032_2 {
	actions {
		do_map_10032_2;
	}
	size : 1;
}


// Map 3 of query 10032
action do_map_10032_3(){
}

table map_10032_3 {
	actions {
		do_map_10032_3;
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
	meta_mapinit_10032_1.ipv4_dstIP;
	meta_mapinit_10032_1.ipv4_srcIP;
	meta_mapinit_10032_1.ipv4_totalLen;
}

field_list_calculation hash_distinct_10032_4 {
	input {
		hash_distinct_10032_4_fields;
	}
	algorithm: crc32;
	output_width: 12;
}

register distinct_10032_4 {
	width: 32;
	instance_count: 4096;
}

action do_init_distinct_10032_4(){
	modify_field_with_hash_based_offset(meta_distinct_10032_4.index, 0, hash_distinct_10032_4, 4096);
	register_read(meta_distinct_10032_4.value, distinct_10032_4, meta_distinct_10032_4.index);
	bit_or(meta_distinct_10032_4.value, meta_distinct_10032_4.value, 1);
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
	apply(init_app_metadata);
		// query 10032
		if (meta_app_data.drop_10032 != 1) {
			apply(mapinit_10032_1);
			if (meta_app_data.drop_10032 != 1) {
				apply(map_10032_2);
				if (meta_app_data.drop_10032 != 1) {
					apply(map_10032_3);
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
		if (meta_app_data.satisfied_10032 == 1) {
			apply(add_out_header_10032);
		}
		apply(add_final_header);
	}
}

