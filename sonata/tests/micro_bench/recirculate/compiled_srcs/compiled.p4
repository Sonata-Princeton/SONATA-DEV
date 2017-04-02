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


parser parse_out_header {
	extract(out_header_10016);
	extract(out_header_10032);
	return parse_ethernet;
}

header_type out_header_10016_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_10016_t out_header_10016;

header_type out_header_10032_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_10032_t out_header_10032;

header_type meta_map_init_10016_t {
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

metadata meta_map_init_10016_t meta_map_init_10016;

header_type meta_distinct_2_10016_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_10016_t meta_distinct_2_10016;

header_type hash_meta_distinct_2_10016_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_10016_t hash_meta_distinct_2_10016;

header_type meta_reduce_3_10016_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_10016_t meta_reduce_3_10016;

header_type hash_meta_reduce_3_10016_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_10016_t hash_meta_reduce_3_10016;

header_type meta_map_init_10032_t {
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

metadata meta_map_init_10032_t meta_map_init_10032;

header_type meta_distinct_3_10032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_10032_t meta_distinct_3_10032;

header_type hash_meta_distinct_3_10032_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_10032_t hash_meta_distinct_3_10032;

header_type meta_reduce_4_10032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_10032_t meta_reduce_4_10032;

header_type hash_meta_reduce_4_10032_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_10032_t hash_meta_reduce_4_10032;

header_type meta_fm_t {
	fields {
		f1 : 8;
	}
}

metadata meta_fm_t meta_fm;

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){   } 
	if (meta_fm.f1 == 1){  } 
	if (meta_fm.f1 == 2){  apply(send_original_out);  } 
}

control egress {
    if (standard_metadata.instance_type != 1)
    { 	if(meta_fm.f1 < 2) {
     		apply(recirculate_to_ingress);
    } 
}

