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
	recirculate_flag : 16;}
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

table drop_table {
	actions {_drop;}
	size : 1;
}

table drop_packets {
	actions {_drop;}
	size : 1;
}

action mark_drop() {
	modify_field(meta_fm.is_drop, 1);
}

parser parse_out_header {
	extract(out_header_30001);
	extract(out_header_30002);
	return parse_ethernet;
}

header_type out_header_30001_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_30001_t out_header_30001;

field_list copy_to_cpu_fields_30001{
	standard_metadata;
	meta_map_init_30001;
	meta_fm;
}

action do_copy_to_cpu_30001() {
	clone_ingress_pkt_to_egress(30201, copy_to_cpu_fields_30001);
}

table copy_to_cpu_30001 {
	actions {do_copy_to_cpu_30001;}
	size : 1;
}

table encap_30001 {
	actions { do_encap_30001; }
	size : 1;
}

action do_encap_30001() {
	add_header(out_header_30001);
	modify_field(out_header_30001.qid, meta_map_init_30001.qid);
	modify_field(out_header_30001.dIP, meta_map_init_30001.dIP);
}

header_type out_header_30002_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_30002_t out_header_30002;

field_list copy_to_cpu_fields_30002{
	standard_metadata;
	meta_map_init_30002;
	meta_fm;
}

action do_copy_to_cpu_30002() {
	clone_ingress_pkt_to_egress(30202, copy_to_cpu_fields_30002);
}

table copy_to_cpu_30002 {
	actions {do_copy_to_cpu_30002;}
	size : 1;
}

table encap_30002 {
	actions { do_encap_30002; }
	size : 1;
}

action do_encap_30002() {
	add_header(out_header_30002);
	modify_field(out_header_30002.qid, meta_map_init_30002.qid);
	modify_field(out_header_30002.dIP, meta_map_init_30002.dIP);
}

table map_init_30001{
	actions{
		do_map_init_30001;
	}
}

action do_map_init_30001(){
	modify_field(meta_map_init_30001.qid, 30001);
	modify_field(meta_map_init_30001.dIP, ipv4.dstAddr);
}

header_type meta_map_init_30001_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_30001_t meta_map_init_30001;

table map_init_30002{
	actions{
		do_map_init_30002;
	}
}

action do_map_init_30002(){
	modify_field(meta_map_init_30002.qid, 30002);
	modify_field(meta_map_init_30002.dIP, ipv4.dstAddr);
}

header_type meta_map_init_30002_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_30002_t meta_map_init_30002;

header_type meta_fm_t {
	fields {
		qid_30001 : 1;
		qid_30002 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_30001, 1);
	modify_field(meta_fm.qid_30002, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_30001(){
	modify_field(meta_fm.qid_30001, 1);
}

action set_meta_fm_30002(){
	modify_field(meta_fm.qid_30002, 1);
}

action reset_meta_fm_30001(){
	modify_field(meta_fm.qid_30001, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_30002(){
	modify_field(meta_fm.qid_30002, 0);
	modify_field(meta_fm.is_drop, 1);
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_30001 == 1){
					apply(map_init_30001);
			apply(copy_to_cpu_30001);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_30002 == 1){
					apply(map_init_30002);
			apply(copy_to_cpu_30002);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 2) {
			apply(recirculate_to_ingress);
		}
		else {
			apply(drop_table);
		}
	}

	else if (standard_metadata.instance_type == 1) {
		if (meta_fm.is_drop == 1){
			apply(drop_packets);
		}
		else {
			if (meta_fm.f1 == 0){
				apply(encap_30001);
			}
			if (meta_fm.f1 == 1){
				apply(encap_30002);
			}
		}


	}
}

