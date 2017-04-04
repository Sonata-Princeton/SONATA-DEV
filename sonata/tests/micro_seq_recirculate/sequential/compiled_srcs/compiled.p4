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

header_type final_header_t {
	fields {
		delimiter: 32;
	}
}

header final_header_t final_header;

// query 10016
header_type out_header_10016_t {
	fields {
		qid: 16;
		dIP: 32;
		count: 16;
	}
}

header out_header_10016_t out_header_10016;

// MapInit of query 10016
header_type meta_mapinit_10016_1_t {
	fields {
		count: 16;
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

// Distinct 4 of query 10016
header_type meta_distinct_10016_4_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_10016_4_t meta_distinct_10016_4;

// Reduce 6 of query 10016
header_type meta_reduce_10016_6_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_reduce_10016_6_t meta_reduce_10016_6;

// query 10032
header_type out_header_10032_t {
	fields {
		qid: 16;
		dIP: 32;
		count: 16;
	}
}

header out_header_10032_t out_header_10032;


// MapInit of query 10032
header_type meta_mapinit_10032_1_t {
	fields {
		count: 16;
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

// Distinct 5 of query 10032
header_type meta_distinct_10032_5_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_distinct_10032_5_t meta_distinct_10032_5;

// Reduce 7 of query 10032
header_type meta_reduce_10032_7_t {
	fields {
		value: 32;
		index: 12;
	}
}

metadata meta_reduce_10032_7_t meta_reduce_10032_7;

action do_send_original_out() {
	modify_field(standard_metadata.egress_spec, 13);
}

table send_original_out {
	actions { do_send_original_out; }
	size : 1;
}

control ingress {
    apply(send_original_out);
}

control egress {
}

