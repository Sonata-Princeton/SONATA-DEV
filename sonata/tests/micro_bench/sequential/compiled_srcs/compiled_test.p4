
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


header_type out_header_0_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_0_t out_header_0;


//Map
header_type meta_map_init_0_t {
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

metadata meta_map_init_0_t meta_map_init_0;
            

//Reduce
header_type meta_reduce_0_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_0_t meta_reduce_0;

header_type hash_meta_reduce_0_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_0_t hash_meta_reduce_0;
            

header_type meta_distinct_0_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_0_t meta_distinct_0;

header_type hash_meta_distinct_0_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_0_t hash_meta_distinct_0;
            


header_type out_header_1_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_1_t out_header_1;


//Map
header_type meta_map_init_1_t {
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

metadata meta_map_init_1_t meta_map_init_1;
            

//Reduce
header_type meta_reduce_1_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_1_t meta_reduce_1;

header_type hash_meta_reduce_1_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_1_t hash_meta_reduce_1;
            

header_type meta_distinct_1_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_1_t meta_distinct_1;

header_type hash_meta_distinct_1_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_1_t hash_meta_distinct_1;
            


header_type out_header_2_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_2_t out_header_2;


//Map
header_type meta_map_init_2_t {
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

metadata meta_map_init_2_t meta_map_init_2;
            

//Reduce
header_type meta_reduce_2_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_t meta_reduce_2;

header_type hash_meta_reduce_2_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_2_t hash_meta_reduce_2;
            

header_type meta_distinct_2_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_t meta_distinct_2;

header_type hash_meta_distinct_2_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_t hash_meta_distinct_2;
            


parser parse_out_header {
	extract(out_header_0);
extract(out_header_1);
extract(out_header_2);

	return parse_ethernet;
}   
///Sequential
header_type meta_app_data_t {
	fields {
		drop_0: 1;
satisfied_0: 1;drop_1: 1;
satisfied_1: 1;drop_2: 1;
satisfied_2: 1;
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;

control ingress {
    apply(send_original_out);
}


control egress {
}