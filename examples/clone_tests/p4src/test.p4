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

/*action copy_i2i_action(){
	clone_ingress_pkt_to_ingress(LD_SESSION_ID, report_fields_list);
}

table copy_i2i{
	actions{
		copy_i2i_action;
	}
    size: 1;
}*/

action copy_i2e_action(){
	clone_ingress_pkt_to_egress(LD_SESSION_ID, report_fields_list);
}

table copy_i2e{
	actions{
		copy_i2e_action;
	}
    size: 1;
}

/*action copy_e2i_action(){
	clone_egress_pkt_to_ingress(LD_SESSION_ID, report_fields_list);
}

table copy_e2i{
	actions{
		copy_e2i_action;
	}
    size: 1;
}*/

action copy_e2e_action(){
	clone_egress_pkt_to_egress(LD_SESSION_ID, report_fields_list);
}

table copy_e2e{
	actions{
		copy_e2e_action;
	}
    size: 1;
}

action ingress_iclone_tagging(){
	modify_field(tcp.srcPort, 555);
}

table ingress_iclone_tag{
	actions{
		ingress_iclone_tagging;
	}
    size: 1;
}

action ingress_eclone_tagging(){
	modify_field(tcp.srcPort, 777);
}

table ingress_eclone_tag{
	actions{
		ingress_eclone_tagging;
	}
    size: 1;
}

action egress_iclone_tagging(){
	modify_field(tcp.dstPort, 888);
}

table egress_iclone_tag{
	actions{
		egress_iclone_tagging;
	}
    size: 1;
}

action egress_eclone_tagging(){
	modify_field(tcp.dstPort, 999);
}

table egress_eclone_tag{
	actions{
		egress_eclone_tagging;
	}
    size: 1;
}

action egress_tagging(){
	modify_field(ethernet.srcAddr, ethernet.srcAddr | 0xffffff000000);
}

table egress_tag{
	actions{
		egress_tagging;
	}
    size: 1;
}

action ingress_tagging(){
	modify_field(ethernet.srcAddr, ethernet.srcAddr | 0x000000ffffff);
}

table ingress_tag{
	actions{
		ingress_tagging;
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
	
	if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_NORMAL) {
		//apply(copy_i2i);
		
		//apply(copy_i2e);
		
		//apply(copy_e2i);
		
		//apply(copy_e2e);
	}
	else {
		if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_INGRESS_CLONE) {
			apply(ingress_iclone_tag); // srcport 555
		}
		if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_EGRESS_CLONE) {
			apply(ingress_eclone_tag); // srcport 777
		}
	}
	
	
	apply(forward);
	apply(ingress_tag); // srcmac 00:00:00:FF:FF:FF
}

control egress {
	
	if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_NORMAL) {
		//apply(copy_i2i);
		
		//apply(copy_i2e);
		
		//apply(copy_e2i);
		
		apply(copy_e2e);
	}
	
	apply(egress_tag); // srcmac FF:FF:FF:00:00:00
	
	if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_INGRESS_CLONE) {
		apply(egress_iclone_tag); // dstport 888
	}
	if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_EGRESS_CLONE) {
		apply(egress_eclone_tag); // dstport 999
	}

}
