#include "includes/headers.p4"
#include "includes/parser.p4"
#include "includes/distinct.p4"
#include "includes/reduce.p4"
#include "includes/utils.p4"

#define TABLE_WIDTH 16
#define TABLE_SIZE 4096
#define DISTINCT 0
#define THRESHOLD 2

header_type outTuple_header_t {
	 fields {
			 dIP: 32;
			 count: 8;
	 }
}

header outTuple_header_t outTuple_header;

field_list copy_to_cpu_fields {
    standard_metadata;
		meta_distinct;
		meta_reduce;
}

control ingress {
	apply(start_distinct);
	apply(start_reduce);

	if(meta_distinct.distinctVal > DISTINCT) {
		apply(skip1);
	}
	else if (meta_distinct.distinctVal == DISTINCT) {
		apply(drop1);
	}
	else {
		apply(drop2);
	}

	apply(update_distinct_counts);

	apply(update_reduce_counts);

	if(meta_reduce.reduceVal > THRESHOLD) {
		apply(set_count);
	}
	else if (meta_reduce.reduceVal == THRESHOLD) {
		apply(skip2);
	}
	else {
		apply(drop3);
	}
	apply(copy_to_cpu);
}

control egress {
		apply(encap);
}

action do_encap() {
    add_header(outTuple_header);
    modify_field(outTuple_header.dIP, ipv4.dstAddr);
    modify_field(outTuple_header.count, meta_reduce.reduceVal);
}

table encap {
    actions { do_encap; }
    size : 1;
}
