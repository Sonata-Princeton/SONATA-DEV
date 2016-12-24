#include "includes/headers.p4"
#include "includes/parser.p4"

header_type join_metadata_t {
    fields {
        filter_index: 32;
        filter_value: 1;
    }
}

metadata join_metadata_t join_metadata;

/* Flow Filter Hash - 5 tuple and egress port */
field_list join_filter_list {
        tcp.dstPort;
}

field_list_calculation join_filter_hash {
    input {
        join_filter_list;
    }
    algorithm: csum16;
    output_width: 16;
}

#define JOIN_FILTER_WIDTH 1024

register join_filter {
    width: 1;
    instance_count: JOIN_FILTER_WIDTH;
}

/* Compute Hashes */
action compute_hash() {
	// flow filter indices
	modify_field_with_hash_based_offset(join_metadata.filter_index, 0, join_filter_hash, JOIN_FILTER_WIDTH);
    
    // load flow filter values
    register_read(join_metadata.filter_value, join_filter, join_metadata.filter_index);
}

table compute_hash {
    actions {
        compute_hash;
    }
    size: 1;
}

/* Insert into Filters */
action filter_insert() {
    // write to the flow filter
    register_write(join_filter, join_metadata.filter_index, 1);
}

action _nop() {
    no_op();
}


table insert_in_filters {
	reads {
		tcp.srcPort: exact;
	}
    actions {
        filter_insert;
        _nop;
    }
    size: 1;
}

/* Report Duplicate Packet Action -- For now use copy_to_cpu */
#define LD_SESSION_ID 111

field_list report_fields_list {
        join_metadata.filter_value;
}

action report_join_to_controller() {
	clone_ingress_pkt_to_egress(LD_SESSION_ID, report_fields_list);
}

table report_join {
    actions {
        report_join_to_controller;
    }
    size: 1;
}	

/* Control Flow */
control join {
	apply(compute_hash);

	if  (join_metadata.filter_value != 1) {
		apply(insert_in_filters);
    } else {
    	apply(report_join);
    }
}

/* Normal Control Flow */
action set_default_nhop(port, dstMac) {
    modify_field(standard_metadata.egress_spec, port);
    modify_field(ethernet.dstAddr, dstMac);
    add_to_field(ipv4.ttl, -1);
}

action _drop() {
    drop();
}

table forward {
	reads {
		ipv4.dstAddr: exact;
	}
    actions {
        set_default_nhop;
        _drop;
    }
    size: 16;
}

control ingress {
    apply(forward);
    join();
    
}

control egress {
}
