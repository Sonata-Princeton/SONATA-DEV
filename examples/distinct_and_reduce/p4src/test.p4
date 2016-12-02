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

parser parse_out_header {
	extract(out_header_2);
	return parse_ethernet;
}

header_type out_header_2_t {
	fields {
		dIP : 32;
		count : 8;
	}
}

header out_header_2_t out_header_2;

field_list copy_to_cpu_fields_2                 {
	standard_metadata;
	meta_register_0_2;
}

action do_copy_to_cpu_2() {
	clone_ingress_pkt_to_egress(202, copy_to_cpu_fields_2);
}

table copy_to_cpu_2 {
	actions {do_copy_to_cpu_2;}
	size : 1;
}

table encap_2 {
	actions { do_encap_2; }
	size : 1;
}

action do_encap_2() {
	add_header(out_header_2);
	modify_field(out_header_2.dIP, ipv4.dstAddr);
	modify_field(out_header_2.count, meta_register_0_2.val);
}

table skip_register_0_2_1 {
	actions {_nop;}
	size : 1;
}

table drop_register_0_2_1 {
	actions {_drop;}
	size : 1;
}

header_type meta_register_0_2_t {
	fields {
		idx : 16;
		val : 16;
	}
}

metadata meta_register_0_2_t meta_register_0_2;

field_list register_0_2_fields {
	ipv4.dstAddr;
}

field_list_calculation register_0_2_fields_hash {
	input {
		register_0_2_fields;
	}
	algorithm : crc32;
	output_width : 16;
}

register register_0_2{
	width : 16;
	instance_count : 4096;
}

action update_register_0_2_regs() {
	add_to_field(meta_register_0_2.val, 1);
	register_write(register_0_2,meta_register_0_2.idx,meta_register_0_2.val);
}

table update_register_0_2_counts {
	actions {update_register_0_2_regs;}
	size : 1;
}

action do_register_0_2_hashes() {
	modify_field_with_hash_based_offset(meta_register_0_2.val, 0,register_0_2_fields_hash , 4096);
	register_read(meta_register_0_2.val, register_0_2, meta_register_0_2.idx);
}

table start_register_0_2 {
	actions {do_register_0_2_hashes;}
	size : 1;
}

action set_register_0_2_count() {
	modify_field(meta_register_0_2.val, 1);
}

table set_register_0_2_count {
	actions {set_register_0_2_count;}
        size: 1;
}

control ingress {
	apply(start_register_0_2);
	apply(update_register_0_2_counts);
	if(meta_register_0_2.val > 0) {
		apply(set_register_0_2_count);	}
	else if(meta_register_0_2.val == 0) {
		apply(skip_register_0_2_1);
	}
	else {
		apply(drop_register_0_2_1);
	}

	apply(copy_to_cpu_2);}

control egress {
	apply(encap_2);
}
