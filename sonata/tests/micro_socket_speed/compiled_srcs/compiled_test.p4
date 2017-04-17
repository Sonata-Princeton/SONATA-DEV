
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
	recirculate_flag : 16;
	}
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


action do_send_original_out() {
	    modify_field(standard_metadata.egress_spec, 13);
}

table send_original_out {
	actions { do_send_original_out; }
	size : 1;
}
header_type meta_fm_t {
	fields {
		f1 : 8;
	}
}

metadata meta_fm_t meta_fm;


table send_filter_updates {
	reads {
		ipv4.dstAddr: lpm;
	}
	actions {
		_nop;
		_drop;
	}
	size : 100000;
}

parser parse_out_header {
	
	return parse_ethernet;
}   
///Sequential
header_type meta_app_data_t {
	fields {
		
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;

control ingress {
    apply(send_filter_updates);
    apply(send_original_out);
}


control egress {
}