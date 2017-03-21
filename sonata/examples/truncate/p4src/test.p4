#include "includes/headers.p4"
#include "includes/parser.p4"

parser start {
	return parse_ethernet;
}

/* Report Duplicate Packet Action -- For now use copy_to_cpu */
#define LD_SESSION_ID 111

header_type dummy_md_t {
	fields {
		hello : 32;
	}
}

metadata dummy_md_t dummy_md;

field_list report_fields_list {
	dummy_md;
}

action copy_i2e_action(){
	clone_ingress_pkt_to_egress(LD_SESSION_ID, report_fields_list);
}

table copy_i2e{
	actions{
		copy_i2e_action;
	}
    size: 1;
}

action truncate_packet_action() {
	truncate(100);
}

table truncate_packet {
	actions {
		truncate_packet_action;
	}
	size: 1;
}

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

#define PKT_INSTANCE_TYPE_NORMAL 0
#define PKT_INSTANCE_TYPE_INGRESS_CLONE 1
#define PKT_INSTANCE_TYPE_EGRESS_CLONE 2

control ingress {
	apply(copy_i2e);
	
	apply(forward);
}

control egress {
	if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_INGRESS_CLONE) {
		apply(truncate_packet);
	}
}
