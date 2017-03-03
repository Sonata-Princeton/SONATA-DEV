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
	extract(out_header_140032);
	extract(out_header_20032);
	extract(out_header_80004);
	extract(out_header_20012);
	extract(out_header_80012);
	extract(out_header_70032);
	extract(out_header_10012);
	extract(out_header_80032);
	extract(out_header_50032);
	extract(out_header_100004);
	extract(out_header_80028);
	extract(out_header_100012);
	extract(out_header_10032);
	extract(out_header_110004);
	extract(out_header_110012);
	extract(out_header_100032);
	extract(out_header_40004);
	extract(out_header_40012);
	extract(out_header_110028);
	extract(out_header_110032);
	extract(out_header_50004);
	extract(out_header_130012);
	extract(out_header_40032);
	extract(out_header_140004);
	extract(out_header_50012);
	extract(out_header_140012);
	extract(out_header_130032);
	extract(out_header_140008);
	extract(out_header_70004);
	extract(out_header_130004);
	extract(out_header_70012);
	return parse_ethernet;
}

header_type out_header_140032_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_140032_t out_header_140032;

field_list copy_to_cpu_fields_140032{
	standard_metadata;
	hash_meta_reduce_3_140032;
	meta_reduce_3_140032;
	meta_map_init_140032;
	meta_fm;
}

action do_copy_to_cpu_140032() {
	clone_ingress_pkt_to_egress(140232, copy_to_cpu_fields_140032);
}

table copy_to_cpu_140032 {
	actions {do_copy_to_cpu_140032;}
	size : 1;
}

table encap_140032 {
	actions { do_encap_140032; }
	size : 1;
}

action do_encap_140032() {
	add_header(out_header_140032);
	modify_field(out_header_140032.qid, meta_reduce_3_140032.qid);
	modify_field(out_header_140032.dIP, meta_map_init_140032.dIP);
	modify_field(out_header_140032.count, meta_reduce_3_140032.val);
}

header_type out_header_20032_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_20032_t out_header_20032;

field_list copy_to_cpu_fields_20032{
	standard_metadata;
	hash_meta_reduce_4_20032;
	meta_reduce_4_20032;
	meta_map_init_20032;
	meta_fm;
}

action do_copy_to_cpu_20032() {
	clone_ingress_pkt_to_egress(20232, copy_to_cpu_fields_20032);
}

table copy_to_cpu_20032 {
	actions {do_copy_to_cpu_20032;}
	size : 1;
}

table encap_20032 {
	actions { do_encap_20032; }
	size : 1;
}

action do_encap_20032() {
	add_header(out_header_20032);
	modify_field(out_header_20032.qid, meta_reduce_4_20032.qid);
	modify_field(out_header_20032.sIP, meta_map_init_20032.sIP);
	modify_field(out_header_20032.count, meta_reduce_4_20032.val);
}

header_type out_header_80004_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_80004_t out_header_80004;

field_list copy_to_cpu_fields_80004{
	standard_metadata;
	hash_meta_reduce_4_80004;
	meta_reduce_4_80004;
	meta_map_init_80004;
	meta_fm;
}

action do_copy_to_cpu_80004() {
	clone_ingress_pkt_to_egress(80204, copy_to_cpu_fields_80004);
}

table copy_to_cpu_80004 {
	actions {do_copy_to_cpu_80004;}
	size : 1;
}

table encap_80004 {
	actions { do_encap_80004; }
	size : 1;
}

action do_encap_80004() {
	add_header(out_header_80004);
	modify_field(out_header_80004.qid, meta_reduce_4_80004.qid);
	modify_field(out_header_80004.sIP, meta_map_init_80004.sIP);
	modify_field(out_header_80004.count, meta_reduce_4_80004.val);
}

header_type out_header_20012_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_20012_t out_header_20012;

field_list copy_to_cpu_fields_20012{
	standard_metadata;
	hash_meta_reduce_3_20012;
	meta_reduce_3_20012;
	meta_map_init_20012;
	meta_fm;
}

action do_copy_to_cpu_20012() {
	clone_ingress_pkt_to_egress(20212, copy_to_cpu_fields_20012);
}

table copy_to_cpu_20012 {
	actions {do_copy_to_cpu_20012;}
	size : 1;
}

table encap_20012 {
	actions { do_encap_20012; }
	size : 1;
}

action do_encap_20012() {
	add_header(out_header_20012);
	modify_field(out_header_20012.qid, meta_reduce_3_20012.qid);
	modify_field(out_header_20012.sIP, meta_map_init_20012.sIP);
	modify_field(out_header_20012.count, meta_reduce_3_20012.val);
}

header_type out_header_80012_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_80012_t out_header_80012;

field_list copy_to_cpu_fields_80012{
	standard_metadata;
	hash_meta_reduce_5_80012;
	meta_reduce_5_80012;
	meta_map_init_80012;
	meta_fm;
}

action do_copy_to_cpu_80012() {
	clone_ingress_pkt_to_egress(80212, copy_to_cpu_fields_80012);
}

table copy_to_cpu_80012 {
	actions {do_copy_to_cpu_80012;}
	size : 1;
}

table encap_80012 {
	actions { do_encap_80012; }
	size : 1;
}

action do_encap_80012() {
	add_header(out_header_80012);
	modify_field(out_header_80012.qid, meta_reduce_5_80012.qid);
	modify_field(out_header_80012.sIP, meta_map_init_80012.sIP);
	modify_field(out_header_80012.count, meta_reduce_5_80012.val);
}

header_type out_header_70032_t {
	fields {
		qid : 16;
		sIP : 32;}
}

header out_header_70032_t out_header_70032;

field_list copy_to_cpu_fields_70032{
	standard_metadata;
	meta_map_init_70032;
	meta_fm;
}

action do_copy_to_cpu_70032() {
	clone_ingress_pkt_to_egress(70232, copy_to_cpu_fields_70032);
}

table copy_to_cpu_70032 {
	actions {do_copy_to_cpu_70032;}
	size : 1;
}

table encap_70032 {
	actions { do_encap_70032; }
	size : 1;
}

action do_encap_70032() {
	add_header(out_header_70032);
	modify_field(out_header_70032.qid, meta_map_init_70032.qid);
	modify_field(out_header_70032.sIP, meta_map_init_70032.sIP);
}

header_type out_header_10012_t {
	fields {
		qid : 16;
		sIP : 32;}
}

header out_header_10012_t out_header_10012;

field_list copy_to_cpu_fields_10012{
	standard_metadata;
	hash_meta_distinct_3_10012;
	meta_distinct_3_10012;
	meta_map_init_10012;
	meta_fm;
}

action do_copy_to_cpu_10012() {
	clone_ingress_pkt_to_egress(10212, copy_to_cpu_fields_10012);
}

table copy_to_cpu_10012 {
	actions {do_copy_to_cpu_10012;}
	size : 1;
}

table encap_10012 {
	actions { do_encap_10012; }
	size : 1;
}

action do_encap_10012() {
	add_header(out_header_10012);
	modify_field(out_header_10012.qid, meta_distinct_3_10012.qid);
	modify_field(out_header_10012.sIP, meta_map_init_10012.sIP);
}

header_type out_header_80032_t {
	fields {
		qid : 16;
		sIP : 32;
		dIP : 32;
		nBytes : 16;
		dMac : 48;
		sMac : 48;
		proto : 16;
		count : 16;
	}
}

header out_header_80032_t out_header_80032;

field_list copy_to_cpu_fields_80032{
	standard_metadata;
	hash_meta_reduce_3_80032;
	meta_reduce_3_80032;
	meta_map_init_80032;
	meta_fm;
}

action do_copy_to_cpu_80032() {
	clone_ingress_pkt_to_egress(80232, copy_to_cpu_fields_80032);
}

table copy_to_cpu_80032 {
	actions {do_copy_to_cpu_80032;}
	size : 1;
}

table encap_80032 {
	actions { do_encap_80032; }
	size : 1;
}

action do_encap_80032() {
	add_header(out_header_80032);
	modify_field(out_header_80032.qid, meta_reduce_3_80032.qid);
	modify_field(out_header_80032.sIP, meta_map_init_80032.sIP);
	modify_field(out_header_80032.dIP, meta_map_init_80032.dIP);
	modify_field(out_header_80032.nBytes, meta_map_init_80032.nBytes);
	modify_field(out_header_80032.dMac, meta_map_init_80032.dMac);
	modify_field(out_header_80032.sMac, meta_map_init_80032.sMac);
	modify_field(out_header_80032.proto, meta_map_init_80032.proto);
	modify_field(out_header_80032.count, meta_reduce_3_80032.val);
}

header_type out_header_50032_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_50032_t out_header_50032;

field_list copy_to_cpu_fields_50032{
	standard_metadata;
	hash_meta_reduce_3_50032;
	meta_reduce_3_50032;
	meta_map_init_50032;
	meta_fm;
}

action do_copy_to_cpu_50032() {
	clone_ingress_pkt_to_egress(50232, copy_to_cpu_fields_50032);
}

table copy_to_cpu_50032 {
	actions {do_copy_to_cpu_50032;}
	size : 1;
}

table encap_50032 {
	actions { do_encap_50032; }
	size : 1;
}

action do_encap_50032() {
	add_header(out_header_50032);
	modify_field(out_header_50032.qid, meta_reduce_3_50032.qid);
	modify_field(out_header_50032.sIP, meta_map_init_50032.sIP);
	modify_field(out_header_50032.count, meta_reduce_3_50032.val);
}

header_type out_header_100004_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_100004_t out_header_100004;

field_list copy_to_cpu_fields_100004{
	standard_metadata;
	hash_meta_distinct_3_100004;
	meta_distinct_3_100004;
	meta_map_init_100004;
	meta_fm;
}

action do_copy_to_cpu_100004() {
	clone_ingress_pkt_to_egress(100204, copy_to_cpu_fields_100004);
}

table copy_to_cpu_100004 {
	actions {do_copy_to_cpu_100004;}
	size : 1;
}

table encap_100004 {
	actions { do_encap_100004; }
	size : 1;
}

action do_encap_100004() {
	add_header(out_header_100004);
	modify_field(out_header_100004.qid, meta_distinct_3_100004.qid);
	modify_field(out_header_100004.dIP, meta_map_init_100004.dIP);
}

header_type out_header_80028_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_80028_t out_header_80028;

field_list copy_to_cpu_fields_80028{
	standard_metadata;
	hash_meta_reduce_5_80028;
	meta_reduce_5_80028;
	meta_map_init_80028;
	meta_fm;
}

action do_copy_to_cpu_80028() {
	clone_ingress_pkt_to_egress(80228, copy_to_cpu_fields_80028);
}

table copy_to_cpu_80028 {
	actions {do_copy_to_cpu_80028;}
	size : 1;
}

table encap_80028 {
	actions { do_encap_80028; }
	size : 1;
}

action do_encap_80028() {
	add_header(out_header_80028);
	modify_field(out_header_80028.qid, meta_reduce_5_80028.qid);
	modify_field(out_header_80028.sIP, meta_map_init_80028.sIP);
	modify_field(out_header_80028.count, meta_reduce_5_80028.val);
}

header_type out_header_100012_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_100012_t out_header_100012;

field_list copy_to_cpu_fields_100012{
	standard_metadata;
	hash_meta_distinct_3_100012;
	meta_distinct_3_100012;
	meta_map_init_100012;
	meta_fm;
}

action do_copy_to_cpu_100012() {
	clone_ingress_pkt_to_egress(100212, copy_to_cpu_fields_100012);
}

table copy_to_cpu_100012 {
	actions {do_copy_to_cpu_100012;}
	size : 1;
}

table encap_100012 {
	actions { do_encap_100012; }
	size : 1;
}

action do_encap_100012() {
	add_header(out_header_100012);
	modify_field(out_header_100012.qid, meta_distinct_3_100012.qid);
	modify_field(out_header_100012.dIP, meta_map_init_100012.dIP);
}

header_type out_header_10032_t {
	fields {
		qid : 16;
		sIP : 32;}
}

header out_header_10032_t out_header_10032;

field_list copy_to_cpu_fields_10032{
	standard_metadata;
	hash_meta_distinct_3_10032;
	meta_distinct_3_10032;
	meta_map_init_10032;
	meta_fm;
}

action do_copy_to_cpu_10032() {
	clone_ingress_pkt_to_egress(10232, copy_to_cpu_fields_10032);
}

table copy_to_cpu_10032 {
	actions {do_copy_to_cpu_10032;}
	size : 1;
}

table encap_10032 {
	actions { do_encap_10032; }
	size : 1;
}

action do_encap_10032() {
	add_header(out_header_10032);
	modify_field(out_header_10032.qid, meta_distinct_3_10032.qid);
	modify_field(out_header_10032.sIP, meta_map_init_10032.sIP);
}

header_type out_header_110004_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_110004_t out_header_110004;

field_list copy_to_cpu_fields_110004{
	standard_metadata;
	hash_meta_reduce_4_110004;
	meta_reduce_4_110004;
	meta_map_init_110004;
	meta_fm;
}

action do_copy_to_cpu_110004() {
	clone_ingress_pkt_to_egress(110204, copy_to_cpu_fields_110004);
}

table copy_to_cpu_110004 {
	actions {do_copy_to_cpu_110004;}
	size : 1;
}

table encap_110004 {
	actions { do_encap_110004; }
	size : 1;
}

action do_encap_110004() {
	add_header(out_header_110004);
	modify_field(out_header_110004.qid, meta_reduce_4_110004.qid);
	modify_field(out_header_110004.dIP, meta_map_init_110004.dIP);
	modify_field(out_header_110004.count, meta_reduce_4_110004.val);
}

header_type out_header_110012_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_110012_t out_header_110012;

field_list copy_to_cpu_fields_110012{
	standard_metadata;
	hash_meta_reduce_5_110012;
	meta_reduce_5_110012;
	meta_map_init_110012;
	meta_fm;
}

action do_copy_to_cpu_110012() {
	clone_ingress_pkt_to_egress(110212, copy_to_cpu_fields_110012);
}

table copy_to_cpu_110012 {
	actions {do_copy_to_cpu_110012;}
	size : 1;
}

table encap_110012 {
	actions { do_encap_110012; }
	size : 1;
}

action do_encap_110012() {
	add_header(out_header_110012);
	modify_field(out_header_110012.qid, meta_reduce_5_110012.qid);
	modify_field(out_header_110012.dIP, meta_map_init_110012.dIP);
	modify_field(out_header_110012.count, meta_reduce_5_110012.val);
}

header_type out_header_100032_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_100032_t out_header_100032;

field_list copy_to_cpu_fields_100032{
	standard_metadata;
	meta_map_init_100032;
	meta_fm;
}

action do_copy_to_cpu_100032() {
	clone_ingress_pkt_to_egress(100232, copy_to_cpu_fields_100032);
}

table copy_to_cpu_100032 {
	actions {do_copy_to_cpu_100032;}
	size : 1;
}

table encap_100032 {
	actions { do_encap_100032; }
	size : 1;
}

action do_encap_100032() {
	add_header(out_header_100032);
	modify_field(out_header_100032.qid, meta_map_init_100032.qid);
	modify_field(out_header_100032.dIP, meta_map_init_100032.dIP);
}

header_type out_header_40004_t {
	fields {
		qid : 16;
		sIP : 32;
		dPort : 16;
		sMac : 48;
		proto : 16;
		dMac : 48;
		dIP : 32;
		nBytes : 16;}
}

header out_header_40004_t out_header_40004;

field_list copy_to_cpu_fields_40004{
	standard_metadata;
	hash_meta_distinct_3_40004;
	meta_distinct_3_40004;
	meta_map_init_40004;
	meta_fm;
}

action do_copy_to_cpu_40004() {
	clone_ingress_pkt_to_egress(40204, copy_to_cpu_fields_40004);
}

table copy_to_cpu_40004 {
	actions {do_copy_to_cpu_40004;}
	size : 1;
}

table encap_40004 {
	actions { do_encap_40004; }
	size : 1;
}

action do_encap_40004() {
	add_header(out_header_40004);
	modify_field(out_header_40004.qid, meta_distinct_3_40004.qid);
	modify_field(out_header_40004.sIP, meta_map_init_40004.sIP);
	modify_field(out_header_40004.dPort, meta_map_init_40004.dPort);
	modify_field(out_header_40004.sMac, meta_map_init_40004.sMac);
	modify_field(out_header_40004.proto, meta_map_init_40004.proto);
	modify_field(out_header_40004.dMac, meta_map_init_40004.dMac);
	modify_field(out_header_40004.dIP, meta_map_init_40004.dIP);
	modify_field(out_header_40004.nBytes, meta_map_init_40004.nBytes);
}

header_type out_header_40012_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_40012_t out_header_40012;

field_list copy_to_cpu_fields_40012{
	standard_metadata;
	hash_meta_reduce_5_40012;
	meta_reduce_5_40012;
	meta_map_init_40012;
	meta_fm;
}

action do_copy_to_cpu_40012() {
	clone_ingress_pkt_to_egress(40212, copy_to_cpu_fields_40012);
}

table copy_to_cpu_40012 {
	actions {do_copy_to_cpu_40012;}
	size : 1;
}

table encap_40012 {
	actions { do_encap_40012; }
	size : 1;
}

action do_encap_40012() {
	add_header(out_header_40012);
	modify_field(out_header_40012.qid, meta_reduce_5_40012.qid);
	modify_field(out_header_40012.sIP, meta_map_init_40012.sIP);
	modify_field(out_header_40012.count, meta_reduce_5_40012.val);
}

header_type out_header_110028_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_110028_t out_header_110028;

field_list copy_to_cpu_fields_110028{
	standard_metadata;
	hash_meta_reduce_5_110028;
	meta_reduce_5_110028;
	meta_map_init_110028;
	meta_fm;
}

action do_copy_to_cpu_110028() {
	clone_ingress_pkt_to_egress(110228, copy_to_cpu_fields_110028);
}

table copy_to_cpu_110028 {
	actions {do_copy_to_cpu_110028;}
	size : 1;
}

table encap_110028 {
	actions { do_encap_110028; }
	size : 1;
}

action do_encap_110028() {
	add_header(out_header_110028);
	modify_field(out_header_110028.qid, meta_reduce_5_110028.qid);
	modify_field(out_header_110028.dIP, meta_map_init_110028.dIP);
	modify_field(out_header_110028.count, meta_reduce_5_110028.val);
}

header_type out_header_110032_t {
	fields {
		qid : 16;
		dPort : 16;
		dMac : 48;
		sPort : 16;
		dIP : 32;}
}

header out_header_110032_t out_header_110032;

field_list copy_to_cpu_fields_110032{
	standard_metadata;
	meta_map_init_110032;
	meta_fm;
}

action do_copy_to_cpu_110032() {
	clone_ingress_pkt_to_egress(110232, copy_to_cpu_fields_110032);
}

table copy_to_cpu_110032 {
	actions {do_copy_to_cpu_110032;}
	size : 1;
}

table encap_110032 {
	actions { do_encap_110032; }
	size : 1;
}

action do_encap_110032() {
	add_header(out_header_110032);
	modify_field(out_header_110032.qid, meta_map_init_110032.qid);
	modify_field(out_header_110032.dPort, meta_map_init_110032.dPort);
	modify_field(out_header_110032.dMac, meta_map_init_110032.dMac);
	modify_field(out_header_110032.sPort, meta_map_init_110032.sPort);
	modify_field(out_header_110032.dIP, meta_map_init_110032.dIP);
}

header_type out_header_50004_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_50004_t out_header_50004;

field_list copy_to_cpu_fields_50004{
	standard_metadata;
	hash_meta_reduce_2_50004;
	meta_reduce_2_50004;
	meta_map_init_50004;
	meta_fm;
}

action do_copy_to_cpu_50004() {
	clone_ingress_pkt_to_egress(50204, copy_to_cpu_fields_50004);
}

table copy_to_cpu_50004 {
	actions {do_copy_to_cpu_50004;}
	size : 1;
}

table encap_50004 {
	actions { do_encap_50004; }
	size : 1;
}

action do_encap_50004() {
	add_header(out_header_50004);
	modify_field(out_header_50004.qid, meta_reduce_2_50004.qid);
	modify_field(out_header_50004.sIP, meta_map_init_50004.sIP);
	modify_field(out_header_50004.count, meta_reduce_2_50004.val);
}

header_type out_header_130012_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_130012_t out_header_130012;

field_list copy_to_cpu_fields_130012{
	standard_metadata;
	meta_map_init_130012;
	meta_fm;
}

action do_copy_to_cpu_130012() {
	clone_ingress_pkt_to_egress(130212, copy_to_cpu_fields_130012);
}

table copy_to_cpu_130012 {
	actions {do_copy_to_cpu_130012;}
	size : 1;
}

table encap_130012 {
	actions { do_encap_130012; }
	size : 1;
}

action do_encap_130012() {
	add_header(out_header_130012);
	modify_field(out_header_130012.qid, meta_map_init_130012.qid);
	modify_field(out_header_130012.dIP, meta_map_init_130012.dIP);
}

header_type out_header_40032_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_40032_t out_header_40032;

field_list copy_to_cpu_fields_40032{
	standard_metadata;
	hash_meta_reduce_5_40032;
	meta_reduce_5_40032;
	meta_map_init_40032;
	meta_fm;
}

action do_copy_to_cpu_40032() {
	clone_ingress_pkt_to_egress(40232, copy_to_cpu_fields_40032);
}

table copy_to_cpu_40032 {
	actions {do_copy_to_cpu_40032;}
	size : 1;
}

table encap_40032 {
	actions { do_encap_40032; }
	size : 1;
}

action do_encap_40032() {
	add_header(out_header_40032);
	modify_field(out_header_40032.qid, meta_reduce_5_40032.qid);
	modify_field(out_header_40032.sIP, meta_map_init_40032.sIP);
	modify_field(out_header_40032.count, meta_reduce_5_40032.val);
}

header_type out_header_140004_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_140004_t out_header_140004;

field_list copy_to_cpu_fields_140004{
	standard_metadata;
	hash_meta_reduce_2_140004;
	meta_reduce_2_140004;
	meta_map_init_140004;
	meta_fm;
}

action do_copy_to_cpu_140004() {
	clone_ingress_pkt_to_egress(140204, copy_to_cpu_fields_140004);
}

table copy_to_cpu_140004 {
	actions {do_copy_to_cpu_140004;}
	size : 1;
}

table encap_140004 {
	actions { do_encap_140004; }
	size : 1;
}

action do_encap_140004() {
	add_header(out_header_140004);
	modify_field(out_header_140004.qid, meta_reduce_2_140004.qid);
	modify_field(out_header_140004.dIP, meta_map_init_140004.dIP);
	modify_field(out_header_140004.count, meta_reduce_2_140004.val);
}

header_type out_header_50012_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_50012_t out_header_50012;

field_list copy_to_cpu_fields_50012{
	standard_metadata;
	hash_meta_reduce_3_50012;
	meta_reduce_3_50012;
	meta_map_init_50012;
	meta_fm;
}

action do_copy_to_cpu_50012() {
	clone_ingress_pkt_to_egress(50212, copy_to_cpu_fields_50012);
}

table copy_to_cpu_50012 {
	actions {do_copy_to_cpu_50012;}
	size : 1;
}

table encap_50012 {
	actions { do_encap_50012; }
	size : 1;
}

action do_encap_50012() {
	add_header(out_header_50012);
	modify_field(out_header_50012.qid, meta_reduce_3_50012.qid);
	modify_field(out_header_50012.sIP, meta_map_init_50012.sIP);
	modify_field(out_header_50012.count, meta_reduce_3_50012.val);
}

header_type out_header_140012_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_140012_t out_header_140012;

field_list copy_to_cpu_fields_140012{
	standard_metadata;
	meta_map_init_140012;
	meta_fm;
}

action do_copy_to_cpu_140012() {
	clone_ingress_pkt_to_egress(140212, copy_to_cpu_fields_140012);
}

table copy_to_cpu_140012 {
	actions {do_copy_to_cpu_140012;}
	size : 1;
}

table encap_140012 {
	actions { do_encap_140012; }
	size : 1;
}

action do_encap_140012() {
	add_header(out_header_140012);
	modify_field(out_header_140012.qid, meta_map_init_140012.qid);
	modify_field(out_header_140012.dIP, meta_map_init_140012.dIP);
}

header_type out_header_130032_t {
	fields {
		qid : 16;
		dIP : 32;}
}

header out_header_130032_t out_header_130032;

field_list copy_to_cpu_fields_130032{
	standard_metadata;
	meta_map_init_130032;
	meta_fm;
}

action do_copy_to_cpu_130032() {
	clone_ingress_pkt_to_egress(130232, copy_to_cpu_fields_130032);
}

table copy_to_cpu_130032 {
	actions {do_copy_to_cpu_130032;}
	size : 1;
}

table encap_130032 {
	actions { do_encap_130032; }
	size : 1;
}

action do_encap_130032() {
	add_header(out_header_130032);
	modify_field(out_header_130032.qid, meta_map_init_130032.qid);
	modify_field(out_header_130032.dIP, meta_map_init_130032.dIP);
}

header_type out_header_140008_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_140008_t out_header_140008;

field_list copy_to_cpu_fields_140008{
	standard_metadata;
	hash_meta_reduce_3_140008;
	meta_reduce_3_140008;
	meta_map_init_140008;
	meta_fm;
}

action do_copy_to_cpu_140008() {
	clone_ingress_pkt_to_egress(140208, copy_to_cpu_fields_140008);
}

table copy_to_cpu_140008 {
	actions {do_copy_to_cpu_140008;}
	size : 1;
}

table encap_140008 {
	actions { do_encap_140008; }
	size : 1;
}

action do_encap_140008() {
	add_header(out_header_140008);
	modify_field(out_header_140008.qid, meta_reduce_3_140008.qid);
	modify_field(out_header_140008.dIP, meta_map_init_140008.dIP);
	modify_field(out_header_140008.count, meta_reduce_3_140008.val);
}

header_type out_header_70004_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_70004_t out_header_70004;

field_list copy_to_cpu_fields_70004{
	standard_metadata;
	hash_meta_reduce_3_70004;
	meta_reduce_3_70004;
	meta_map_init_70004;
	meta_fm;
}

action do_copy_to_cpu_70004() {
	clone_ingress_pkt_to_egress(70204, copy_to_cpu_fields_70004);
}

table copy_to_cpu_70004 {
	actions {do_copy_to_cpu_70004;}
	size : 1;
}

table encap_70004 {
	actions { do_encap_70004; }
	size : 1;
}

action do_encap_70004() {
	add_header(out_header_70004);
	modify_field(out_header_70004.qid, meta_reduce_3_70004.qid);
	modify_field(out_header_70004.sIP, meta_map_init_70004.sIP);
	modify_field(out_header_70004.count, meta_reduce_3_70004.val);
}

header_type out_header_130004_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_130004_t out_header_130004;

field_list copy_to_cpu_fields_130004{
	standard_metadata;
	hash_meta_reduce_3_130004;
	meta_reduce_3_130004;
	meta_map_init_130004;
	meta_fm;
}

action do_copy_to_cpu_130004() {
	clone_ingress_pkt_to_egress(130204, copy_to_cpu_fields_130004);
}

table copy_to_cpu_130004 {
	actions {do_copy_to_cpu_130004;}
	size : 1;
}

table encap_130004 {
	actions { do_encap_130004; }
	size : 1;
}

action do_encap_130004() {
	add_header(out_header_130004);
	modify_field(out_header_130004.qid, meta_reduce_3_130004.qid);
	modify_field(out_header_130004.dIP, meta_map_init_130004.dIP);
	modify_field(out_header_130004.count, meta_reduce_3_130004.val);
}

header_type out_header_70012_t {
	fields {
		qid : 16;
		sIP : 32;
		count : 16;
	}
}

header out_header_70012_t out_header_70012;

field_list copy_to_cpu_fields_70012{
	standard_metadata;
	hash_meta_reduce_3_70012;
	meta_reduce_3_70012;
	meta_map_init_70012;
	meta_fm;
}

action do_copy_to_cpu_70012() {
	clone_ingress_pkt_to_egress(70212, copy_to_cpu_fields_70012);
}

table copy_to_cpu_70012 {
	actions {do_copy_to_cpu_70012;}
	size : 1;
}

table encap_70012 {
	actions { do_encap_70012; }
	size : 1;
}

action do_encap_70012() {
	add_header(out_header_70012);
	modify_field(out_header_70012.qid, meta_reduce_3_70012.qid);
	modify_field(out_header_70012.sIP, meta_map_init_70012.sIP);
	modify_field(out_header_70012.count, meta_reduce_3_70012.val);
}

table skip_reduce_3_140032_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_140032_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_20032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_20032_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_20032_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_20032_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_20032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_2_80004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_2_80004_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_80004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_80004_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_80004_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_80004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_80004_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_2_20012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_20012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_20012_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_20012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_20012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_80012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_80012_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_4_80012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_4_80012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_4_80012_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_80012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_80012_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_10012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_10012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_10012_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_80032_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_80032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_50032_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_50032_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_100004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_100004_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_100004_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_80028_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_80028_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_4_80028_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_4_80028_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_4_80028_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_80028_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_80028_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_100012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_100012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_100012_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_10032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_10032_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_10032_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_2_110004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_110004_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_110004_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_110004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_110004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_110004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_110004_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_110012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_110012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_110012_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_110012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_110012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_110012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_110012_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_40004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_40004_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_40004_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_40012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_40012_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_40012_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_40012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_40012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_40012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_40012_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_110028_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_110028_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_110028_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_110028_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_110028_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_110028_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_110028_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_2_50004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_2_50004_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_40032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_40032_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_40032_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_40032_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_40032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_5_40032_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_5_40032_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_2_140004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_2_140004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_50012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_50012_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_140008_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_140008_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_70004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_70004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_130004_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_130004_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_70012_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_70012_1 {
	actions {mark_drop;}
	size : 1;
}

table map_init_140032{
	actions{
		do_map_init_140032;
	}
}

action do_map_init_140032(){
	modify_field(meta_map_init_140032.qid, 140032);
	modify_field(meta_map_init_140032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_140032_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_140032_t meta_map_init_140032;

table map_140032_2{
	actions{
		do_map_140032_2;
	}
}

action do_map_140032_2() {
	bit_and(meta_map_init_140032.dIP, meta_map_init_140032.dIP, 0xffffffff);
}

header_type meta_reduce_3_140032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_140032_t meta_reduce_3_140032;

header_type hash_meta_reduce_3_140032_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_140032_t hash_meta_reduce_3_140032;

field_list reduce_3_140032_fields {
	hash_meta_reduce_3_140032.dIP;
}

field_list_calculation reduce_3_140032_fields_hash {
	input {
		reduce_3_140032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_140032{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_140032_regs() {
	add_to_field(meta_reduce_3_140032.val, 1);
	register_write(reduce_3_140032,meta_reduce_3_140032.idx,meta_reduce_3_140032.val);
}

table update_reduce_3_140032_counts {
	actions {update_reduce_3_140032_regs;}
	size : 1;
}

action do_reduce_3_140032_hashes() {
	modify_field(hash_meta_reduce_3_140032.dIP, meta_map_init_140032.dIP);
	modify_field(meta_reduce_3_140032.qid, 140032);
	modify_field_with_hash_based_offset(meta_reduce_3_140032.idx, 0, reduce_3_140032_fields_hash, 4096);
	register_read(meta_reduce_3_140032.val, reduce_3_140032, meta_reduce_3_140032.idx);
}

table start_reduce_3_140032 {
	actions {do_reduce_3_140032_hashes;}
	size : 1;
}

action set_reduce_3_140032_count() {
	modify_field(meta_reduce_3_140032.val, 1);
}

table set_reduce_3_140032_count {
	actions {set_reduce_3_140032_count;}
        size: 1;
}

table map_init_20032{
	actions{
		do_map_init_20032;
	}
}

action do_map_init_20032(){
	modify_field(meta_map_init_20032.qid, 20032);
	modify_field(meta_map_init_20032.dPort, tcp.dstPort);
	modify_field(meta_map_init_20032.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_20032.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20032.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_20032.nBytes, ipv4.totalLen);
}

header_type meta_map_init_20032_t {
	 fields {
		qid: 16;
		dPort: 16;
		dMac: 48;
		sIP: 32;
		dIP: 32;
		nBytes: 16;
	}
}

metadata meta_map_init_20032_t meta_map_init_20032;

table map_20032_2{
	actions{
		do_map_20032_2;
	}
}

action do_map_20032_2() {
	bit_and(meta_map_init_20032.sIP, meta_map_init_20032.sIP, 0xffffffff);
}

header_type meta_distinct_3_20032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_20032_t meta_distinct_3_20032;

header_type hash_meta_distinct_3_20032_t {
	fields {
		dPort : 16;
		dMac : 48;
		sIP : 32;
		dIP : 32;
		nBytes : 16;
	}
}

metadata hash_meta_distinct_3_20032_t hash_meta_distinct_3_20032;

field_list distinct_3_20032_fields {
	hash_meta_distinct_3_20032.dPort;
	hash_meta_distinct_3_20032.dMac;
	hash_meta_distinct_3_20032.sIP;
	hash_meta_distinct_3_20032.dIP;
	hash_meta_distinct_3_20032.nBytes;
}

field_list_calculation distinct_3_20032_fields_hash {
	input {
		distinct_3_20032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_20032{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_20032_regs() {
	bit_or(meta_distinct_3_20032.val,meta_distinct_3_20032.val, 1);
	register_write(distinct_3_20032,meta_distinct_3_20032.idx,meta_distinct_3_20032.val);
}

table update_distinct_3_20032_counts {
	actions {update_distinct_3_20032_regs;}
	size : 1;
}

action do_distinct_3_20032_hashes() {
	modify_field(hash_meta_distinct_3_20032.dPort, meta_map_init_20032.dPort);
	modify_field(hash_meta_distinct_3_20032.dMac, meta_map_init_20032.dMac);
	modify_field(hash_meta_distinct_3_20032.sIP, meta_map_init_20032.sIP);
	modify_field(hash_meta_distinct_3_20032.dIP, meta_map_init_20032.dIP);
	modify_field(hash_meta_distinct_3_20032.nBytes, meta_map_init_20032.nBytes);
	modify_field(meta_distinct_3_20032.qid, 20032);
	modify_field_with_hash_based_offset(meta_distinct_3_20032.idx, 0, distinct_3_20032_fields_hash, 4096);
	register_read(meta_distinct_3_20032.val, distinct_3_20032, meta_distinct_3_20032.idx);
}

table start_distinct_3_20032 {
	actions {do_distinct_3_20032_hashes;}
	size : 1;
}

action set_distinct_3_20032_count() {
	modify_field(meta_distinct_3_20032.val, 1);
}

table set_distinct_3_20032_count {
	actions {set_distinct_3_20032_count;}
        size: 1;
}

header_type meta_reduce_4_20032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_20032_t meta_reduce_4_20032;

header_type hash_meta_reduce_4_20032_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_4_20032_t hash_meta_reduce_4_20032;

field_list reduce_4_20032_fields {
	hash_meta_reduce_4_20032.sIP;
}

field_list_calculation reduce_4_20032_fields_hash {
	input {
		reduce_4_20032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_20032{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_20032_regs() {
	add_to_field(meta_reduce_4_20032.val, 1);
	register_write(reduce_4_20032,meta_reduce_4_20032.idx,meta_reduce_4_20032.val);
}

table update_reduce_4_20032_counts {
	actions {update_reduce_4_20032_regs;}
	size : 1;
}

action do_reduce_4_20032_hashes() {
	modify_field(hash_meta_reduce_4_20032.sIP, meta_map_init_20032.sIP);
	modify_field(meta_reduce_4_20032.qid, 20032);
	modify_field_with_hash_based_offset(meta_reduce_4_20032.idx, 0, reduce_4_20032_fields_hash, 4096);
	register_read(meta_reduce_4_20032.val, reduce_4_20032, meta_reduce_4_20032.idx);
}

table start_reduce_4_20032 {
	actions {do_reduce_4_20032_hashes;}
	size : 1;
}

action set_reduce_4_20032_count() {
	modify_field(meta_reduce_4_20032.val, 1);
}

table set_reduce_4_20032_count {
	actions {set_reduce_4_20032_count;}
        size: 1;
}

table map_init_80004{
	actions{
		do_map_init_80004;
	}
}

action do_map_init_80004(){
	modify_field(meta_map_init_80004.qid, 80004);
	modify_field(meta_map_init_80004.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_80004.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_80004.proto, ipv4.protocol);
	modify_field(meta_map_init_80004.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_80004.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_80004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_80004_t {
	 fields {
		qid: 16;
		dMac: 48;
		sIP: 32;
		proto: 16;
		sMac: 48;
		nBytes: 16;
		dIP: 32;
	}
}

metadata meta_map_init_80004_t meta_map_init_80004;

table map_80004_1{
	actions{
		do_map_80004_1;
	}
}

action do_map_80004_1() {
	bit_and(meta_map_init_80004.sIP, meta_map_init_80004.sIP, 0xf0000000);
}

header_type meta_reduce_2_80004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_80004_t meta_reduce_2_80004;

header_type hash_meta_reduce_2_80004_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_2_80004_t hash_meta_reduce_2_80004;

field_list reduce_2_80004_fields {
	hash_meta_reduce_2_80004.dMac;
	hash_meta_reduce_2_80004.sIP;
	hash_meta_reduce_2_80004.proto;
	hash_meta_reduce_2_80004.sMac;
	hash_meta_reduce_2_80004.nBytes;
	hash_meta_reduce_2_80004.dIP;
}

field_list_calculation reduce_2_80004_fields_hash {
	input {
		reduce_2_80004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_2_80004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_2_80004_regs() {
	add_to_field(meta_reduce_2_80004.val, 1);
	register_write(reduce_2_80004,meta_reduce_2_80004.idx,meta_reduce_2_80004.val);
}

table update_reduce_2_80004_counts {
	actions {update_reduce_2_80004_regs;}
	size : 1;
}

action do_reduce_2_80004_hashes() {
	modify_field(hash_meta_reduce_2_80004.dMac, meta_map_init_80004.dMac);
	modify_field(hash_meta_reduce_2_80004.sIP, meta_map_init_80004.sIP);
	modify_field(hash_meta_reduce_2_80004.proto, meta_map_init_80004.proto);
	modify_field(hash_meta_reduce_2_80004.sMac, meta_map_init_80004.sMac);
	modify_field(hash_meta_reduce_2_80004.nBytes, meta_map_init_80004.nBytes);
	modify_field(hash_meta_reduce_2_80004.dIP, meta_map_init_80004.dIP);
	modify_field(meta_reduce_2_80004.qid, 80004);
	modify_field_with_hash_based_offset(meta_reduce_2_80004.idx, 0, reduce_2_80004_fields_hash, 4096);
	register_read(meta_reduce_2_80004.val, reduce_2_80004, meta_reduce_2_80004.idx);
}

table start_reduce_2_80004 {
	actions {do_reduce_2_80004_hashes;}
	size : 1;
}

action set_reduce_2_80004_count() {
	modify_field(meta_reduce_2_80004.val, 1);
}

table set_reduce_2_80004_count {
	actions {set_reduce_2_80004_count;}
        size: 1;
}

header_type meta_distinct_3_80004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_80004_t meta_distinct_3_80004;

header_type hash_meta_distinct_3_80004_t {
	fields {
		sMac : 48;
		dMac : 48;
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_80004_t hash_meta_distinct_3_80004;

field_list distinct_3_80004_fields {
	hash_meta_distinct_3_80004.sMac;
	hash_meta_distinct_3_80004.dMac;
	hash_meta_distinct_3_80004.sIP;
	hash_meta_distinct_3_80004.dIP;
}

field_list_calculation distinct_3_80004_fields_hash {
	input {
		distinct_3_80004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_80004{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_80004_regs() {
	bit_or(meta_distinct_3_80004.val,meta_distinct_3_80004.val, 1);
	register_write(distinct_3_80004,meta_distinct_3_80004.idx,meta_distinct_3_80004.val);
}

table update_distinct_3_80004_counts {
	actions {update_distinct_3_80004_regs;}
	size : 1;
}

action do_distinct_3_80004_hashes() {
	modify_field(hash_meta_distinct_3_80004.sMac, meta_map_init_80004.sMac);
	modify_field(hash_meta_distinct_3_80004.dMac, meta_map_init_80004.dMac);
	modify_field(hash_meta_distinct_3_80004.sIP, meta_map_init_80004.sIP);
	modify_field(hash_meta_distinct_3_80004.dIP, meta_map_init_80004.dIP);
	modify_field(meta_distinct_3_80004.qid, 80004);
	modify_field_with_hash_based_offset(meta_distinct_3_80004.idx, 0, distinct_3_80004_fields_hash, 4096);
	register_read(meta_distinct_3_80004.val, distinct_3_80004, meta_distinct_3_80004.idx);
}

table start_distinct_3_80004 {
	actions {do_distinct_3_80004_hashes;}
	size : 1;
}

action set_distinct_3_80004_count() {
	modify_field(meta_distinct_3_80004.val, 1);
}

table set_distinct_3_80004_count {
	actions {set_distinct_3_80004_count;}
        size: 1;
}

header_type meta_reduce_4_80004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_80004_t meta_reduce_4_80004;

header_type hash_meta_reduce_4_80004_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_4_80004_t hash_meta_reduce_4_80004;

field_list reduce_4_80004_fields {
	hash_meta_reduce_4_80004.sIP;
}

field_list_calculation reduce_4_80004_fields_hash {
	input {
		reduce_4_80004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_80004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_80004_regs() {
	add_to_field(meta_reduce_4_80004.val, 1);
	register_write(reduce_4_80004,meta_reduce_4_80004.idx,meta_reduce_4_80004.val);
}

table update_reduce_4_80004_counts {
	actions {update_reduce_4_80004_regs;}
	size : 1;
}

action do_reduce_4_80004_hashes() {
	modify_field(hash_meta_reduce_4_80004.sIP, meta_map_init_80004.sIP);
	modify_field(meta_reduce_4_80004.qid, 80004);
	modify_field_with_hash_based_offset(meta_reduce_4_80004.idx, 0, reduce_4_80004_fields_hash, 4096);
	register_read(meta_reduce_4_80004.val, reduce_4_80004, meta_reduce_4_80004.idx);
}

table start_reduce_4_80004 {
	actions {do_reduce_4_80004_hashes;}
	size : 1;
}

action set_reduce_4_80004_count() {
	modify_field(meta_reduce_4_80004.val, 1);
}

table set_reduce_4_80004_count {
	actions {set_reduce_4_80004_count;}
        size: 1;
}

table map_init_20012{
	actions{
		do_map_init_20012;
	}
}

action do_map_init_20012(){
	modify_field(meta_map_init_20012.qid, 20012);
	modify_field(meta_map_init_20012.dPort, tcp.dstPort);
	modify_field(meta_map_init_20012.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_20012.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_20012.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_20012.nBytes, ipv4.totalLen);
}

header_type meta_map_init_20012_t {
	 fields {
		qid: 16;
		dPort: 16;
		dMac: 48;
		sIP: 32;
		dIP: 32;
		nBytes: 16;
	}
}

metadata meta_map_init_20012_t meta_map_init_20012;

table map_20012_1{
	actions{
		do_map_20012_1;
	}
}

action do_map_20012_1() {
	bit_and(meta_map_init_20012.sIP, meta_map_init_20012.sIP, 0xfff00000);
}

header_type meta_distinct_2_20012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_20012_t meta_distinct_2_20012;

header_type hash_meta_distinct_2_20012_t {
	fields {
		dPort : 16;
		dMac : 48;
		sIP : 32;
		dIP : 32;
		nBytes : 16;
	}
}

metadata hash_meta_distinct_2_20012_t hash_meta_distinct_2_20012;

field_list distinct_2_20012_fields {
	hash_meta_distinct_2_20012.dPort;
	hash_meta_distinct_2_20012.dMac;
	hash_meta_distinct_2_20012.sIP;
	hash_meta_distinct_2_20012.dIP;
	hash_meta_distinct_2_20012.nBytes;
}

field_list_calculation distinct_2_20012_fields_hash {
	input {
		distinct_2_20012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_20012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_20012_regs() {
	bit_or(meta_distinct_2_20012.val,meta_distinct_2_20012.val, 1);
	register_write(distinct_2_20012,meta_distinct_2_20012.idx,meta_distinct_2_20012.val);
}

table update_distinct_2_20012_counts {
	actions {update_distinct_2_20012_regs;}
	size : 1;
}

action do_distinct_2_20012_hashes() {
	modify_field(hash_meta_distinct_2_20012.dPort, meta_map_init_20012.dPort);
	modify_field(hash_meta_distinct_2_20012.dMac, meta_map_init_20012.dMac);
	modify_field(hash_meta_distinct_2_20012.sIP, meta_map_init_20012.sIP);
	modify_field(hash_meta_distinct_2_20012.dIP, meta_map_init_20012.dIP);
	modify_field(hash_meta_distinct_2_20012.nBytes, meta_map_init_20012.nBytes);
	modify_field(meta_distinct_2_20012.qid, 20012);
	modify_field_with_hash_based_offset(meta_distinct_2_20012.idx, 0, distinct_2_20012_fields_hash, 4096);
	register_read(meta_distinct_2_20012.val, distinct_2_20012, meta_distinct_2_20012.idx);
}

table start_distinct_2_20012 {
	actions {do_distinct_2_20012_hashes;}
	size : 1;
}

action set_distinct_2_20012_count() {
	modify_field(meta_distinct_2_20012.val, 1);
}

table set_distinct_2_20012_count {
	actions {set_distinct_2_20012_count;}
        size: 1;
}

header_type meta_reduce_3_20012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_20012_t meta_reduce_3_20012;

header_type hash_meta_reduce_3_20012_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_3_20012_t hash_meta_reduce_3_20012;

field_list reduce_3_20012_fields {
	hash_meta_reduce_3_20012.sIP;
}

field_list_calculation reduce_3_20012_fields_hash {
	input {
		reduce_3_20012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_20012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_20012_regs() {
	add_to_field(meta_reduce_3_20012.val, 1);
	register_write(reduce_3_20012,meta_reduce_3_20012.idx,meta_reduce_3_20012.val);
}

table update_reduce_3_20012_counts {
	actions {update_reduce_3_20012_regs;}
	size : 1;
}

action do_reduce_3_20012_hashes() {
	modify_field(hash_meta_reduce_3_20012.sIP, meta_map_init_20012.sIP);
	modify_field(meta_reduce_3_20012.qid, 20012);
	modify_field_with_hash_based_offset(meta_reduce_3_20012.idx, 0, reduce_3_20012_fields_hash, 4096);
	register_read(meta_reduce_3_20012.val, reduce_3_20012, meta_reduce_3_20012.idx);
}

table start_reduce_3_20012 {
	actions {do_reduce_3_20012_hashes;}
	size : 1;
}

action set_reduce_3_20012_count() {
	modify_field(meta_reduce_3_20012.val, 1);
}

table set_reduce_3_20012_count {
	actions {set_reduce_3_20012_count;}
        size: 1;
}

table map_init_80012{
	actions{
		do_map_init_80012;
	}
}

action do_map_init_80012(){
	modify_field(meta_map_init_80012.qid, 80012);
	modify_field(meta_map_init_80012.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_80012.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_80012.proto, ipv4.protocol);
	modify_field(meta_map_init_80012.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_80012.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_80012.dIP, ipv4.dstAddr);
}

header_type meta_map_init_80012_t {
	 fields {
		qid: 16;
		dMac: 48;
		sIP: 32;
		proto: 16;
		sMac: 48;
		nBytes: 16;
		dIP: 32;
	}
}

metadata meta_map_init_80012_t meta_map_init_80012;

table map_80012_2{
	actions{
		do_map_80012_2;
	}
}

action do_map_80012_2() {
	bit_and(meta_map_init_80012.sIP, meta_map_init_80012.sIP, 0xfff00000);
}

header_type meta_reduce_3_80012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_80012_t meta_reduce_3_80012;

header_type hash_meta_reduce_3_80012_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_80012_t hash_meta_reduce_3_80012;

field_list reduce_3_80012_fields {
	hash_meta_reduce_3_80012.dMac;
	hash_meta_reduce_3_80012.sIP;
	hash_meta_reduce_3_80012.proto;
	hash_meta_reduce_3_80012.sMac;
	hash_meta_reduce_3_80012.nBytes;
	hash_meta_reduce_3_80012.dIP;
}

field_list_calculation reduce_3_80012_fields_hash {
	input {
		reduce_3_80012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_80012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_80012_regs() {
	add_to_field(meta_reduce_3_80012.val, 1);
	register_write(reduce_3_80012,meta_reduce_3_80012.idx,meta_reduce_3_80012.val);
}

table update_reduce_3_80012_counts {
	actions {update_reduce_3_80012_regs;}
	size : 1;
}

action do_reduce_3_80012_hashes() {
	modify_field(hash_meta_reduce_3_80012.dMac, meta_map_init_80012.dMac);
	modify_field(hash_meta_reduce_3_80012.sIP, meta_map_init_80012.sIP);
	modify_field(hash_meta_reduce_3_80012.proto, meta_map_init_80012.proto);
	modify_field(hash_meta_reduce_3_80012.sMac, meta_map_init_80012.sMac);
	modify_field(hash_meta_reduce_3_80012.nBytes, meta_map_init_80012.nBytes);
	modify_field(hash_meta_reduce_3_80012.dIP, meta_map_init_80012.dIP);
	modify_field(meta_reduce_3_80012.qid, 80012);
	modify_field_with_hash_based_offset(meta_reduce_3_80012.idx, 0, reduce_3_80012_fields_hash, 4096);
	register_read(meta_reduce_3_80012.val, reduce_3_80012, meta_reduce_3_80012.idx);
}

table start_reduce_3_80012 {
	actions {do_reduce_3_80012_hashes;}
	size : 1;
}

action set_reduce_3_80012_count() {
	modify_field(meta_reduce_3_80012.val, 1);
}

table set_reduce_3_80012_count {
	actions {set_reduce_3_80012_count;}
        size: 1;
}

header_type meta_distinct_4_80012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_4_80012_t meta_distinct_4_80012;

header_type hash_meta_distinct_4_80012_t {
	fields {
		sMac : 48;
		dMac : 48;
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_4_80012_t hash_meta_distinct_4_80012;

field_list distinct_4_80012_fields {
	hash_meta_distinct_4_80012.sMac;
	hash_meta_distinct_4_80012.dMac;
	hash_meta_distinct_4_80012.sIP;
	hash_meta_distinct_4_80012.dIP;
}

field_list_calculation distinct_4_80012_fields_hash {
	input {
		distinct_4_80012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_4_80012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_4_80012_regs() {
	bit_or(meta_distinct_4_80012.val,meta_distinct_4_80012.val, 1);
	register_write(distinct_4_80012,meta_distinct_4_80012.idx,meta_distinct_4_80012.val);
}

table update_distinct_4_80012_counts {
	actions {update_distinct_4_80012_regs;}
	size : 1;
}

action do_distinct_4_80012_hashes() {
	modify_field(hash_meta_distinct_4_80012.sMac, meta_map_init_80012.sMac);
	modify_field(hash_meta_distinct_4_80012.dMac, meta_map_init_80012.dMac);
	modify_field(hash_meta_distinct_4_80012.sIP, meta_map_init_80012.sIP);
	modify_field(hash_meta_distinct_4_80012.dIP, meta_map_init_80012.dIP);
	modify_field(meta_distinct_4_80012.qid, 80012);
	modify_field_with_hash_based_offset(meta_distinct_4_80012.idx, 0, distinct_4_80012_fields_hash, 4096);
	register_read(meta_distinct_4_80012.val, distinct_4_80012, meta_distinct_4_80012.idx);
}

table start_distinct_4_80012 {
	actions {do_distinct_4_80012_hashes;}
	size : 1;
}

action set_distinct_4_80012_count() {
	modify_field(meta_distinct_4_80012.val, 1);
}

table set_distinct_4_80012_count {
	actions {set_distinct_4_80012_count;}
        size: 1;
}

header_type meta_reduce_5_80012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_80012_t meta_reduce_5_80012;

header_type hash_meta_reduce_5_80012_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_5_80012_t hash_meta_reduce_5_80012;

field_list reduce_5_80012_fields {
	hash_meta_reduce_5_80012.sIP;
}

field_list_calculation reduce_5_80012_fields_hash {
	input {
		reduce_5_80012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_80012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_80012_regs() {
	add_to_field(meta_reduce_5_80012.val, 1);
	register_write(reduce_5_80012,meta_reduce_5_80012.idx,meta_reduce_5_80012.val);
}

table update_reduce_5_80012_counts {
	actions {update_reduce_5_80012_regs;}
	size : 1;
}

action do_reduce_5_80012_hashes() {
	modify_field(hash_meta_reduce_5_80012.sIP, meta_map_init_80012.sIP);
	modify_field(meta_reduce_5_80012.qid, 80012);
	modify_field_with_hash_based_offset(meta_reduce_5_80012.idx, 0, reduce_5_80012_fields_hash, 4096);
	register_read(meta_reduce_5_80012.val, reduce_5_80012, meta_reduce_5_80012.idx);
}

table start_reduce_5_80012 {
	actions {do_reduce_5_80012_hashes;}
	size : 1;
}

action set_reduce_5_80012_count() {
	modify_field(meta_reduce_5_80012.val, 1);
}

table set_reduce_5_80012_count {
	actions {set_reduce_5_80012_count;}
        size: 1;
}

table map_init_70032{
	actions{
		do_map_init_70032;
	}
}

action do_map_init_70032(){
	modify_field(meta_map_init_70032.qid, 70032);
	modify_field(meta_map_init_70032.sIP, ipv4.srcAddr);
}

header_type meta_map_init_70032_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_70032_t meta_map_init_70032;

table map_70032_2{
	actions{
		do_map_70032_2;
	}
}

action do_map_70032_2() {
	bit_and(meta_map_init_70032.sIP, meta_map_init_70032.sIP, 0xffffffff);
}

table map_init_10012{
	actions{
		do_map_init_10012;
	}
}

action do_map_init_10012(){
	modify_field(meta_map_init_10012.qid, 10012);
	modify_field(meta_map_init_10012.sIP, ipv4.srcAddr);
}

header_type meta_map_init_10012_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_10012_t meta_map_init_10012;

table map_10012_2{
	actions{
		do_map_10012_2;
	}
}

action do_map_10012_2() {
	bit_and(meta_map_init_10012.sIP, meta_map_init_10012.sIP, 0xfff00000);
}

header_type meta_distinct_3_10012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_10012_t meta_distinct_3_10012;

header_type hash_meta_distinct_3_10012_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_distinct_3_10012_t hash_meta_distinct_3_10012;

field_list distinct_3_10012_fields {
	hash_meta_distinct_3_10012.sIP;
}

field_list_calculation distinct_3_10012_fields_hash {
	input {
		distinct_3_10012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_10012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_10012_regs() {
	bit_or(meta_distinct_3_10012.val,meta_distinct_3_10012.val, 1);
	register_write(distinct_3_10012,meta_distinct_3_10012.idx,meta_distinct_3_10012.val);
}

table update_distinct_3_10012_counts {
	actions {update_distinct_3_10012_regs;}
	size : 1;
}

action do_distinct_3_10012_hashes() {
	modify_field(hash_meta_distinct_3_10012.sIP, meta_map_init_10012.sIP);
	modify_field(meta_distinct_3_10012.qid, 10012);
	modify_field_with_hash_based_offset(meta_distinct_3_10012.idx, 0, distinct_3_10012_fields_hash, 4096);
	register_read(meta_distinct_3_10012.val, distinct_3_10012, meta_distinct_3_10012.idx);
}

table start_distinct_3_10012 {
	actions {do_distinct_3_10012_hashes;}
	size : 1;
}

action set_distinct_3_10012_count() {
	modify_field(meta_distinct_3_10012.val, 1);
}

table set_distinct_3_10012_count {
	actions {set_distinct_3_10012_count;}
        size: 1;
}

table map_init_80032{
	actions{
		do_map_init_80032;
	}
}

action do_map_init_80032(){
	modify_field(meta_map_init_80032.qid, 80032);
	modify_field(meta_map_init_80032.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_80032.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_80032.proto, ipv4.protocol);
	modify_field(meta_map_init_80032.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_80032.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_80032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_80032_t {
	 fields {
		qid: 16;
		dMac: 48;
		sIP: 32;
		proto: 16;
		sMac: 48;
		nBytes: 16;
		dIP: 32;
	}
}

metadata meta_map_init_80032_t meta_map_init_80032;

table map_80032_2{
	actions{
		do_map_80032_2;
	}
}

action do_map_80032_2() {
	bit_and(meta_map_init_80032.sIP, meta_map_init_80032.sIP, 0xffffffff);
}

header_type meta_reduce_3_80032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_80032_t meta_reduce_3_80032;

header_type hash_meta_reduce_3_80032_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_80032_t hash_meta_reduce_3_80032;

field_list reduce_3_80032_fields {
	hash_meta_reduce_3_80032.dMac;
	hash_meta_reduce_3_80032.sIP;
	hash_meta_reduce_3_80032.proto;
	hash_meta_reduce_3_80032.sMac;
	hash_meta_reduce_3_80032.nBytes;
	hash_meta_reduce_3_80032.dIP;
}

field_list_calculation reduce_3_80032_fields_hash {
	input {
		reduce_3_80032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_80032{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_80032_regs() {
	add_to_field(meta_reduce_3_80032.val, 1);
	register_write(reduce_3_80032,meta_reduce_3_80032.idx,meta_reduce_3_80032.val);
}

table update_reduce_3_80032_counts {
	actions {update_reduce_3_80032_regs;}
	size : 1;
}

action do_reduce_3_80032_hashes() {
	modify_field(hash_meta_reduce_3_80032.dMac, meta_map_init_80032.dMac);
	modify_field(hash_meta_reduce_3_80032.sIP, meta_map_init_80032.sIP);
	modify_field(hash_meta_reduce_3_80032.proto, meta_map_init_80032.proto);
	modify_field(hash_meta_reduce_3_80032.sMac, meta_map_init_80032.sMac);
	modify_field(hash_meta_reduce_3_80032.nBytes, meta_map_init_80032.nBytes);
	modify_field(hash_meta_reduce_3_80032.dIP, meta_map_init_80032.dIP);
	modify_field(meta_reduce_3_80032.qid, 80032);
	modify_field_with_hash_based_offset(meta_reduce_3_80032.idx, 0, reduce_3_80032_fields_hash, 4096);
	register_read(meta_reduce_3_80032.val, reduce_3_80032, meta_reduce_3_80032.idx);
}

table start_reduce_3_80032 {
	actions {do_reduce_3_80032_hashes;}
	size : 1;
}

action set_reduce_3_80032_count() {
	modify_field(meta_reduce_3_80032.val, 1);
}

table set_reduce_3_80032_count {
	actions {set_reduce_3_80032_count;}
        size: 1;
}

table map_init_50032{
	actions{
		do_map_init_50032;
	}
}

action do_map_init_50032(){
	modify_field(meta_map_init_50032.qid, 50032);
	modify_field(meta_map_init_50032.sIP, ipv4.srcAddr);
}

header_type meta_map_init_50032_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_50032_t meta_map_init_50032;

table map_50032_2{
	actions{
		do_map_50032_2;
	}
}

action do_map_50032_2() {
	bit_and(meta_map_init_50032.sIP, meta_map_init_50032.sIP, 0xffffffff);
}

header_type meta_reduce_3_50032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_50032_t meta_reduce_3_50032;

header_type hash_meta_reduce_3_50032_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_3_50032_t hash_meta_reduce_3_50032;

field_list reduce_3_50032_fields {
	hash_meta_reduce_3_50032.sIP;
}

field_list_calculation reduce_3_50032_fields_hash {
	input {
		reduce_3_50032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_50032{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_50032_regs() {
	add_to_field(meta_reduce_3_50032.val, 1);
	register_write(reduce_3_50032,meta_reduce_3_50032.idx,meta_reduce_3_50032.val);
}

table update_reduce_3_50032_counts {
	actions {update_reduce_3_50032_regs;}
	size : 1;
}

action do_reduce_3_50032_hashes() {
	modify_field(hash_meta_reduce_3_50032.sIP, meta_map_init_50032.sIP);
	modify_field(meta_reduce_3_50032.qid, 50032);
	modify_field_with_hash_based_offset(meta_reduce_3_50032.idx, 0, reduce_3_50032_fields_hash, 4096);
	register_read(meta_reduce_3_50032.val, reduce_3_50032, meta_reduce_3_50032.idx);
}

table start_reduce_3_50032 {
	actions {do_reduce_3_50032_hashes;}
	size : 1;
}

action set_reduce_3_50032_count() {
	modify_field(meta_reduce_3_50032.val, 1);
}

table set_reduce_3_50032_count {
	actions {set_reduce_3_50032_count;}
        size: 1;
}

table map_init_100004{
	actions{
		do_map_init_100004;
	}
}

action do_map_init_100004(){
	modify_field(meta_map_init_100004.qid, 100004);
	modify_field(meta_map_init_100004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_100004_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_100004_t meta_map_init_100004;

table map_100004_2{
	actions{
		do_map_100004_2;
	}
}

action do_map_100004_2() {
	bit_and(meta_map_init_100004.dIP, meta_map_init_100004.dIP, 0xf0000000);
}

header_type meta_distinct_3_100004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_100004_t meta_distinct_3_100004;

header_type hash_meta_distinct_3_100004_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_100004_t hash_meta_distinct_3_100004;

field_list distinct_3_100004_fields {
	hash_meta_distinct_3_100004.dIP;
}

field_list_calculation distinct_3_100004_fields_hash {
	input {
		distinct_3_100004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_100004{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_100004_regs() {
	bit_or(meta_distinct_3_100004.val,meta_distinct_3_100004.val, 1);
	register_write(distinct_3_100004,meta_distinct_3_100004.idx,meta_distinct_3_100004.val);
}

table update_distinct_3_100004_counts {
	actions {update_distinct_3_100004_regs;}
	size : 1;
}

action do_distinct_3_100004_hashes() {
	modify_field(hash_meta_distinct_3_100004.dIP, meta_map_init_100004.dIP);
	modify_field(meta_distinct_3_100004.qid, 100004);
	modify_field_with_hash_based_offset(meta_distinct_3_100004.idx, 0, distinct_3_100004_fields_hash, 4096);
	register_read(meta_distinct_3_100004.val, distinct_3_100004, meta_distinct_3_100004.idx);
}

table start_distinct_3_100004 {
	actions {do_distinct_3_100004_hashes;}
	size : 1;
}

action set_distinct_3_100004_count() {
	modify_field(meta_distinct_3_100004.val, 1);
}

table set_distinct_3_100004_count {
	actions {set_distinct_3_100004_count;}
        size: 1;
}

table map_init_80028{
	actions{
		do_map_init_80028;
	}
}

action do_map_init_80028(){
	modify_field(meta_map_init_80028.qid, 80028);
	modify_field(meta_map_init_80028.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_80028.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_80028.proto, ipv4.protocol);
	modify_field(meta_map_init_80028.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_80028.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_80028.dIP, ipv4.dstAddr);
}

header_type meta_map_init_80028_t {
	 fields {
		qid: 16;
		dMac: 48;
		sIP: 32;
		proto: 16;
		sMac: 48;
		nBytes: 16;
		dIP: 32;
	}
}

metadata meta_map_init_80028_t meta_map_init_80028;

table map_80028_2{
	actions{
		do_map_80028_2;
	}
}

action do_map_80028_2() {
	bit_and(meta_map_init_80028.sIP, meta_map_init_80028.sIP, 0xfffffff0);
}

header_type meta_reduce_3_80028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_80028_t meta_reduce_3_80028;

header_type hash_meta_reduce_3_80028_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_80028_t hash_meta_reduce_3_80028;

field_list reduce_3_80028_fields {
	hash_meta_reduce_3_80028.dMac;
	hash_meta_reduce_3_80028.sIP;
	hash_meta_reduce_3_80028.proto;
	hash_meta_reduce_3_80028.sMac;
	hash_meta_reduce_3_80028.nBytes;
	hash_meta_reduce_3_80028.dIP;
}

field_list_calculation reduce_3_80028_fields_hash {
	input {
		reduce_3_80028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_80028{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_80028_regs() {
	add_to_field(meta_reduce_3_80028.val, 1);
	register_write(reduce_3_80028,meta_reduce_3_80028.idx,meta_reduce_3_80028.val);
}

table update_reduce_3_80028_counts {
	actions {update_reduce_3_80028_regs;}
	size : 1;
}

action do_reduce_3_80028_hashes() {
	modify_field(hash_meta_reduce_3_80028.dMac, meta_map_init_80028.dMac);
	modify_field(hash_meta_reduce_3_80028.sIP, meta_map_init_80028.sIP);
	modify_field(hash_meta_reduce_3_80028.proto, meta_map_init_80028.proto);
	modify_field(hash_meta_reduce_3_80028.sMac, meta_map_init_80028.sMac);
	modify_field(hash_meta_reduce_3_80028.nBytes, meta_map_init_80028.nBytes);
	modify_field(hash_meta_reduce_3_80028.dIP, meta_map_init_80028.dIP);
	modify_field(meta_reduce_3_80028.qid, 80028);
	modify_field_with_hash_based_offset(meta_reduce_3_80028.idx, 0, reduce_3_80028_fields_hash, 4096);
	register_read(meta_reduce_3_80028.val, reduce_3_80028, meta_reduce_3_80028.idx);
}

table start_reduce_3_80028 {
	actions {do_reduce_3_80028_hashes;}
	size : 1;
}

action set_reduce_3_80028_count() {
	modify_field(meta_reduce_3_80028.val, 1);
}

table set_reduce_3_80028_count {
	actions {set_reduce_3_80028_count;}
        size: 1;
}

header_type meta_distinct_4_80028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_4_80028_t meta_distinct_4_80028;

header_type hash_meta_distinct_4_80028_t {
	fields {
		sMac : 48;
		dMac : 48;
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_4_80028_t hash_meta_distinct_4_80028;

field_list distinct_4_80028_fields {
	hash_meta_distinct_4_80028.sMac;
	hash_meta_distinct_4_80028.dMac;
	hash_meta_distinct_4_80028.sIP;
	hash_meta_distinct_4_80028.dIP;
}

field_list_calculation distinct_4_80028_fields_hash {
	input {
		distinct_4_80028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_4_80028{
	width : 32;
	instance_count : 4096;
}

action update_distinct_4_80028_regs() {
	bit_or(meta_distinct_4_80028.val,meta_distinct_4_80028.val, 1);
	register_write(distinct_4_80028,meta_distinct_4_80028.idx,meta_distinct_4_80028.val);
}

table update_distinct_4_80028_counts {
	actions {update_distinct_4_80028_regs;}
	size : 1;
}

action do_distinct_4_80028_hashes() {
	modify_field(hash_meta_distinct_4_80028.sMac, meta_map_init_80028.sMac);
	modify_field(hash_meta_distinct_4_80028.dMac, meta_map_init_80028.dMac);
	modify_field(hash_meta_distinct_4_80028.sIP, meta_map_init_80028.sIP);
	modify_field(hash_meta_distinct_4_80028.dIP, meta_map_init_80028.dIP);
	modify_field(meta_distinct_4_80028.qid, 80028);
	modify_field_with_hash_based_offset(meta_distinct_4_80028.idx, 0, distinct_4_80028_fields_hash, 4096);
	register_read(meta_distinct_4_80028.val, distinct_4_80028, meta_distinct_4_80028.idx);
}

table start_distinct_4_80028 {
	actions {do_distinct_4_80028_hashes;}
	size : 1;
}

action set_distinct_4_80028_count() {
	modify_field(meta_distinct_4_80028.val, 1);
}

table set_distinct_4_80028_count {
	actions {set_distinct_4_80028_count;}
        size: 1;
}

header_type meta_reduce_5_80028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_80028_t meta_reduce_5_80028;

header_type hash_meta_reduce_5_80028_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_5_80028_t hash_meta_reduce_5_80028;

field_list reduce_5_80028_fields {
	hash_meta_reduce_5_80028.sIP;
}

field_list_calculation reduce_5_80028_fields_hash {
	input {
		reduce_5_80028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_80028{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_80028_regs() {
	add_to_field(meta_reduce_5_80028.val, 1);
	register_write(reduce_5_80028,meta_reduce_5_80028.idx,meta_reduce_5_80028.val);
}

table update_reduce_5_80028_counts {
	actions {update_reduce_5_80028_regs;}
	size : 1;
}

action do_reduce_5_80028_hashes() {
	modify_field(hash_meta_reduce_5_80028.sIP, meta_map_init_80028.sIP);
	modify_field(meta_reduce_5_80028.qid, 80028);
	modify_field_with_hash_based_offset(meta_reduce_5_80028.idx, 0, reduce_5_80028_fields_hash, 4096);
	register_read(meta_reduce_5_80028.val, reduce_5_80028, meta_reduce_5_80028.idx);
}

table start_reduce_5_80028 {
	actions {do_reduce_5_80028_hashes;}
	size : 1;
}

action set_reduce_5_80028_count() {
	modify_field(meta_reduce_5_80028.val, 1);
}

table set_reduce_5_80028_count {
	actions {set_reduce_5_80028_count;}
        size: 1;
}

table map_init_100012{
	actions{
		do_map_init_100012;
	}
}

action do_map_init_100012(){
	modify_field(meta_map_init_100012.qid, 100012);
	modify_field(meta_map_init_100012.dIP, ipv4.dstAddr);
}

header_type meta_map_init_100012_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_100012_t meta_map_init_100012;

table map_100012_2{
	actions{
		do_map_100012_2;
	}
}

action do_map_100012_2() {
	bit_and(meta_map_init_100012.dIP, meta_map_init_100012.dIP, 0xfff00000);
}

header_type meta_distinct_3_100012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_100012_t meta_distinct_3_100012;

header_type hash_meta_distinct_3_100012_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_100012_t hash_meta_distinct_3_100012;

field_list distinct_3_100012_fields {
	hash_meta_distinct_3_100012.dIP;
}

field_list_calculation distinct_3_100012_fields_hash {
	input {
		distinct_3_100012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_100012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_100012_regs() {
	bit_or(meta_distinct_3_100012.val,meta_distinct_3_100012.val, 1);
	register_write(distinct_3_100012,meta_distinct_3_100012.idx,meta_distinct_3_100012.val);
}

table update_distinct_3_100012_counts {
	actions {update_distinct_3_100012_regs;}
	size : 1;
}

action do_distinct_3_100012_hashes() {
	modify_field(hash_meta_distinct_3_100012.dIP, meta_map_init_100012.dIP);
	modify_field(meta_distinct_3_100012.qid, 100012);
	modify_field_with_hash_based_offset(meta_distinct_3_100012.idx, 0, distinct_3_100012_fields_hash, 4096);
	register_read(meta_distinct_3_100012.val, distinct_3_100012, meta_distinct_3_100012.idx);
}

table start_distinct_3_100012 {
	actions {do_distinct_3_100012_hashes;}
	size : 1;
}

action set_distinct_3_100012_count() {
	modify_field(meta_distinct_3_100012.val, 1);
}

table set_distinct_3_100012_count {
	actions {set_distinct_3_100012_count;}
        size: 1;
}

table map_init_10032{
	actions{
		do_map_init_10032;
	}
}

action do_map_init_10032(){
	modify_field(meta_map_init_10032.qid, 10032);
	modify_field(meta_map_init_10032.sIP, ipv4.srcAddr);
}

header_type meta_map_init_10032_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_10032_t meta_map_init_10032;

table map_10032_2{
	actions{
		do_map_10032_2;
	}
}

action do_map_10032_2() {
	bit_and(meta_map_init_10032.sIP, meta_map_init_10032.sIP, 0xffffffff);
}

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
	}
}

metadata hash_meta_distinct_3_10032_t hash_meta_distinct_3_10032;

field_list distinct_3_10032_fields {
	hash_meta_distinct_3_10032.sIP;
}

field_list_calculation distinct_3_10032_fields_hash {
	input {
		distinct_3_10032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_10032{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_10032_regs() {
	bit_or(meta_distinct_3_10032.val,meta_distinct_3_10032.val, 1);
	register_write(distinct_3_10032,meta_distinct_3_10032.idx,meta_distinct_3_10032.val);
}

table update_distinct_3_10032_counts {
	actions {update_distinct_3_10032_regs;}
	size : 1;
}

action do_distinct_3_10032_hashes() {
	modify_field(hash_meta_distinct_3_10032.sIP, meta_map_init_10032.sIP);
	modify_field(meta_distinct_3_10032.qid, 10032);
	modify_field_with_hash_based_offset(meta_distinct_3_10032.idx, 0, distinct_3_10032_fields_hash, 4096);
	register_read(meta_distinct_3_10032.val, distinct_3_10032, meta_distinct_3_10032.idx);
}

table start_distinct_3_10032 {
	actions {do_distinct_3_10032_hashes;}
	size : 1;
}

action set_distinct_3_10032_count() {
	modify_field(meta_distinct_3_10032.val, 1);
}

table set_distinct_3_10032_count {
	actions {set_distinct_3_10032_count;}
        size: 1;
}

table map_init_110004{
	actions{
		do_map_init_110004;
	}
}

action do_map_init_110004(){
	modify_field(meta_map_init_110004.qid, 110004);
	modify_field(meta_map_init_110004.dPort, tcp.dstPort);
	modify_field(meta_map_init_110004.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_110004.sPort, tcp.srcPort);
	modify_field(meta_map_init_110004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_110004_t {
	 fields {
		qid: 16;
		dPort: 16;
		dMac: 48;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_110004_t meta_map_init_110004;

table map_110004_1{
	actions{
		do_map_110004_1;
	}
}

action do_map_110004_1() {
	bit_and(meta_map_init_110004.dIP, meta_map_init_110004.dIP, 0xf0000000);
}

header_type meta_distinct_2_110004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_110004_t meta_distinct_2_110004;

header_type hash_meta_distinct_2_110004_t {
	fields {
		dPort : 16;
		dMac : 48;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_110004_t hash_meta_distinct_2_110004;

field_list distinct_2_110004_fields {
	hash_meta_distinct_2_110004.dPort;
	hash_meta_distinct_2_110004.dMac;
	hash_meta_distinct_2_110004.sPort;
	hash_meta_distinct_2_110004.dIP;
}

field_list_calculation distinct_2_110004_fields_hash {
	input {
		distinct_2_110004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_110004{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_110004_regs() {
	bit_or(meta_distinct_2_110004.val,meta_distinct_2_110004.val, 1);
	register_write(distinct_2_110004,meta_distinct_2_110004.idx,meta_distinct_2_110004.val);
}

table update_distinct_2_110004_counts {
	actions {update_distinct_2_110004_regs;}
	size : 1;
}

action do_distinct_2_110004_hashes() {
	modify_field(hash_meta_distinct_2_110004.dPort, meta_map_init_110004.dPort);
	modify_field(hash_meta_distinct_2_110004.dMac, meta_map_init_110004.dMac);
	modify_field(hash_meta_distinct_2_110004.sPort, meta_map_init_110004.sPort);
	modify_field(hash_meta_distinct_2_110004.dIP, meta_map_init_110004.dIP);
	modify_field(meta_distinct_2_110004.qid, 110004);
	modify_field_with_hash_based_offset(meta_distinct_2_110004.idx, 0, distinct_2_110004_fields_hash, 4096);
	register_read(meta_distinct_2_110004.val, distinct_2_110004, meta_distinct_2_110004.idx);
}

table start_distinct_2_110004 {
	actions {do_distinct_2_110004_hashes;}
	size : 1;
}

action set_distinct_2_110004_count() {
	modify_field(meta_distinct_2_110004.val, 1);
}

table set_distinct_2_110004_count {
	actions {set_distinct_2_110004_count;}
        size: 1;
}

header_type meta_reduce_3_110004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_110004_t meta_reduce_3_110004;

header_type hash_meta_reduce_3_110004_t {
	fields {
		dPort : 16;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_110004_t hash_meta_reduce_3_110004;

field_list reduce_3_110004_fields {
	hash_meta_reduce_3_110004.dPort;
	hash_meta_reduce_3_110004.sPort;
	hash_meta_reduce_3_110004.dIP;
}

field_list_calculation reduce_3_110004_fields_hash {
	input {
		reduce_3_110004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_110004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_110004_regs() {
	add_to_field(meta_reduce_3_110004.val, 1);
	register_write(reduce_3_110004,meta_reduce_3_110004.idx,meta_reduce_3_110004.val);
}

table update_reduce_3_110004_counts {
	actions {update_reduce_3_110004_regs;}
	size : 1;
}

action do_reduce_3_110004_hashes() {
	modify_field(hash_meta_reduce_3_110004.dPort, meta_map_init_110004.dPort);
	modify_field(hash_meta_reduce_3_110004.sPort, meta_map_init_110004.sPort);
	modify_field(hash_meta_reduce_3_110004.dIP, meta_map_init_110004.dIP);
	modify_field(meta_reduce_3_110004.qid, 110004);
	modify_field_with_hash_based_offset(meta_reduce_3_110004.idx, 0, reduce_3_110004_fields_hash, 4096);
	register_read(meta_reduce_3_110004.val, reduce_3_110004, meta_reduce_3_110004.idx);
}

table start_reduce_3_110004 {
	actions {do_reduce_3_110004_hashes;}
	size : 1;
}

action set_reduce_3_110004_count() {
	modify_field(meta_reduce_3_110004.val, 1);
}

table set_reduce_3_110004_count {
	actions {set_reduce_3_110004_count;}
        size: 1;
}

header_type meta_reduce_4_110004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_110004_t meta_reduce_4_110004;

header_type hash_meta_reduce_4_110004_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_110004_t hash_meta_reduce_4_110004;

field_list reduce_4_110004_fields {
	hash_meta_reduce_4_110004.dIP;
}

field_list_calculation reduce_4_110004_fields_hash {
	input {
		reduce_4_110004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_110004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_110004_regs() {
	add_to_field(meta_reduce_4_110004.val, 1);
	register_write(reduce_4_110004,meta_reduce_4_110004.idx,meta_reduce_4_110004.val);
}

table update_reduce_4_110004_counts {
	actions {update_reduce_4_110004_regs;}
	size : 1;
}

action do_reduce_4_110004_hashes() {
	modify_field(hash_meta_reduce_4_110004.dIP, meta_map_init_110004.dIP);
	modify_field(meta_reduce_4_110004.qid, 110004);
	modify_field_with_hash_based_offset(meta_reduce_4_110004.idx, 0, reduce_4_110004_fields_hash, 4096);
	register_read(meta_reduce_4_110004.val, reduce_4_110004, meta_reduce_4_110004.idx);
}

table start_reduce_4_110004 {
	actions {do_reduce_4_110004_hashes;}
	size : 1;
}

action set_reduce_4_110004_count() {
	modify_field(meta_reduce_4_110004.val, 1);
}

table set_reduce_4_110004_count {
	actions {set_reduce_4_110004_count;}
        size: 1;
}

table map_init_110012{
	actions{
		do_map_init_110012;
	}
}

action do_map_init_110012(){
	modify_field(meta_map_init_110012.qid, 110012);
	modify_field(meta_map_init_110012.dPort, tcp.dstPort);
	modify_field(meta_map_init_110012.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_110012.sPort, tcp.srcPort);
	modify_field(meta_map_init_110012.dIP, ipv4.dstAddr);
}

header_type meta_map_init_110012_t {
	 fields {
		qid: 16;
		dPort: 16;
		dMac: 48;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_110012_t meta_map_init_110012;

table map_110012_2{
	actions{
		do_map_110012_2;
	}
}

action do_map_110012_2() {
	bit_and(meta_map_init_110012.dIP, meta_map_init_110012.dIP, 0xfff00000);
}

header_type meta_distinct_3_110012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_110012_t meta_distinct_3_110012;

header_type hash_meta_distinct_3_110012_t {
	fields {
		dPort : 16;
		dMac : 48;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_110012_t hash_meta_distinct_3_110012;

field_list distinct_3_110012_fields {
	hash_meta_distinct_3_110012.dPort;
	hash_meta_distinct_3_110012.dMac;
	hash_meta_distinct_3_110012.sPort;
	hash_meta_distinct_3_110012.dIP;
}

field_list_calculation distinct_3_110012_fields_hash {
	input {
		distinct_3_110012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_110012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_110012_regs() {
	bit_or(meta_distinct_3_110012.val,meta_distinct_3_110012.val, 1);
	register_write(distinct_3_110012,meta_distinct_3_110012.idx,meta_distinct_3_110012.val);
}

table update_distinct_3_110012_counts {
	actions {update_distinct_3_110012_regs;}
	size : 1;
}

action do_distinct_3_110012_hashes() {
	modify_field(hash_meta_distinct_3_110012.dPort, meta_map_init_110012.dPort);
	modify_field(hash_meta_distinct_3_110012.dMac, meta_map_init_110012.dMac);
	modify_field(hash_meta_distinct_3_110012.sPort, meta_map_init_110012.sPort);
	modify_field(hash_meta_distinct_3_110012.dIP, meta_map_init_110012.dIP);
	modify_field(meta_distinct_3_110012.qid, 110012);
	modify_field_with_hash_based_offset(meta_distinct_3_110012.idx, 0, distinct_3_110012_fields_hash, 4096);
	register_read(meta_distinct_3_110012.val, distinct_3_110012, meta_distinct_3_110012.idx);
}

table start_distinct_3_110012 {
	actions {do_distinct_3_110012_hashes;}
	size : 1;
}

action set_distinct_3_110012_count() {
	modify_field(meta_distinct_3_110012.val, 1);
}

table set_distinct_3_110012_count {
	actions {set_distinct_3_110012_count;}
        size: 1;
}

header_type meta_reduce_4_110012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_110012_t meta_reduce_4_110012;

header_type hash_meta_reduce_4_110012_t {
	fields {
		dPort : 16;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_110012_t hash_meta_reduce_4_110012;

field_list reduce_4_110012_fields {
	hash_meta_reduce_4_110012.dPort;
	hash_meta_reduce_4_110012.sPort;
	hash_meta_reduce_4_110012.dIP;
}

field_list_calculation reduce_4_110012_fields_hash {
	input {
		reduce_4_110012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_110012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_110012_regs() {
	add_to_field(meta_reduce_4_110012.val, 1);
	register_write(reduce_4_110012,meta_reduce_4_110012.idx,meta_reduce_4_110012.val);
}

table update_reduce_4_110012_counts {
	actions {update_reduce_4_110012_regs;}
	size : 1;
}

action do_reduce_4_110012_hashes() {
	modify_field(hash_meta_reduce_4_110012.dPort, meta_map_init_110012.dPort);
	modify_field(hash_meta_reduce_4_110012.sPort, meta_map_init_110012.sPort);
	modify_field(hash_meta_reduce_4_110012.dIP, meta_map_init_110012.dIP);
	modify_field(meta_reduce_4_110012.qid, 110012);
	modify_field_with_hash_based_offset(meta_reduce_4_110012.idx, 0, reduce_4_110012_fields_hash, 4096);
	register_read(meta_reduce_4_110012.val, reduce_4_110012, meta_reduce_4_110012.idx);
}

table start_reduce_4_110012 {
	actions {do_reduce_4_110012_hashes;}
	size : 1;
}

action set_reduce_4_110012_count() {
	modify_field(meta_reduce_4_110012.val, 1);
}

table set_reduce_4_110012_count {
	actions {set_reduce_4_110012_count;}
        size: 1;
}

header_type meta_reduce_5_110012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_110012_t meta_reduce_5_110012;

header_type hash_meta_reduce_5_110012_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_5_110012_t hash_meta_reduce_5_110012;

field_list reduce_5_110012_fields {
	hash_meta_reduce_5_110012.dIP;
}

field_list_calculation reduce_5_110012_fields_hash {
	input {
		reduce_5_110012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_110012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_110012_regs() {
	add_to_field(meta_reduce_5_110012.val, 1);
	register_write(reduce_5_110012,meta_reduce_5_110012.idx,meta_reduce_5_110012.val);
}

table update_reduce_5_110012_counts {
	actions {update_reduce_5_110012_regs;}
	size : 1;
}

action do_reduce_5_110012_hashes() {
	modify_field(hash_meta_reduce_5_110012.dIP, meta_map_init_110012.dIP);
	modify_field(meta_reduce_5_110012.qid, 110012);
	modify_field_with_hash_based_offset(meta_reduce_5_110012.idx, 0, reduce_5_110012_fields_hash, 4096);
	register_read(meta_reduce_5_110012.val, reduce_5_110012, meta_reduce_5_110012.idx);
}

table start_reduce_5_110012 {
	actions {do_reduce_5_110012_hashes;}
	size : 1;
}

action set_reduce_5_110012_count() {
	modify_field(meta_reduce_5_110012.val, 1);
}

table set_reduce_5_110012_count {
	actions {set_reduce_5_110012_count;}
        size: 1;
}

table map_init_100032{
	actions{
		do_map_init_100032;
	}
}

action do_map_init_100032(){
	modify_field(meta_map_init_100032.qid, 100032);
	modify_field(meta_map_init_100032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_100032_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_100032_t meta_map_init_100032;

table map_100032_2{
	actions{
		do_map_100032_2;
	}
}

action do_map_100032_2() {
	bit_and(meta_map_init_100032.dIP, meta_map_init_100032.dIP, 0xffffffff);
}

table map_init_40004{
	actions{
		do_map_init_40004;
	}
}

action do_map_init_40004(){
	modify_field(meta_map_init_40004.qid, 40004);
	modify_field(meta_map_init_40004.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_40004.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_40004.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_40004.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_40004.proto, ipv4.protocol);
	modify_field(meta_map_init_40004.dPort, tcp.dstPort);
	modify_field(meta_map_init_40004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40004_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
		nBytes: 16;
		proto: 16;
		dPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40004_t meta_map_init_40004;

table map_40004_2{
	actions{
		do_map_40004_2;
	}
}

action do_map_40004_2() {
	bit_and(meta_map_init_40004.sIP, meta_map_init_40004.sIP, 0xf0000000);
}

header_type meta_distinct_3_40004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_40004_t meta_distinct_3_40004;

header_type hash_meta_distinct_3_40004_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_40004_t hash_meta_distinct_3_40004;

field_list distinct_3_40004_fields {
	hash_meta_distinct_3_40004.dMac;
	hash_meta_distinct_3_40004.sIP;
	hash_meta_distinct_3_40004.proto;
	hash_meta_distinct_3_40004.sMac;
	hash_meta_distinct_3_40004.nBytes;
	hash_meta_distinct_3_40004.dPort;
	hash_meta_distinct_3_40004.dIP;
}

field_list_calculation distinct_3_40004_fields_hash {
	input {
		distinct_3_40004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_40004{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_40004_regs() {
	bit_or(meta_distinct_3_40004.val,meta_distinct_3_40004.val, 1);
	register_write(distinct_3_40004,meta_distinct_3_40004.idx,meta_distinct_3_40004.val);
}

table update_distinct_3_40004_counts {
	actions {update_distinct_3_40004_regs;}
	size : 1;
}

action do_distinct_3_40004_hashes() {
	modify_field(hash_meta_distinct_3_40004.dMac, meta_map_init_40004.dMac);
	modify_field(hash_meta_distinct_3_40004.sIP, meta_map_init_40004.sIP);
	modify_field(hash_meta_distinct_3_40004.proto, meta_map_init_40004.proto);
	modify_field(hash_meta_distinct_3_40004.sMac, meta_map_init_40004.sMac);
	modify_field(hash_meta_distinct_3_40004.nBytes, meta_map_init_40004.nBytes);
	modify_field(hash_meta_distinct_3_40004.dPort, meta_map_init_40004.dPort);
	modify_field(hash_meta_distinct_3_40004.dIP, meta_map_init_40004.dIP);
	modify_field(meta_distinct_3_40004.qid, 40004);
	modify_field_with_hash_based_offset(meta_distinct_3_40004.idx, 0, distinct_3_40004_fields_hash, 4096);
	register_read(meta_distinct_3_40004.val, distinct_3_40004, meta_distinct_3_40004.idx);
}

table start_distinct_3_40004 {
	actions {do_distinct_3_40004_hashes;}
	size : 1;
}

action set_distinct_3_40004_count() {
	modify_field(meta_distinct_3_40004.val, 1);
}

table set_distinct_3_40004_count {
	actions {set_distinct_3_40004_count;}
        size: 1;
}

table map_init_40012{
	actions{
		do_map_init_40012;
	}
}

action do_map_init_40012(){
	modify_field(meta_map_init_40012.qid, 40012);
	modify_field(meta_map_init_40012.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_40012.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_40012.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_40012.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_40012.proto, ipv4.protocol);
	modify_field(meta_map_init_40012.dPort, tcp.dstPort);
	modify_field(meta_map_init_40012.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40012_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
		nBytes: 16;
		proto: 16;
		dPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40012_t meta_map_init_40012;

table map_40012_2{
	actions{
		do_map_40012_2;
	}
}

action do_map_40012_2() {
	bit_and(meta_map_init_40012.sIP, meta_map_init_40012.sIP, 0xfff00000);
}

header_type meta_distinct_3_40012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_40012_t meta_distinct_3_40012;

header_type hash_meta_distinct_3_40012_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_40012_t hash_meta_distinct_3_40012;

field_list distinct_3_40012_fields {
	hash_meta_distinct_3_40012.dMac;
	hash_meta_distinct_3_40012.sIP;
	hash_meta_distinct_3_40012.proto;
	hash_meta_distinct_3_40012.sMac;
	hash_meta_distinct_3_40012.nBytes;
	hash_meta_distinct_3_40012.dPort;
	hash_meta_distinct_3_40012.dIP;
}

field_list_calculation distinct_3_40012_fields_hash {
	input {
		distinct_3_40012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_40012{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_40012_regs() {
	bit_or(meta_distinct_3_40012.val,meta_distinct_3_40012.val, 1);
	register_write(distinct_3_40012,meta_distinct_3_40012.idx,meta_distinct_3_40012.val);
}

table update_distinct_3_40012_counts {
	actions {update_distinct_3_40012_regs;}
	size : 1;
}

action do_distinct_3_40012_hashes() {
	modify_field(hash_meta_distinct_3_40012.dMac, meta_map_init_40012.dMac);
	modify_field(hash_meta_distinct_3_40012.sIP, meta_map_init_40012.sIP);
	modify_field(hash_meta_distinct_3_40012.proto, meta_map_init_40012.proto);
	modify_field(hash_meta_distinct_3_40012.sMac, meta_map_init_40012.sMac);
	modify_field(hash_meta_distinct_3_40012.nBytes, meta_map_init_40012.nBytes);
	modify_field(hash_meta_distinct_3_40012.dPort, meta_map_init_40012.dPort);
	modify_field(hash_meta_distinct_3_40012.dIP, meta_map_init_40012.dIP);
	modify_field(meta_distinct_3_40012.qid, 40012);
	modify_field_with_hash_based_offset(meta_distinct_3_40012.idx, 0, distinct_3_40012_fields_hash, 4096);
	register_read(meta_distinct_3_40012.val, distinct_3_40012, meta_distinct_3_40012.idx);
}

table start_distinct_3_40012 {
	actions {do_distinct_3_40012_hashes;}
	size : 1;
}

action set_distinct_3_40012_count() {
	modify_field(meta_distinct_3_40012.val, 1);
}

table set_distinct_3_40012_count {
	actions {set_distinct_3_40012_count;}
        size: 1;
}

header_type meta_reduce_4_40012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_40012_t meta_reduce_4_40012;

header_type hash_meta_reduce_4_40012_t {
	fields {
		sIP : 32;
		nBytes : 16;
	}
}

metadata hash_meta_reduce_4_40012_t hash_meta_reduce_4_40012;

field_list reduce_4_40012_fields {
	hash_meta_reduce_4_40012.sIP;
	hash_meta_reduce_4_40012.nBytes;
}

field_list_calculation reduce_4_40012_fields_hash {
	input {
		reduce_4_40012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_40012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_40012_regs() {
	add_to_field(meta_reduce_4_40012.val, 1);
	register_write(reduce_4_40012,meta_reduce_4_40012.idx,meta_reduce_4_40012.val);
}

table update_reduce_4_40012_counts {
	actions {update_reduce_4_40012_regs;}
	size : 1;
}

action do_reduce_4_40012_hashes() {
	modify_field(hash_meta_reduce_4_40012.sIP, meta_map_init_40012.sIP);
	modify_field(hash_meta_reduce_4_40012.nBytes, meta_map_init_40012.nBytes);
	modify_field(meta_reduce_4_40012.qid, 40012);
	modify_field_with_hash_based_offset(meta_reduce_4_40012.idx, 0, reduce_4_40012_fields_hash, 4096);
	register_read(meta_reduce_4_40012.val, reduce_4_40012, meta_reduce_4_40012.idx);
}

table start_reduce_4_40012 {
	actions {do_reduce_4_40012_hashes;}
	size : 1;
}

action set_reduce_4_40012_count() {
	modify_field(meta_reduce_4_40012.val, 1);
}

table set_reduce_4_40012_count {
	actions {set_reduce_4_40012_count;}
        size: 1;
}

header_type meta_reduce_5_40012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_40012_t meta_reduce_5_40012;

header_type hash_meta_reduce_5_40012_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_5_40012_t hash_meta_reduce_5_40012;

field_list reduce_5_40012_fields {
	hash_meta_reduce_5_40012.sIP;
}

field_list_calculation reduce_5_40012_fields_hash {
	input {
		reduce_5_40012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_40012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_40012_regs() {
	add_to_field(meta_reduce_5_40012.val, 1);
	register_write(reduce_5_40012,meta_reduce_5_40012.idx,meta_reduce_5_40012.val);
}

table update_reduce_5_40012_counts {
	actions {update_reduce_5_40012_regs;}
	size : 1;
}

action do_reduce_5_40012_hashes() {
	modify_field(hash_meta_reduce_5_40012.sIP, meta_map_init_40012.sIP);
	modify_field(meta_reduce_5_40012.qid, 40012);
	modify_field_with_hash_based_offset(meta_reduce_5_40012.idx, 0, reduce_5_40012_fields_hash, 4096);
	register_read(meta_reduce_5_40012.val, reduce_5_40012, meta_reduce_5_40012.idx);
}

table start_reduce_5_40012 {
	actions {do_reduce_5_40012_hashes;}
	size : 1;
}

action set_reduce_5_40012_count() {
	modify_field(meta_reduce_5_40012.val, 1);
}

table set_reduce_5_40012_count {
	actions {set_reduce_5_40012_count;}
        size: 1;
}

table map_init_110028{
	actions{
		do_map_init_110028;
	}
}

action do_map_init_110028(){
	modify_field(meta_map_init_110028.qid, 110028);
	modify_field(meta_map_init_110028.dPort, tcp.dstPort);
	modify_field(meta_map_init_110028.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_110028.sPort, tcp.srcPort);
	modify_field(meta_map_init_110028.dIP, ipv4.dstAddr);
}

header_type meta_map_init_110028_t {
	 fields {
		qid: 16;
		dPort: 16;
		dMac: 48;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_110028_t meta_map_init_110028;

table map_110028_2{
	actions{
		do_map_110028_2;
	}
}

action do_map_110028_2() {
	bit_and(meta_map_init_110028.dIP, meta_map_init_110028.dIP, 0xfffffff0);
}

header_type meta_distinct_3_110028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_110028_t meta_distinct_3_110028;

header_type hash_meta_distinct_3_110028_t {
	fields {
		dPort : 16;
		dMac : 48;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_110028_t hash_meta_distinct_3_110028;

field_list distinct_3_110028_fields {
	hash_meta_distinct_3_110028.dPort;
	hash_meta_distinct_3_110028.dMac;
	hash_meta_distinct_3_110028.sPort;
	hash_meta_distinct_3_110028.dIP;
}

field_list_calculation distinct_3_110028_fields_hash {
	input {
		distinct_3_110028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_110028{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_110028_regs() {
	bit_or(meta_distinct_3_110028.val,meta_distinct_3_110028.val, 1);
	register_write(distinct_3_110028,meta_distinct_3_110028.idx,meta_distinct_3_110028.val);
}

table update_distinct_3_110028_counts {
	actions {update_distinct_3_110028_regs;}
	size : 1;
}

action do_distinct_3_110028_hashes() {
	modify_field(hash_meta_distinct_3_110028.dPort, meta_map_init_110028.dPort);
	modify_field(hash_meta_distinct_3_110028.dMac, meta_map_init_110028.dMac);
	modify_field(hash_meta_distinct_3_110028.sPort, meta_map_init_110028.sPort);
	modify_field(hash_meta_distinct_3_110028.dIP, meta_map_init_110028.dIP);
	modify_field(meta_distinct_3_110028.qid, 110028);
	modify_field_with_hash_based_offset(meta_distinct_3_110028.idx, 0, distinct_3_110028_fields_hash, 4096);
	register_read(meta_distinct_3_110028.val, distinct_3_110028, meta_distinct_3_110028.idx);
}

table start_distinct_3_110028 {
	actions {do_distinct_3_110028_hashes;}
	size : 1;
}

action set_distinct_3_110028_count() {
	modify_field(meta_distinct_3_110028.val, 1);
}

table set_distinct_3_110028_count {
	actions {set_distinct_3_110028_count;}
        size: 1;
}

header_type meta_reduce_4_110028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_110028_t meta_reduce_4_110028;

header_type hash_meta_reduce_4_110028_t {
	fields {
		dPort : 16;
		sPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_110028_t hash_meta_reduce_4_110028;

field_list reduce_4_110028_fields {
	hash_meta_reduce_4_110028.dPort;
	hash_meta_reduce_4_110028.sPort;
	hash_meta_reduce_4_110028.dIP;
}

field_list_calculation reduce_4_110028_fields_hash {
	input {
		reduce_4_110028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_110028{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_110028_regs() {
	add_to_field(meta_reduce_4_110028.val, 1);
	register_write(reduce_4_110028,meta_reduce_4_110028.idx,meta_reduce_4_110028.val);
}

table update_reduce_4_110028_counts {
	actions {update_reduce_4_110028_regs;}
	size : 1;
}

action do_reduce_4_110028_hashes() {
	modify_field(hash_meta_reduce_4_110028.dPort, meta_map_init_110028.dPort);
	modify_field(hash_meta_reduce_4_110028.sPort, meta_map_init_110028.sPort);
	modify_field(hash_meta_reduce_4_110028.dIP, meta_map_init_110028.dIP);
	modify_field(meta_reduce_4_110028.qid, 110028);
	modify_field_with_hash_based_offset(meta_reduce_4_110028.idx, 0, reduce_4_110028_fields_hash, 4096);
	register_read(meta_reduce_4_110028.val, reduce_4_110028, meta_reduce_4_110028.idx);
}

table start_reduce_4_110028 {
	actions {do_reduce_4_110028_hashes;}
	size : 1;
}

action set_reduce_4_110028_count() {
	modify_field(meta_reduce_4_110028.val, 1);
}

table set_reduce_4_110028_count {
	actions {set_reduce_4_110028_count;}
        size: 1;
}

header_type meta_reduce_5_110028_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_110028_t meta_reduce_5_110028;

header_type hash_meta_reduce_5_110028_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_5_110028_t hash_meta_reduce_5_110028;

field_list reduce_5_110028_fields {
	hash_meta_reduce_5_110028.dIP;
}

field_list_calculation reduce_5_110028_fields_hash {
	input {
		reduce_5_110028_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_110028{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_110028_regs() {
	add_to_field(meta_reduce_5_110028.val, 1);
	register_write(reduce_5_110028,meta_reduce_5_110028.idx,meta_reduce_5_110028.val);
}

table update_reduce_5_110028_counts {
	actions {update_reduce_5_110028_regs;}
	size : 1;
}

action do_reduce_5_110028_hashes() {
	modify_field(hash_meta_reduce_5_110028.dIP, meta_map_init_110028.dIP);
	modify_field(meta_reduce_5_110028.qid, 110028);
	modify_field_with_hash_based_offset(meta_reduce_5_110028.idx, 0, reduce_5_110028_fields_hash, 4096);
	register_read(meta_reduce_5_110028.val, reduce_5_110028, meta_reduce_5_110028.idx);
}

table start_reduce_5_110028 {
	actions {do_reduce_5_110028_hashes;}
	size : 1;
}

action set_reduce_5_110028_count() {
	modify_field(meta_reduce_5_110028.val, 1);
}

table set_reduce_5_110028_count {
	actions {set_reduce_5_110028_count;}
        size: 1;
}

table map_init_110032{
	actions{
		do_map_init_110032;
	}
}

action do_map_init_110032(){
	modify_field(meta_map_init_110032.qid, 110032);
	modify_field(meta_map_init_110032.dPort, tcp.dstPort);
	modify_field(meta_map_init_110032.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_110032.sPort, tcp.srcPort);
	modify_field(meta_map_init_110032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_110032_t {
	 fields {
		qid: 16;
		dPort: 16;
		dMac: 48;
		sPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_110032_t meta_map_init_110032;

table map_110032_2{
	actions{
		do_map_110032_2;
	}
}

action do_map_110032_2() {
	bit_and(meta_map_init_110032.dIP, meta_map_init_110032.dIP, 0xffffffff);
}

table map_init_50004{
	actions{
		do_map_init_50004;
	}
}

action do_map_init_50004(){
	modify_field(meta_map_init_50004.qid, 50004);
	modify_field(meta_map_init_50004.sIP, ipv4.srcAddr);
}

header_type meta_map_init_50004_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_50004_t meta_map_init_50004;

table map_50004_1{
	actions{
		do_map_50004_1;
	}
}

action do_map_50004_1() {
	bit_and(meta_map_init_50004.sIP, meta_map_init_50004.sIP, 0xf0000000);
}

header_type meta_reduce_2_50004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_50004_t meta_reduce_2_50004;

header_type hash_meta_reduce_2_50004_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_2_50004_t hash_meta_reduce_2_50004;

field_list reduce_2_50004_fields {
	hash_meta_reduce_2_50004.sIP;
}

field_list_calculation reduce_2_50004_fields_hash {
	input {
		reduce_2_50004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_2_50004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_2_50004_regs() {
	add_to_field(meta_reduce_2_50004.val, 1);
	register_write(reduce_2_50004,meta_reduce_2_50004.idx,meta_reduce_2_50004.val);
}

table update_reduce_2_50004_counts {
	actions {update_reduce_2_50004_regs;}
	size : 1;
}

action do_reduce_2_50004_hashes() {
	modify_field(hash_meta_reduce_2_50004.sIP, meta_map_init_50004.sIP);
	modify_field(meta_reduce_2_50004.qid, 50004);
	modify_field_with_hash_based_offset(meta_reduce_2_50004.idx, 0, reduce_2_50004_fields_hash, 4096);
	register_read(meta_reduce_2_50004.val, reduce_2_50004, meta_reduce_2_50004.idx);
}

table start_reduce_2_50004 {
	actions {do_reduce_2_50004_hashes;}
	size : 1;
}

action set_reduce_2_50004_count() {
	modify_field(meta_reduce_2_50004.val, 1);
}

table set_reduce_2_50004_count {
	actions {set_reduce_2_50004_count;}
        size: 1;
}

table map_init_130012{
	actions{
		do_map_init_130012;
	}
}

action do_map_init_130012(){
	modify_field(meta_map_init_130012.qid, 130012);
	modify_field(meta_map_init_130012.dIP, ipv4.dstAddr);
}

header_type meta_map_init_130012_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_130012_t meta_map_init_130012;

table map_130012_2{
	actions{
		do_map_130012_2;
	}
}

action do_map_130012_2() {
	bit_and(meta_map_init_130012.dIP, meta_map_init_130012.dIP, 0xfff00000);
}

table map_init_40032{
	actions{
		do_map_init_40032;
	}
}

action do_map_init_40032(){
	modify_field(meta_map_init_40032.qid, 40032);
	modify_field(meta_map_init_40032.sMac, ethernet.srcAddr);
	modify_field(meta_map_init_40032.dMac, ethernet.dstAddr);
	modify_field(meta_map_init_40032.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_40032.nBytes, ipv4.totalLen);
	modify_field(meta_map_init_40032.proto, ipv4.protocol);
	modify_field(meta_map_init_40032.dPort, tcp.dstPort);
	modify_field(meta_map_init_40032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_40032_t {
	 fields {
		qid: 16;
		sMac: 48;
		dMac: 48;
		sIP: 32;
		nBytes: 16;
		proto: 16;
		dPort: 16;
		dIP: 32;
	}
}

metadata meta_map_init_40032_t meta_map_init_40032;

table map_40032_2{
	actions{
		do_map_40032_2;
	}
}

action do_map_40032_2() {
	bit_and(meta_map_init_40032.sIP, meta_map_init_40032.sIP, 0xffffffff);
}

header_type meta_distinct_3_40032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_40032_t meta_distinct_3_40032;

header_type hash_meta_distinct_3_40032_t {
	fields {
		dMac : 48;
		sIP : 32;
		proto : 16;
		sMac : 48;
		nBytes : 16;
		dPort : 16;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_40032_t hash_meta_distinct_3_40032;

field_list distinct_3_40032_fields {
	hash_meta_distinct_3_40032.dMac;
	hash_meta_distinct_3_40032.sIP;
	hash_meta_distinct_3_40032.proto;
	hash_meta_distinct_3_40032.sMac;
	hash_meta_distinct_3_40032.nBytes;
	hash_meta_distinct_3_40032.dPort;
	hash_meta_distinct_3_40032.dIP;
}

field_list_calculation distinct_3_40032_fields_hash {
	input {
		distinct_3_40032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_40032{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_40032_regs() {
	bit_or(meta_distinct_3_40032.val,meta_distinct_3_40032.val, 1);
	register_write(distinct_3_40032,meta_distinct_3_40032.idx,meta_distinct_3_40032.val);
}

table update_distinct_3_40032_counts {
	actions {update_distinct_3_40032_regs;}
	size : 1;
}

action do_distinct_3_40032_hashes() {
	modify_field(hash_meta_distinct_3_40032.dMac, meta_map_init_40032.dMac);
	modify_field(hash_meta_distinct_3_40032.sIP, meta_map_init_40032.sIP);
	modify_field(hash_meta_distinct_3_40032.proto, meta_map_init_40032.proto);
	modify_field(hash_meta_distinct_3_40032.sMac, meta_map_init_40032.sMac);
	modify_field(hash_meta_distinct_3_40032.nBytes, meta_map_init_40032.nBytes);
	modify_field(hash_meta_distinct_3_40032.dPort, meta_map_init_40032.dPort);
	modify_field(hash_meta_distinct_3_40032.dIP, meta_map_init_40032.dIP);
	modify_field(meta_distinct_3_40032.qid, 40032);
	modify_field_with_hash_based_offset(meta_distinct_3_40032.idx, 0, distinct_3_40032_fields_hash, 4096);
	register_read(meta_distinct_3_40032.val, distinct_3_40032, meta_distinct_3_40032.idx);
}

table start_distinct_3_40032 {
	actions {do_distinct_3_40032_hashes;}
	size : 1;
}

action set_distinct_3_40032_count() {
	modify_field(meta_distinct_3_40032.val, 1);
}

table set_distinct_3_40032_count {
	actions {set_distinct_3_40032_count;}
        size: 1;
}

header_type meta_reduce_4_40032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_40032_t meta_reduce_4_40032;

header_type hash_meta_reduce_4_40032_t {
	fields {
		sIP : 32;
		nBytes : 16;
	}
}

metadata hash_meta_reduce_4_40032_t hash_meta_reduce_4_40032;

field_list reduce_4_40032_fields {
	hash_meta_reduce_4_40032.sIP;
	hash_meta_reduce_4_40032.nBytes;
}

field_list_calculation reduce_4_40032_fields_hash {
	input {
		reduce_4_40032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_40032{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_40032_regs() {
	add_to_field(meta_reduce_4_40032.val, 1);
	register_write(reduce_4_40032,meta_reduce_4_40032.idx,meta_reduce_4_40032.val);
}

table update_reduce_4_40032_counts {
	actions {update_reduce_4_40032_regs;}
	size : 1;
}

action do_reduce_4_40032_hashes() {
	modify_field(hash_meta_reduce_4_40032.sIP, meta_map_init_40032.sIP);
	modify_field(hash_meta_reduce_4_40032.nBytes, meta_map_init_40032.nBytes);
	modify_field(meta_reduce_4_40032.qid, 40032);
	modify_field_with_hash_based_offset(meta_reduce_4_40032.idx, 0, reduce_4_40032_fields_hash, 4096);
	register_read(meta_reduce_4_40032.val, reduce_4_40032, meta_reduce_4_40032.idx);
}

table start_reduce_4_40032 {
	actions {do_reduce_4_40032_hashes;}
	size : 1;
}

action set_reduce_4_40032_count() {
	modify_field(meta_reduce_4_40032.val, 1);
}

table set_reduce_4_40032_count {
	actions {set_reduce_4_40032_count;}
        size: 1;
}

header_type meta_reduce_5_40032_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_5_40032_t meta_reduce_5_40032;

header_type hash_meta_reduce_5_40032_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_5_40032_t hash_meta_reduce_5_40032;

field_list reduce_5_40032_fields {
	hash_meta_reduce_5_40032.sIP;
}

field_list_calculation reduce_5_40032_fields_hash {
	input {
		reduce_5_40032_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_5_40032{
	width : 32;
	instance_count : 4096;
}

action update_reduce_5_40032_regs() {
	add_to_field(meta_reduce_5_40032.val, 1);
	register_write(reduce_5_40032,meta_reduce_5_40032.idx,meta_reduce_5_40032.val);
}

table update_reduce_5_40032_counts {
	actions {update_reduce_5_40032_regs;}
	size : 1;
}

action do_reduce_5_40032_hashes() {
	modify_field(hash_meta_reduce_5_40032.sIP, meta_map_init_40032.sIP);
	modify_field(meta_reduce_5_40032.qid, 40032);
	modify_field_with_hash_based_offset(meta_reduce_5_40032.idx, 0, reduce_5_40032_fields_hash, 4096);
	register_read(meta_reduce_5_40032.val, reduce_5_40032, meta_reduce_5_40032.idx);
}

table start_reduce_5_40032 {
	actions {do_reduce_5_40032_hashes;}
	size : 1;
}

action set_reduce_5_40032_count() {
	modify_field(meta_reduce_5_40032.val, 1);
}

table set_reduce_5_40032_count {
	actions {set_reduce_5_40032_count;}
        size: 1;
}

table map_init_140004{
	actions{
		do_map_init_140004;
	}
}

action do_map_init_140004(){
	modify_field(meta_map_init_140004.qid, 140004);
	modify_field(meta_map_init_140004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_140004_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_140004_t meta_map_init_140004;

table map_140004_1{
	actions{
		do_map_140004_1;
	}
}

action do_map_140004_1() {
	bit_and(meta_map_init_140004.dIP, meta_map_init_140004.dIP, 0xf0000000);
}

header_type meta_reduce_2_140004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_140004_t meta_reduce_2_140004;

header_type hash_meta_reduce_2_140004_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_2_140004_t hash_meta_reduce_2_140004;

field_list reduce_2_140004_fields {
	hash_meta_reduce_2_140004.dIP;
}

field_list_calculation reduce_2_140004_fields_hash {
	input {
		reduce_2_140004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_2_140004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_2_140004_regs() {
	add_to_field(meta_reduce_2_140004.val, 1);
	register_write(reduce_2_140004,meta_reduce_2_140004.idx,meta_reduce_2_140004.val);
}

table update_reduce_2_140004_counts {
	actions {update_reduce_2_140004_regs;}
	size : 1;
}

action do_reduce_2_140004_hashes() {
	modify_field(hash_meta_reduce_2_140004.dIP, meta_map_init_140004.dIP);
	modify_field(meta_reduce_2_140004.qid, 140004);
	modify_field_with_hash_based_offset(meta_reduce_2_140004.idx, 0, reduce_2_140004_fields_hash, 4096);
	register_read(meta_reduce_2_140004.val, reduce_2_140004, meta_reduce_2_140004.idx);
}

table start_reduce_2_140004 {
	actions {do_reduce_2_140004_hashes;}
	size : 1;
}

action set_reduce_2_140004_count() {
	modify_field(meta_reduce_2_140004.val, 1);
}

table set_reduce_2_140004_count {
	actions {set_reduce_2_140004_count;}
        size: 1;
}

table map_init_50012{
	actions{
		do_map_init_50012;
	}
}

action do_map_init_50012(){
	modify_field(meta_map_init_50012.qid, 50012);
	modify_field(meta_map_init_50012.sIP, ipv4.srcAddr);
}

header_type meta_map_init_50012_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_50012_t meta_map_init_50012;

table map_50012_2{
	actions{
		do_map_50012_2;
	}
}

action do_map_50012_2() {
	bit_and(meta_map_init_50012.sIP, meta_map_init_50012.sIP, 0xfff00000);
}

header_type meta_reduce_3_50012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_50012_t meta_reduce_3_50012;

header_type hash_meta_reduce_3_50012_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_3_50012_t hash_meta_reduce_3_50012;

field_list reduce_3_50012_fields {
	hash_meta_reduce_3_50012.sIP;
}

field_list_calculation reduce_3_50012_fields_hash {
	input {
		reduce_3_50012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_50012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_50012_regs() {
	add_to_field(meta_reduce_3_50012.val, 1);
	register_write(reduce_3_50012,meta_reduce_3_50012.idx,meta_reduce_3_50012.val);
}

table update_reduce_3_50012_counts {
	actions {update_reduce_3_50012_regs;}
	size : 1;
}

action do_reduce_3_50012_hashes() {
	modify_field(hash_meta_reduce_3_50012.sIP, meta_map_init_50012.sIP);
	modify_field(meta_reduce_3_50012.qid, 50012);
	modify_field_with_hash_based_offset(meta_reduce_3_50012.idx, 0, reduce_3_50012_fields_hash, 4096);
	register_read(meta_reduce_3_50012.val, reduce_3_50012, meta_reduce_3_50012.idx);
}

table start_reduce_3_50012 {
	actions {do_reduce_3_50012_hashes;}
	size : 1;
}

action set_reduce_3_50012_count() {
	modify_field(meta_reduce_3_50012.val, 1);
}

table set_reduce_3_50012_count {
	actions {set_reduce_3_50012_count;}
        size: 1;
}

table map_init_140012{
	actions{
		do_map_init_140012;
	}
}

action do_map_init_140012(){
	modify_field(meta_map_init_140012.qid, 140012);
	modify_field(meta_map_init_140012.dIP, ipv4.dstAddr);
}

header_type meta_map_init_140012_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_140012_t meta_map_init_140012;

table map_140012_2{
	actions{
		do_map_140012_2;
	}
}

action do_map_140012_2() {
	bit_and(meta_map_init_140012.dIP, meta_map_init_140012.dIP, 0xfff00000);
}

table map_init_130032{
	actions{
		do_map_init_130032;
	}
}

action do_map_init_130032(){
	modify_field(meta_map_init_130032.qid, 130032);
	modify_field(meta_map_init_130032.dIP, ipv4.dstAddr);
}

header_type meta_map_init_130032_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_130032_t meta_map_init_130032;

table map_130032_2{
	actions{
		do_map_130032_2;
	}
}

action do_map_130032_2() {
	bit_and(meta_map_init_130032.dIP, meta_map_init_130032.dIP, 0xffffffff);
}

table map_init_140008{
	actions{
		do_map_init_140008;
	}
}

action do_map_init_140008(){
	modify_field(meta_map_init_140008.qid, 140008);
	modify_field(meta_map_init_140008.dIP, ipv4.dstAddr);
}

header_type meta_map_init_140008_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_140008_t meta_map_init_140008;

table map_140008_2{
	actions{
		do_map_140008_2;
	}
}

action do_map_140008_2() {
	bit_and(meta_map_init_140008.dIP, meta_map_init_140008.dIP, 0xff000000);
}

header_type meta_reduce_3_140008_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_140008_t meta_reduce_3_140008;

header_type hash_meta_reduce_3_140008_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_140008_t hash_meta_reduce_3_140008;

field_list reduce_3_140008_fields {
	hash_meta_reduce_3_140008.dIP;
}

field_list_calculation reduce_3_140008_fields_hash {
	input {
		reduce_3_140008_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_140008{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_140008_regs() {
	add_to_field(meta_reduce_3_140008.val, 1);
	register_write(reduce_3_140008,meta_reduce_3_140008.idx,meta_reduce_3_140008.val);
}

table update_reduce_3_140008_counts {
	actions {update_reduce_3_140008_regs;}
	size : 1;
}

action do_reduce_3_140008_hashes() {
	modify_field(hash_meta_reduce_3_140008.dIP, meta_map_init_140008.dIP);
	modify_field(meta_reduce_3_140008.qid, 140008);
	modify_field_with_hash_based_offset(meta_reduce_3_140008.idx, 0, reduce_3_140008_fields_hash, 4096);
	register_read(meta_reduce_3_140008.val, reduce_3_140008, meta_reduce_3_140008.idx);
}

table start_reduce_3_140008 {
	actions {do_reduce_3_140008_hashes;}
	size : 1;
}

action set_reduce_3_140008_count() {
	modify_field(meta_reduce_3_140008.val, 1);
}

table set_reduce_3_140008_count {
	actions {set_reduce_3_140008_count;}
        size: 1;
}

table map_init_70004{
	actions{
		do_map_init_70004;
	}
}

action do_map_init_70004(){
	modify_field(meta_map_init_70004.qid, 70004);
	modify_field(meta_map_init_70004.sIP, ipv4.srcAddr);
}

header_type meta_map_init_70004_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_70004_t meta_map_init_70004;

table map_70004_2{
	actions{
		do_map_70004_2;
	}
}

action do_map_70004_2() {
	bit_and(meta_map_init_70004.sIP, meta_map_init_70004.sIP, 0xf0000000);
}

header_type meta_reduce_3_70004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_70004_t meta_reduce_3_70004;

header_type hash_meta_reduce_3_70004_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_3_70004_t hash_meta_reduce_3_70004;

field_list reduce_3_70004_fields {
	hash_meta_reduce_3_70004.sIP;
}

field_list_calculation reduce_3_70004_fields_hash {
	input {
		reduce_3_70004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_70004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_70004_regs() {
	add_to_field(meta_reduce_3_70004.val, 1);
	register_write(reduce_3_70004,meta_reduce_3_70004.idx,meta_reduce_3_70004.val);
}

table update_reduce_3_70004_counts {
	actions {update_reduce_3_70004_regs;}
	size : 1;
}

action do_reduce_3_70004_hashes() {
	modify_field(hash_meta_reduce_3_70004.sIP, meta_map_init_70004.sIP);
	modify_field(meta_reduce_3_70004.qid, 70004);
	modify_field_with_hash_based_offset(meta_reduce_3_70004.idx, 0, reduce_3_70004_fields_hash, 4096);
	register_read(meta_reduce_3_70004.val, reduce_3_70004, meta_reduce_3_70004.idx);
}

table start_reduce_3_70004 {
	actions {do_reduce_3_70004_hashes;}
	size : 1;
}

action set_reduce_3_70004_count() {
	modify_field(meta_reduce_3_70004.val, 1);
}

table set_reduce_3_70004_count {
	actions {set_reduce_3_70004_count;}
        size: 1;
}

table map_init_130004{
	actions{
		do_map_init_130004;
	}
}

action do_map_init_130004(){
	modify_field(meta_map_init_130004.qid, 130004);
	modify_field(meta_map_init_130004.dIP, ipv4.dstAddr);
}

header_type meta_map_init_130004_t {
	 fields {
		qid: 16;
		dIP: 32;
	}
}

metadata meta_map_init_130004_t meta_map_init_130004;

table map_130004_2{
	actions{
		do_map_130004_2;
	}
}

action do_map_130004_2() {
	bit_and(meta_map_init_130004.dIP, meta_map_init_130004.dIP, 0xf0000000);
}

header_type meta_reduce_3_130004_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_130004_t meta_reduce_3_130004;

header_type hash_meta_reduce_3_130004_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_3_130004_t hash_meta_reduce_3_130004;

field_list reduce_3_130004_fields {
	hash_meta_reduce_3_130004.dIP;
}

field_list_calculation reduce_3_130004_fields_hash {
	input {
		reduce_3_130004_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_130004{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_130004_regs() {
	add_to_field(meta_reduce_3_130004.val, 1);
	register_write(reduce_3_130004,meta_reduce_3_130004.idx,meta_reduce_3_130004.val);
}

table update_reduce_3_130004_counts {
	actions {update_reduce_3_130004_regs;}
	size : 1;
}

action do_reduce_3_130004_hashes() {
	modify_field(hash_meta_reduce_3_130004.dIP, meta_map_init_130004.dIP);
	modify_field(meta_reduce_3_130004.qid, 130004);
	modify_field_with_hash_based_offset(meta_reduce_3_130004.idx, 0, reduce_3_130004_fields_hash, 4096);
	register_read(meta_reduce_3_130004.val, reduce_3_130004, meta_reduce_3_130004.idx);
}

table start_reduce_3_130004 {
	actions {do_reduce_3_130004_hashes;}
	size : 1;
}

action set_reduce_3_130004_count() {
	modify_field(meta_reduce_3_130004.val, 1);
}

table set_reduce_3_130004_count {
	actions {set_reduce_3_130004_count;}
        size: 1;
}

table map_init_70012{
	actions{
		do_map_init_70012;
	}
}

action do_map_init_70012(){
	modify_field(meta_map_init_70012.qid, 70012);
	modify_field(meta_map_init_70012.sIP, ipv4.srcAddr);
}

header_type meta_map_init_70012_t {
	 fields {
		qid: 16;
		sIP: 32;
	}
}

metadata meta_map_init_70012_t meta_map_init_70012;

table map_70012_2{
	actions{
		do_map_70012_2;
	}
}

action do_map_70012_2() {
	bit_and(meta_map_init_70012.sIP, meta_map_init_70012.sIP, 0xfff00000);
}

header_type meta_reduce_3_70012_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_70012_t meta_reduce_3_70012;

header_type hash_meta_reduce_3_70012_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_3_70012_t hash_meta_reduce_3_70012;

field_list reduce_3_70012_fields {
	hash_meta_reduce_3_70012.sIP;
}

field_list_calculation reduce_3_70012_fields_hash {
	input {
		reduce_3_70012_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_70012{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_70012_regs() {
	add_to_field(meta_reduce_3_70012.val, 1);
	register_write(reduce_3_70012,meta_reduce_3_70012.idx,meta_reduce_3_70012.val);
}

table update_reduce_3_70012_counts {
	actions {update_reduce_3_70012_regs;}
	size : 1;
}

action do_reduce_3_70012_hashes() {
	modify_field(hash_meta_reduce_3_70012.sIP, meta_map_init_70012.sIP);
	modify_field(meta_reduce_3_70012.qid, 70012);
	modify_field_with_hash_based_offset(meta_reduce_3_70012.idx, 0, reduce_3_70012_fields_hash, 4096);
	register_read(meta_reduce_3_70012.val, reduce_3_70012, meta_reduce_3_70012.idx);
}

table start_reduce_3_70012 {
	actions {do_reduce_3_70012_hashes;}
	size : 1;
}

action set_reduce_3_70012_count() {
	modify_field(meta_reduce_3_70012.val, 1);
}

table set_reduce_3_70012_count {
	actions {set_reduce_3_70012_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_140032 : 1;
		qid_20032 : 1;
		qid_80004 : 1;
		qid_20012 : 1;
		qid_80012 : 1;
		qid_70032 : 1;
		qid_10012 : 1;
		qid_80032 : 1;
		qid_50032 : 1;
		qid_100004 : 1;
		qid_80028 : 1;
		qid_100012 : 1;
		qid_10032 : 1;
		qid_110004 : 1;
		qid_110012 : 1;
		qid_100032 : 1;
		qid_40004 : 1;
		qid_40012 : 1;
		qid_110028 : 1;
		qid_110032 : 1;
		qid_50004 : 1;
		qid_130012 : 1;
		qid_40032 : 1;
		qid_140004 : 1;
		qid_50012 : 1;
		qid_140012 : 1;
		qid_130032 : 1;
		qid_140008 : 1;
		qid_70004 : 1;
		qid_130004 : 1;
		qid_70012 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_140032, 1);
	modify_field(meta_fm.qid_20032, 1);
	modify_field(meta_fm.qid_80004, 1);
	modify_field(meta_fm.qid_20012, 1);
	modify_field(meta_fm.qid_80012, 1);
	modify_field(meta_fm.qid_70032, 1);
	modify_field(meta_fm.qid_10012, 1);
	modify_field(meta_fm.qid_80032, 1);
	modify_field(meta_fm.qid_50032, 1);
	modify_field(meta_fm.qid_100004, 1);
	modify_field(meta_fm.qid_80028, 1);
	modify_field(meta_fm.qid_100012, 1);
	modify_field(meta_fm.qid_10032, 1);
	modify_field(meta_fm.qid_110004, 1);
	modify_field(meta_fm.qid_110012, 1);
	modify_field(meta_fm.qid_100032, 1);
	modify_field(meta_fm.qid_40004, 1);
	modify_field(meta_fm.qid_40012, 1);
	modify_field(meta_fm.qid_110028, 1);
	modify_field(meta_fm.qid_110032, 1);
	modify_field(meta_fm.qid_50004, 1);
	modify_field(meta_fm.qid_130012, 1);
	modify_field(meta_fm.qid_40032, 1);
	modify_field(meta_fm.qid_140004, 1);
	modify_field(meta_fm.qid_50012, 1);
	modify_field(meta_fm.qid_140012, 1);
	modify_field(meta_fm.qid_130032, 1);
	modify_field(meta_fm.qid_140008, 1);
	modify_field(meta_fm.qid_70004, 1);
	modify_field(meta_fm.qid_130004, 1);
	modify_field(meta_fm.qid_70012, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_140032(){
	modify_field(meta_fm.qid_140032, 1);
}

action set_meta_fm_20032(){
	modify_field(meta_fm.qid_20032, 1);
}

action set_meta_fm_80004(){
	modify_field(meta_fm.qid_80004, 1);
}

action set_meta_fm_20012(){
	modify_field(meta_fm.qid_20012, 1);
}

action set_meta_fm_80012(){
	modify_field(meta_fm.qid_80012, 1);
}

action set_meta_fm_70032(){
	modify_field(meta_fm.qid_70032, 1);
}

action set_meta_fm_10012(){
	modify_field(meta_fm.qid_10012, 1);
}

action set_meta_fm_80032(){
	modify_field(meta_fm.qid_80032, 1);
}

action set_meta_fm_50032(){
	modify_field(meta_fm.qid_50032, 1);
}

action set_meta_fm_100004(){
	modify_field(meta_fm.qid_100004, 1);
}

action set_meta_fm_80028(){
	modify_field(meta_fm.qid_80028, 1);
}

action set_meta_fm_100012(){
	modify_field(meta_fm.qid_100012, 1);
}

action set_meta_fm_10032(){
	modify_field(meta_fm.qid_10032, 1);
}

action set_meta_fm_110004(){
	modify_field(meta_fm.qid_110004, 1);
}

action set_meta_fm_110012(){
	modify_field(meta_fm.qid_110012, 1);
}

action set_meta_fm_100032(){
	modify_field(meta_fm.qid_100032, 1);
}

action set_meta_fm_40004(){
	modify_field(meta_fm.qid_40004, 1);
}

action set_meta_fm_40012(){
	modify_field(meta_fm.qid_40012, 1);
}

action set_meta_fm_110028(){
	modify_field(meta_fm.qid_110028, 1);
}

action set_meta_fm_110032(){
	modify_field(meta_fm.qid_110032, 1);
}

action set_meta_fm_50004(){
	modify_field(meta_fm.qid_50004, 1);
}

action set_meta_fm_130012(){
	modify_field(meta_fm.qid_130012, 1);
}

action set_meta_fm_40032(){
	modify_field(meta_fm.qid_40032, 1);
}

action set_meta_fm_140004(){
	modify_field(meta_fm.qid_140004, 1);
}

action set_meta_fm_50012(){
	modify_field(meta_fm.qid_50012, 1);
}

action set_meta_fm_140012(){
	modify_field(meta_fm.qid_140012, 1);
}

action set_meta_fm_130032(){
	modify_field(meta_fm.qid_130032, 1);
}

action set_meta_fm_140008(){
	modify_field(meta_fm.qid_140008, 1);
}

action set_meta_fm_70004(){
	modify_field(meta_fm.qid_70004, 1);
}

action set_meta_fm_130004(){
	modify_field(meta_fm.qid_130004, 1);
}

action set_meta_fm_70012(){
	modify_field(meta_fm.qid_70012, 1);
}

action reset_meta_fm_140032(){
	modify_field(meta_fm.qid_140032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_20032(){
	modify_field(meta_fm.qid_20032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_80004(){
	modify_field(meta_fm.qid_80004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_20012(){
	modify_field(meta_fm.qid_20012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_80012(){
	modify_field(meta_fm.qid_80012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_70032(){
	modify_field(meta_fm.qid_70032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10012(){
	modify_field(meta_fm.qid_10012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_80032(){
	modify_field(meta_fm.qid_80032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_50032(){
	modify_field(meta_fm.qid_50032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_100004(){
	modify_field(meta_fm.qid_100004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_80028(){
	modify_field(meta_fm.qid_80028, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_100012(){
	modify_field(meta_fm.qid_100012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10032(){
	modify_field(meta_fm.qid_10032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_110004(){
	modify_field(meta_fm.qid_110004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_110012(){
	modify_field(meta_fm.qid_110012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_100032(){
	modify_field(meta_fm.qid_100032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40004(){
	modify_field(meta_fm.qid_40004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40012(){
	modify_field(meta_fm.qid_40012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_110028(){
	modify_field(meta_fm.qid_110028, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_110032(){
	modify_field(meta_fm.qid_110032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_50004(){
	modify_field(meta_fm.qid_50004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_130012(){
	modify_field(meta_fm.qid_130012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_40032(){
	modify_field(meta_fm.qid_40032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_140004(){
	modify_field(meta_fm.qid_140004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_50012(){
	modify_field(meta_fm.qid_50012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_140012(){
	modify_field(meta_fm.qid_140012, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_130032(){
	modify_field(meta_fm.qid_130032, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_140008(){
	modify_field(meta_fm.qid_140008, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_70004(){
	modify_field(meta_fm.qid_70004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_130004(){
	modify_field(meta_fm.qid_130004, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_70012(){
	modify_field(meta_fm.qid_70012, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_140032_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_140032;
		reset_meta_fm_140032;
	}
}

table filter_20032_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_20032;
		reset_meta_fm_20032;
	}
}

table filter_80012_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_80012;
		reset_meta_fm_80012;
	}
}

table filter_70032_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_70032;
		reset_meta_fm_70032;
	}
}

table filter_10012_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_10012;
		reset_meta_fm_10012;
	}
}

table filter_80032_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_80032;
		reset_meta_fm_80032;
	}
}

table filter_50032_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_50032;
		reset_meta_fm_50032;
	}
}

table filter_100004_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_100004;
		reset_meta_fm_100004;
	}
}

table filter_80028_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_80028;
		reset_meta_fm_80028;
	}
}

table filter_100012_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_100012;
		reset_meta_fm_100012;
	}
}

table filter_10032_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_10032;
		reset_meta_fm_10032;
	}
}

table filter_110012_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_110012;
		reset_meta_fm_110012;
	}
}

table filter_100032_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_100032;
		reset_meta_fm_100032;
	}
}

table filter_40004_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_40004;
		reset_meta_fm_40004;
	}
}

table filter_40012_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_40012;
		reset_meta_fm_40012;
	}
}

table filter_110028_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_110028;
		reset_meta_fm_110028;
	}
}

table filter_110032_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_110032;
		reset_meta_fm_110032;
	}
}

table filter_130012_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_130012;
		reset_meta_fm_130012;
	}
}

table filter_40032_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_40032;
		reset_meta_fm_40032;
	}
}

table filter_50012_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_50012;
		reset_meta_fm_50012;
	}
}

table filter_140012_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_140012;
		reset_meta_fm_140012;
	}
}

table filter_130032_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_130032;
		reset_meta_fm_130032;
	}
}

table filter_140008_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_140008;
		reset_meta_fm_140008;
	}
}

table filter_70004_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_70004;
		reset_meta_fm_70004;
	}
}

table filter_130004_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_130004;
		reset_meta_fm_130004;
	}
}

table filter_70012_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_70012;
		reset_meta_fm_70012;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_140032== 1){
			apply(filter_140032_1);
		}
		if (meta_fm.qid_140032 == 1){
					apply(map_init_140032);
			apply(map_140032_2);
			apply(start_reduce_3_140032);
			apply(update_reduce_3_140032_counts);
			if(meta_reduce_3_140032.val > 99) {
				apply(set_reduce_3_140032_count);			}
			else if(meta_reduce_3_140032.val == 99) {
				apply(skip_reduce_3_140032_1);
			}
			else {
				apply(drop_reduce_3_140032_1);
			}

			apply(copy_to_cpu_140032);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_20032== 1){
			apply(filter_20032_1);
		}
		if (meta_fm.qid_20032 == 1){
					apply(map_init_20032);
			apply(map_20032_2);
			apply(start_distinct_3_20032);
			apply(start_reduce_4_20032);
			if(meta_distinct_3_20032.val > 0) {
				apply(drop_distinct_3_20032_1);
			}
			else if(meta_distinct_3_20032.val == 0) {
				apply(skip_distinct_3_20032_1);
			}
			else {
				apply(drop_distinct_3_20032_2);
			}

			apply(update_distinct_3_20032_counts);
			apply(update_reduce_4_20032_counts);
			if(meta_reduce_4_20032.val > 57) {
				apply(set_reduce_4_20032_count);			}
			else if(meta_reduce_4_20032.val == 57) {
				apply(skip_reduce_4_20032_1);
			}
			else {
				apply(drop_reduce_4_20032_1);
			}

			apply(copy_to_cpu_20032);
		}
	}
	if (meta_fm.f1 == 2){
		if (meta_fm.qid_80004 == 1){
					apply(map_init_80004);
			apply(map_80004_1);
			apply(start_reduce_2_80004);
			apply(start_distinct_3_80004);
			apply(start_reduce_4_80004);
			apply(update_reduce_2_80004_counts);
			if(meta_reduce_2_80004.val > 2) {
				apply(set_reduce_2_80004_count);			}
			else if(meta_reduce_2_80004.val == 2) {
				apply(skip_reduce_2_80004_1);
			}
			else {
				apply(drop_reduce_2_80004_1);
			}

			if(meta_distinct_3_80004.val > 0) {
				apply(drop_distinct_3_80004_1);
			}
			else if(meta_distinct_3_80004.val == 0) {
				apply(skip_distinct_3_80004_1);
			}
			else {
				apply(drop_distinct_3_80004_2);
			}

			apply(update_distinct_3_80004_counts);
			apply(update_reduce_4_80004_counts);
			if(meta_reduce_4_80004.val > 59) {
				apply(set_reduce_4_80004_count);			}
			else if(meta_reduce_4_80004.val == 59) {
				apply(skip_reduce_4_80004_1);
			}
			else {
				apply(drop_reduce_4_80004_1);
			}

			apply(copy_to_cpu_80004);
		}
	}
	if (meta_fm.f1 == 3){
		if (meta_fm.qid_20012 == 1){
					apply(map_init_20012);
			apply(map_20012_1);
			apply(start_distinct_2_20012);
			apply(start_reduce_3_20012);
			if(meta_distinct_2_20012.val > 0) {
				apply(drop_distinct_2_20012_1);
			}
			else if(meta_distinct_2_20012.val == 0) {
				apply(skip_distinct_2_20012_1);
			}
			else {
				apply(drop_distinct_2_20012_2);
			}

			apply(update_distinct_2_20012_counts);
			apply(update_reduce_3_20012_counts);
			if(meta_reduce_3_20012.val > 57) {
				apply(set_reduce_3_20012_count);			}
			else if(meta_reduce_3_20012.val == 57) {
				apply(skip_reduce_3_20012_1);
			}
			else {
				apply(drop_reduce_3_20012_1);
			}

			apply(copy_to_cpu_20012);
		}
	}
	if (meta_fm.f1 == 4){
		if (meta_fm.qid_80012== 1){
			apply(filter_80012_1);
		}
		if (meta_fm.qid_80012 == 1){
					apply(map_init_80012);
			apply(map_80012_2);
			apply(start_reduce_3_80012);
			apply(start_distinct_4_80012);
			apply(start_reduce_5_80012);
			apply(update_reduce_3_80012_counts);
			if(meta_reduce_3_80012.val > 2) {
				apply(set_reduce_3_80012_count);			}
			else if(meta_reduce_3_80012.val == 2) {
				apply(skip_reduce_3_80012_1);
			}
			else {
				apply(drop_reduce_3_80012_1);
			}

			if(meta_distinct_4_80012.val > 0) {
				apply(drop_distinct_4_80012_1);
			}
			else if(meta_distinct_4_80012.val == 0) {
				apply(skip_distinct_4_80012_1);
			}
			else {
				apply(drop_distinct_4_80012_2);
			}

			apply(update_distinct_4_80012_counts);
			apply(update_reduce_5_80012_counts);
			if(meta_reduce_5_80012.val > 59) {
				apply(set_reduce_5_80012_count);			}
			else if(meta_reduce_5_80012.val == 59) {
				apply(skip_reduce_5_80012_1);
			}
			else {
				apply(drop_reduce_5_80012_1);
			}

			apply(copy_to_cpu_80012);
		}
	}
	if (meta_fm.f1 == 5){
		if (meta_fm.qid_70032== 1){
			apply(filter_70032_1);
		}
		if (meta_fm.qid_70032 == 1){
					apply(map_init_70032);
			apply(map_70032_2);
			apply(copy_to_cpu_70032);
		}
	}
	if (meta_fm.f1 == 6){
		if (meta_fm.qid_10012== 1){
			apply(filter_10012_1);
		}
		if (meta_fm.qid_10012 == 1){
					apply(map_init_10012);
			apply(map_10012_2);
			apply(start_distinct_3_10012);
			if(meta_distinct_3_10012.val > 0) {
				apply(drop_distinct_3_10012_1);
			}
			else if(meta_distinct_3_10012.val == 0) {
				apply(skip_distinct_3_10012_1);
			}
			else {
				apply(drop_distinct_3_10012_2);
			}

			apply(update_distinct_3_10012_counts);
			apply(copy_to_cpu_10012);
		}
	}
	if (meta_fm.f1 == 7){
		if (meta_fm.qid_80032== 1){
			apply(filter_80032_1);
		}
		if (meta_fm.qid_80032 == 1){
					apply(map_init_80032);
			apply(map_80032_2);
			apply(start_reduce_3_80032);
			apply(update_reduce_3_80032_counts);
			if(meta_reduce_3_80032.val > 59) {
				apply(set_reduce_3_80032_count);			}
			else if(meta_reduce_3_80032.val == 59) {
				apply(skip_reduce_3_80032_1);
			}
			else {
				apply(drop_reduce_3_80032_1);
			}

			apply(copy_to_cpu_80032);
		}
	}
	if (meta_fm.f1 == 8){
		if (meta_fm.qid_50032== 1){
			apply(filter_50032_1);
		}
		if (meta_fm.qid_50032 == 1){
					apply(map_init_50032);
			apply(map_50032_2);
			apply(start_reduce_3_50032);
			apply(update_reduce_3_50032_counts);
			if(meta_reduce_3_50032.val > 59) {
				apply(set_reduce_3_50032_count);			}
			else if(meta_reduce_3_50032.val == 59) {
				apply(skip_reduce_3_50032_1);
			}
			else {
				apply(drop_reduce_3_50032_1);
			}

			apply(copy_to_cpu_50032);
		}
	}
	if (meta_fm.f1 == 9){
		if (meta_fm.qid_100004== 1){
			apply(filter_100004_1);
		}
		if (meta_fm.qid_100004 == 1){
					apply(map_init_100004);
			apply(map_100004_2);
			apply(start_distinct_3_100004);
			if(meta_distinct_3_100004.val > 0) {
				apply(drop_distinct_3_100004_1);
			}
			else if(meta_distinct_3_100004.val == 0) {
				apply(skip_distinct_3_100004_1);
			}
			else {
				apply(drop_distinct_3_100004_2);
			}

			apply(update_distinct_3_100004_counts);
			apply(copy_to_cpu_100004);
		}
	}
	if (meta_fm.f1 == 10){
		if (meta_fm.qid_80028== 1){
			apply(filter_80028_1);
		}
		if (meta_fm.qid_80028 == 1){
					apply(map_init_80028);
			apply(map_80028_2);
			apply(start_reduce_3_80028);
			apply(start_distinct_4_80028);
			apply(start_reduce_5_80028);
			apply(update_reduce_3_80028_counts);
			if(meta_reduce_3_80028.val > 2) {
				apply(set_reduce_3_80028_count);			}
			else if(meta_reduce_3_80028.val == 2) {
				apply(skip_reduce_3_80028_1);
			}
			else {
				apply(drop_reduce_3_80028_1);
			}

			if(meta_distinct_4_80028.val > 0) {
				apply(drop_distinct_4_80028_1);
			}
			else if(meta_distinct_4_80028.val == 0) {
				apply(skip_distinct_4_80028_1);
			}
			else {
				apply(drop_distinct_4_80028_2);
			}

			apply(update_distinct_4_80028_counts);
			apply(update_reduce_5_80028_counts);
			if(meta_reduce_5_80028.val > 59) {
				apply(set_reduce_5_80028_count);			}
			else if(meta_reduce_5_80028.val == 59) {
				apply(skip_reduce_5_80028_1);
			}
			else {
				apply(drop_reduce_5_80028_1);
			}

			apply(copy_to_cpu_80028);
		}
	}
	if (meta_fm.f1 == 11){
		if (meta_fm.qid_100012== 1){
			apply(filter_100012_1);
		}
		if (meta_fm.qid_100012 == 1){
					apply(map_init_100012);
			apply(map_100012_2);
			apply(start_distinct_3_100012);
			if(meta_distinct_3_100012.val > 0) {
				apply(drop_distinct_3_100012_1);
			}
			else if(meta_distinct_3_100012.val == 0) {
				apply(skip_distinct_3_100012_1);
			}
			else {
				apply(drop_distinct_3_100012_2);
			}

			apply(update_distinct_3_100012_counts);
			apply(copy_to_cpu_100012);
		}
	}
	if (meta_fm.f1 == 12){
		if (meta_fm.qid_10032== 1){
			apply(filter_10032_1);
		}
		if (meta_fm.qid_10032 == 1){
					apply(map_init_10032);
			apply(map_10032_2);
			apply(start_distinct_3_10032);
			if(meta_distinct_3_10032.val > 0) {
				apply(drop_distinct_3_10032_1);
			}
			else if(meta_distinct_3_10032.val == 0) {
				apply(skip_distinct_3_10032_1);
			}
			else {
				apply(drop_distinct_3_10032_2);
			}

			apply(update_distinct_3_10032_counts);
			apply(copy_to_cpu_10032);
		}
	}
	if (meta_fm.f1 == 13){
		if (meta_fm.qid_110004 == 1){
					apply(map_init_110004);
			apply(map_110004_1);
			apply(start_distinct_2_110004);
			apply(start_reduce_3_110004);
			apply(start_reduce_4_110004);
			if(meta_distinct_2_110004.val > 0) {
				apply(drop_distinct_2_110004_1);
			}
			else if(meta_distinct_2_110004.val == 0) {
				apply(skip_distinct_2_110004_1);
			}
			else {
				apply(drop_distinct_2_110004_2);
			}

			apply(update_distinct_2_110004_counts);
			apply(update_reduce_3_110004_counts);
			if(meta_reduce_3_110004.val > 2) {
				apply(set_reduce_3_110004_count);			}
			else if(meta_reduce_3_110004.val == 2) {
				apply(skip_reduce_3_110004_1);
			}
			else {
				apply(drop_reduce_3_110004_1);
			}

			apply(update_reduce_4_110004_counts);
			if(meta_reduce_4_110004.val > 79) {
				apply(set_reduce_4_110004_count);			}
			else if(meta_reduce_4_110004.val == 79) {
				apply(skip_reduce_4_110004_1);
			}
			else {
				apply(drop_reduce_4_110004_1);
			}

			apply(copy_to_cpu_110004);
		}
	}
	if (meta_fm.f1 == 14){
		if (meta_fm.qid_110012== 1){
			apply(filter_110012_1);
		}
		if (meta_fm.qid_110012 == 1){
					apply(map_init_110012);
			apply(map_110012_2);
			apply(start_distinct_3_110012);
			apply(start_reduce_4_110012);
			apply(start_reduce_5_110012);
			if(meta_distinct_3_110012.val > 0) {
				apply(drop_distinct_3_110012_1);
			}
			else if(meta_distinct_3_110012.val == 0) {
				apply(skip_distinct_3_110012_1);
			}
			else {
				apply(drop_distinct_3_110012_2);
			}

			apply(update_distinct_3_110012_counts);
			apply(update_reduce_4_110012_counts);
			if(meta_reduce_4_110012.val > 2) {
				apply(set_reduce_4_110012_count);			}
			else if(meta_reduce_4_110012.val == 2) {
				apply(skip_reduce_4_110012_1);
			}
			else {
				apply(drop_reduce_4_110012_1);
			}

			apply(update_reduce_5_110012_counts);
			if(meta_reduce_5_110012.val > 79) {
				apply(set_reduce_5_110012_count);			}
			else if(meta_reduce_5_110012.val == 79) {
				apply(skip_reduce_5_110012_1);
			}
			else {
				apply(drop_reduce_5_110012_1);
			}

			apply(copy_to_cpu_110012);
		}
	}
	if (meta_fm.f1 == 15){
		if (meta_fm.qid_100032== 1){
			apply(filter_100032_1);
		}
		if (meta_fm.qid_100032 == 1){
					apply(map_init_100032);
			apply(map_100032_2);
			apply(copy_to_cpu_100032);
		}
	}
	if (meta_fm.f1 == 16){
		if (meta_fm.qid_40004== 1){
			apply(filter_40004_1);
		}
		if (meta_fm.qid_40004 == 1){
					apply(map_init_40004);
			apply(map_40004_2);
			apply(start_distinct_3_40004);
			if(meta_distinct_3_40004.val > 0) {
				apply(drop_distinct_3_40004_1);
			}
			else if(meta_distinct_3_40004.val == 0) {
				apply(skip_distinct_3_40004_1);
			}
			else {
				apply(drop_distinct_3_40004_2);
			}

			apply(update_distinct_3_40004_counts);
			apply(copy_to_cpu_40004);
		}
	}
	if (meta_fm.f1 == 17){
		if (meta_fm.qid_40012== 1){
			apply(filter_40012_1);
		}
		if (meta_fm.qid_40012 == 1){
					apply(map_init_40012);
			apply(map_40012_2);
			apply(start_distinct_3_40012);
			apply(start_reduce_4_40012);
			apply(start_reduce_5_40012);
			if(meta_distinct_3_40012.val > 0) {
				apply(drop_distinct_3_40012_1);
			}
			else if(meta_distinct_3_40012.val == 0) {
				apply(skip_distinct_3_40012_1);
			}
			else {
				apply(drop_distinct_3_40012_2);
			}

			apply(update_distinct_3_40012_counts);
			apply(update_reduce_4_40012_counts);
			if(meta_reduce_4_40012.val > 2) {
				apply(set_reduce_4_40012_count);			}
			else if(meta_reduce_4_40012.val == 2) {
				apply(skip_reduce_4_40012_1);
			}
			else {
				apply(drop_reduce_4_40012_1);
			}

			apply(update_reduce_5_40012_counts);
			if(meta_reduce_5_40012.val > 79) {
				apply(set_reduce_5_40012_count);			}
			else if(meta_reduce_5_40012.val == 79) {
				apply(skip_reduce_5_40012_1);
			}
			else {
				apply(drop_reduce_5_40012_1);
			}

			apply(copy_to_cpu_40012);
		}
	}
	if (meta_fm.f1 == 18){
		if (meta_fm.qid_110028== 1){
			apply(filter_110028_1);
		}
		if (meta_fm.qid_110028 == 1){
					apply(map_init_110028);
			apply(map_110028_2);
			apply(start_distinct_3_110028);
			apply(start_reduce_4_110028);
			apply(start_reduce_5_110028);
			if(meta_distinct_3_110028.val > 0) {
				apply(drop_distinct_3_110028_1);
			}
			else if(meta_distinct_3_110028.val == 0) {
				apply(skip_distinct_3_110028_1);
			}
			else {
				apply(drop_distinct_3_110028_2);
			}

			apply(update_distinct_3_110028_counts);
			apply(update_reduce_4_110028_counts);
			if(meta_reduce_4_110028.val > 2) {
				apply(set_reduce_4_110028_count);			}
			else if(meta_reduce_4_110028.val == 2) {
				apply(skip_reduce_4_110028_1);
			}
			else {
				apply(drop_reduce_4_110028_1);
			}

			apply(update_reduce_5_110028_counts);
			if(meta_reduce_5_110028.val > 79) {
				apply(set_reduce_5_110028_count);			}
			else if(meta_reduce_5_110028.val == 79) {
				apply(skip_reduce_5_110028_1);
			}
			else {
				apply(drop_reduce_5_110028_1);
			}

			apply(copy_to_cpu_110028);
		}
	}
	if (meta_fm.f1 == 19){
		if (meta_fm.qid_110032== 1){
			apply(filter_110032_1);
		}
		if (meta_fm.qid_110032 == 1){
					apply(map_init_110032);
			apply(map_110032_2);
			apply(copy_to_cpu_110032);
		}
	}
	if (meta_fm.f1 == 20){
		if (meta_fm.qid_50004 == 1){
					apply(map_init_50004);
			apply(map_50004_1);
			apply(start_reduce_2_50004);
			apply(update_reduce_2_50004_counts);
			if(meta_reduce_2_50004.val > 59) {
				apply(set_reduce_2_50004_count);			}
			else if(meta_reduce_2_50004.val == 59) {
				apply(skip_reduce_2_50004_1);
			}
			else {
				apply(drop_reduce_2_50004_1);
			}

			apply(copy_to_cpu_50004);
		}
	}
	if (meta_fm.f1 == 21){
		if (meta_fm.qid_130012== 1){
			apply(filter_130012_1);
		}
		if (meta_fm.qid_130012 == 1){
					apply(map_init_130012);
			apply(map_130012_2);
			apply(copy_to_cpu_130012);
		}
	}
	if (meta_fm.f1 == 22){
		if (meta_fm.qid_40032== 1){
			apply(filter_40032_1);
		}
		if (meta_fm.qid_40032 == 1){
					apply(map_init_40032);
			apply(map_40032_2);
			apply(start_distinct_3_40032);
			apply(start_reduce_4_40032);
			apply(start_reduce_5_40032);
			if(meta_distinct_3_40032.val > 0) {
				apply(drop_distinct_3_40032_1);
			}
			else if(meta_distinct_3_40032.val == 0) {
				apply(skip_distinct_3_40032_1);
			}
			else {
				apply(drop_distinct_3_40032_2);
			}

			apply(update_distinct_3_40032_counts);
			apply(update_reduce_4_40032_counts);
			if(meta_reduce_4_40032.val > 2) {
				apply(set_reduce_4_40032_count);			}
			else if(meta_reduce_4_40032.val == 2) {
				apply(skip_reduce_4_40032_1);
			}
			else {
				apply(drop_reduce_4_40032_1);
			}

			apply(update_reduce_5_40032_counts);
			if(meta_reduce_5_40032.val > 79) {
				apply(set_reduce_5_40032_count);			}
			else if(meta_reduce_5_40032.val == 79) {
				apply(skip_reduce_5_40032_1);
			}
			else {
				apply(drop_reduce_5_40032_1);
			}

			apply(copy_to_cpu_40032);
		}
	}
	if (meta_fm.f1 == 23){
		if (meta_fm.qid_140004 == 1){
					apply(map_init_140004);
			apply(map_140004_1);
			apply(start_reduce_2_140004);
			apply(update_reduce_2_140004_counts);
			if(meta_reduce_2_140004.val > 99) {
				apply(set_reduce_2_140004_count);			}
			else if(meta_reduce_2_140004.val == 99) {
				apply(skip_reduce_2_140004_1);
			}
			else {
				apply(drop_reduce_2_140004_1);
			}

			apply(copy_to_cpu_140004);
		}
	}
	if (meta_fm.f1 == 24){
		if (meta_fm.qid_50012== 1){
			apply(filter_50012_1);
		}
		if (meta_fm.qid_50012 == 1){
					apply(map_init_50012);
			apply(map_50012_2);
			apply(start_reduce_3_50012);
			apply(update_reduce_3_50012_counts);
			if(meta_reduce_3_50012.val > 59) {
				apply(set_reduce_3_50012_count);			}
			else if(meta_reduce_3_50012.val == 59) {
				apply(skip_reduce_3_50012_1);
			}
			else {
				apply(drop_reduce_3_50012_1);
			}

			apply(copy_to_cpu_50012);
		}
	}
	if (meta_fm.f1 == 25){
		if (meta_fm.qid_140012== 1){
			apply(filter_140012_1);
		}
		if (meta_fm.qid_140012 == 1){
					apply(map_init_140012);
			apply(map_140012_2);
			apply(copy_to_cpu_140012);
		}
	}
	if (meta_fm.f1 == 26){
		if (meta_fm.qid_130032== 1){
			apply(filter_130032_1);
		}
		if (meta_fm.qid_130032 == 1){
					apply(map_init_130032);
			apply(map_130032_2);
			apply(copy_to_cpu_130032);
		}
	}
	if (meta_fm.f1 == 27){
		if (meta_fm.qid_140008== 1){
			apply(filter_140008_1);
		}
		if (meta_fm.qid_140008 == 1){
					apply(map_init_140008);
			apply(map_140008_2);
			apply(start_reduce_3_140008);
			apply(update_reduce_3_140008_counts);
			if(meta_reduce_3_140008.val > 99) {
				apply(set_reduce_3_140008_count);			}
			else if(meta_reduce_3_140008.val == 99) {
				apply(skip_reduce_3_140008_1);
			}
			else {
				apply(drop_reduce_3_140008_1);
			}

			apply(copy_to_cpu_140008);
		}
	}
	if (meta_fm.f1 == 28){
		if (meta_fm.qid_70004== 1){
			apply(filter_70004_1);
		}
		if (meta_fm.qid_70004 == 1){
					apply(map_init_70004);
			apply(map_70004_2);
			apply(start_reduce_3_70004);
			apply(update_reduce_3_70004_counts);
			if(meta_reduce_3_70004.val > 70) {
				apply(set_reduce_3_70004_count);			}
			else if(meta_reduce_3_70004.val == 70) {
				apply(skip_reduce_3_70004_1);
			}
			else {
				apply(drop_reduce_3_70004_1);
			}

			apply(copy_to_cpu_70004);
		}
	}
	if (meta_fm.f1 == 29){
		if (meta_fm.qid_130004== 1){
			apply(filter_130004_1);
		}
		if (meta_fm.qid_130004 == 1){
					apply(map_init_130004);
			apply(map_130004_2);
			apply(start_reduce_3_130004);
			apply(update_reduce_3_130004_counts);
			if(meta_reduce_3_130004.val > 54) {
				apply(set_reduce_3_130004_count);			}
			else if(meta_reduce_3_130004.val == 54) {
				apply(skip_reduce_3_130004_1);
			}
			else {
				apply(drop_reduce_3_130004_1);
			}

			apply(copy_to_cpu_130004);
		}
	}
	if (meta_fm.f1 == 30){
		if (meta_fm.qid_70012== 1){
			apply(filter_70012_1);
		}
		if (meta_fm.qid_70012 == 1){
					apply(map_init_70012);
			apply(map_70012_2);
			apply(start_reduce_3_70012);
			apply(update_reduce_3_70012_counts);
			if(meta_reduce_3_70012.val > 70) {
				apply(set_reduce_3_70012_count);			}
			else if(meta_reduce_3_70012.val == 70) {
				apply(skip_reduce_3_70012_1);
			}
			else {
				apply(drop_reduce_3_70012_1);
			}

			apply(copy_to_cpu_70012);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 31) {
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
				apply(encap_140032);
			}
			if (meta_fm.f1 == 1){
				apply(encap_20032);
			}
			if (meta_fm.f1 == 2){
				apply(encap_80004);
			}
			if (meta_fm.f1 == 3){
				apply(encap_20012);
			}
			if (meta_fm.f1 == 4){
				apply(encap_80012);
			}
			if (meta_fm.f1 == 5){
				apply(encap_70032);
			}
			if (meta_fm.f1 == 6){
				apply(encap_10012);
			}
			if (meta_fm.f1 == 7){
				apply(encap_80032);
			}
			if (meta_fm.f1 == 8){
				apply(encap_50032);
			}
			if (meta_fm.f1 == 9){
				apply(encap_100004);
			}
			if (meta_fm.f1 == 10){
				apply(encap_80028);
			}
			if (meta_fm.f1 == 11){
				apply(encap_100012);
			}
			if (meta_fm.f1 == 12){
				apply(encap_10032);
			}
			if (meta_fm.f1 == 13){
				apply(encap_110004);
			}
			if (meta_fm.f1 == 14){
				apply(encap_110012);
			}
			if (meta_fm.f1 == 15){
				apply(encap_100032);
			}
			if (meta_fm.f1 == 16){
				apply(encap_40004);
			}
			if (meta_fm.f1 == 17){
				apply(encap_40012);
			}
			if (meta_fm.f1 == 18){
				apply(encap_110028);
			}
			if (meta_fm.f1 == 19){
				apply(encap_110032);
			}
			if (meta_fm.f1 == 20){
				apply(encap_50004);
			}
			if (meta_fm.f1 == 21){
				apply(encap_130012);
			}
			if (meta_fm.f1 == 22){
				apply(encap_40032);
			}
			if (meta_fm.f1 == 23){
				apply(encap_140004);
			}
			if (meta_fm.f1 == 24){
				apply(encap_50012);
			}
			if (meta_fm.f1 == 25){
				apply(encap_140012);
			}
			if (meta_fm.f1 == 26){
				apply(encap_130032);
			}
			if (meta_fm.f1 == 27){
				apply(encap_140008);
			}
			if (meta_fm.f1 == 28){
				apply(encap_70004);
			}
			if (meta_fm.f1 == 29){
				apply(encap_130004);
			}
			if (meta_fm.f1 == 30){
				apply(encap_70012);
			}
		}


	}
}

