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
	extract(out_header);
	return parse_ethernet;
}

action _nop(){
	no_op();
}

field_list report_packet_fields {
    standard_metadata;
    meta_reduce;
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

header_type out_header_t {
	// Add code here
}
header out_header_t out_header;

action do_add_out_header(){
	// Add code here
}

table add_out_header {
	actions {
		do_add_out_header;
	}
	size : 1;
}

header_type meta_app_data_t {
	// Add code here
}

metadata meta_app_data_t meta_app_data;

action set_yield(){
	// Add code here
}

table filter_1 {
	reads {
		// Add code here
	}
	actions {
		set_yield;
		_nop;
	}
	size : 64;
}

header_type meta_reduce_t {
	// Add code here
}

metadata meta_reduce_t meta_reduce;

field_list hash_reduce_fields {
	// Add code here
}

field_list_calculation hash_reduce {
	input {
		// Add code here
	}
	algorithm: crc16;
	output_width: 16;
}

register reduce_1 {
	// Add code here
}

action do_init_reduce_1(){
    // Update the functions below
	modify_field_with_hash_based_offset(...);
	register_read(...);
	modify_field(...);
	register_write(...);
}

table init_reduce_1 {
	actions {
		do_init_reduce_1;
	}
	size : 1;
}

control ingress {
    apply(filter_1);
        // Apply reduce operation only if yield ==1
        if(...)
        {
            apply(init_reduce_1);
            // Report only a single packet for each key (destination IP address)
            // for which the count exceeds the threshold
            if (...) {
                apply(report_packet);
            }
        }
}

control egress {
	if (standard_metadata.instance_type == 0) {
		// original packet, apply forwarding
	}

	else if (standard_metadata.instance_type == 1) {
        apply(add_out_header);
	}
}