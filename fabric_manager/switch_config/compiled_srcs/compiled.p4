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
	extract(out_header_10002);
	extract(out_header_10001);
	return parse_ethernet;
}

header_type out_header_30001_t {
	fields {
		qid : 8;
		dIP : 32;
		count : 8;
	}
}

header out_header_30001_t out_header_30001;

field_list copy_to_cpu_fields_30001{
	standard_metadata;
	hash_meta_reduce_2_30001;
	meta_reduce_2_30001;
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
	modify_field(out_header_30001.qid, meta_reduce_2_30001.qid);
	modify_field(out_header_30001.dIP, meta_map_init_30001.dIP);
	modify_field(out_header_30001.count, meta_reduce_2_30001.val);
}

header_type out_header_30002_t {
	fields {
		qid : 8;
		dIP : 32;
		count : 8;
	}
}

header out_header_30002_t out_header_30002;

field_list copy_to_cpu_fields_30002{
	standard_metadata;
	hash_meta_reduce_2_30002;
	meta_reduce_2_30002;
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
	modify_field(out_header_30002.qid, meta_reduce_2_30002.qid);
	modify_field(out_header_30002.dIP, meta_map_init_30002.dIP);
	modify_field(out_header_30002.count, meta_reduce_2_30002.val);
}

header_type out_header_10002_t {
	fields {
		qid : 8;
		dIP : 32;
		sIP : 32;}
}

header out_header_10002_t out_header_10002;

field_list copy_to_cpu_fields_10002{
	standard_metadata;
	hash_meta_distinct_3_10002;
	meta_distinct_3_10002;
	meta_map_init_10002;
	meta_fm;
}

action do_copy_to_cpu_10002() {
	clone_ingress_pkt_to_egress(10202, copy_to_cpu_fields_10002);
}

table copy_to_cpu_10002 {
	actions {do_copy_to_cpu_10002;}
	size : 1;
}

table encap_10002 {
	actions { do_encap_10002; }
	size : 1;
}

action do_encap_10002() {
	add_header(out_header_10002);
	modify_field(out_header_10002.qid, meta_distinct_3_10002.qid);
	modify_field(out_header_10002.dIP, meta_map_init_10002.dIP);
	modify_field(out_header_10002.sIP, meta_map_init_10002.sIP);
}

header_type out_header_10001_t {
	fields {
		qid : 8;
		dIP : 32;
		sIP : 32;}
}

header out_header_10001_t out_header_10001;

field_list copy_to_cpu_fields_10001{
	standard_metadata;
	hash_meta_distinct_2_10001;
	meta_distinct_2_10001;
	meta_map_init_10001;
	meta_fm;
}

action do_copy_to_cpu_10001() {
	clone_ingress_pkt_to_egress(10201, copy_to_cpu_fields_10001);
}

table copy_to_cpu_10001 {
	actions {do_copy_to_cpu_10001;}
	size : 1;
}

table encap_10001 {
	actions { do_encap_10001; }
	size : 1;
}

action do_encap_10001() {
	add_header(out_header_10001);
	modify_field(out_header_10001.qid, meta_distinct_2_10001.qid);
	modify_field(out_header_10001.dIP, meta_map_init_10001.dIP);
	modify_field(out_header_10001.sIP, meta_map_init_10001.sIP);
}

table skip_reduce_2_30001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_2_30001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_2_30002_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_2_30002_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_3_10002_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_10002_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_10002_2 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_2_10001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_10001_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_10001_2 {
	actions {mark_drop;}
	size : 1;
}

header_type meta_map_init_30001_t {
	 fields {
		dIP: 32;
	}
}

metadata meta_map_init_30001_t meta_map_init_30001;

table map_init_30001{
	actions{
		do_map_init_30001;
	}
}

action do_map_init_30001(){
	modify_field(meta_map_init_30001.dIP, ipv4.dstAddr);
}

table map_30001_1{
	actions{
		do_map_30001_1;
	}
}

action do_map_30001_1() {
	bit_and(meta_map_init_30001.dIP, meta_map_init_30001.dIP, 0xff000000);
}

header_type meta_reduce_2_30001_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_30001_t meta_reduce_2_30001;

header_type hash_meta_reduce_2_30001_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_2_30001_t hash_meta_reduce_2_30001;

field_list reduce_2_30001_fields {
	hash_meta_reduce_2_30001.dIP;
}

field_list_calculation reduce_2_30001_fields_hash {
	input {
		reduce_2_30001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_2_30001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_2_30001_regs() {
	add_to_field(meta_reduce_2_30001.val, 1);
	register_write(reduce_2_30001,meta_reduce_2_30001.idx,meta_reduce_2_30001.val);
}

table update_reduce_2_30001_counts {
	actions {update_reduce_2_30001_regs;}
	size : 1;
}

action do_reduce_2_30001_hashes() {
	modify_field(hash_meta_reduce_2_30001.dIP, meta_map_init_30001.dIP);
	modify_field(meta_reduce_2_30001.qid, 30001);
	modify_field_with_hash_based_offset(meta_reduce_2_30001.idx, 0, reduce_2_30001_fields_hash, 4096);
	register_read(meta_reduce_2_30001.val, reduce_2_30001, meta_reduce_2_30001.idx);
}

table start_reduce_2_30001 {
	actions {do_reduce_2_30001_hashes;}
	size : 1;
}

action set_reduce_2_30001_count() {
	modify_field(meta_reduce_2_30001.val, 1);
}

table set_reduce_2_30001_count {
	actions {set_reduce_2_30001_count;}
        size: 1;
}

header_type meta_map_init_30002_t {
	 fields {
		dIP: 32;
	}
}

metadata meta_map_init_30002_t meta_map_init_30002;

table map_init_30002{
	actions{
		do_map_init_30002;
	}
}

action do_map_init_30002(){
	modify_field(meta_map_init_30002.dIP, ipv4.dstAddr);
}

table map_30002_1{
	actions{
		do_map_30002_1;
	}
}

action do_map_30002_1() {
	bit_and(meta_map_init_30002.dIP, meta_map_init_30002.dIP, 0xffffffff);
}

header_type meta_reduce_2_30002_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_2_30002_t meta_reduce_2_30002;

header_type hash_meta_reduce_2_30002_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_2_30002_t hash_meta_reduce_2_30002;

field_list reduce_2_30002_fields {
	hash_meta_reduce_2_30002.dIP;
}

field_list_calculation reduce_2_30002_fields_hash {
	input {
		reduce_2_30002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_2_30002{
	width : 32;
	instance_count : 4096;
}

action update_reduce_2_30002_regs() {
	add_to_field(meta_reduce_2_30002.val, 1);
	register_write(reduce_2_30002,meta_reduce_2_30002.idx,meta_reduce_2_30002.val);
}

table update_reduce_2_30002_counts {
	actions {update_reduce_2_30002_regs;}
	size : 1;
}

action do_reduce_2_30002_hashes() {
	modify_field(hash_meta_reduce_2_30002.dIP, meta_map_init_30002.dIP);
	modify_field(meta_reduce_2_30002.qid, 30002);
	modify_field_with_hash_based_offset(meta_reduce_2_30002.idx, 0, reduce_2_30002_fields_hash, 4096);
	register_read(meta_reduce_2_30002.val, reduce_2_30002, meta_reduce_2_30002.idx);
}

table start_reduce_2_30002 {
	actions {do_reduce_2_30002_hashes;}
	size : 1;
}

action set_reduce_2_30002_count() {
	modify_field(meta_reduce_2_30002.val, 1);
}

table set_reduce_2_30002_count {
	actions {set_reduce_2_30002_count;}
        size: 1;
}

header_type meta_map_init_10002_t {
	 fields {
		sIP: 32;
		dIP: 32;
		proto: 8;
	}
}

metadata meta_map_init_10002_t meta_map_init_10002;

table map_init_10002{
	actions{
		do_map_init_10002;
	}
}

action do_map_init_10002(){
	modify_field(meta_map_init_10002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10002.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_10002.proto, ipv4.protocol);
}

table map_10002_1{
	actions{
		do_map_10002_1;
	}
}

action do_map_10002_1() {
	bit_and(meta_map_init_10002.dIP, meta_map_init_10002.dIP, 0xffffffff);
}

header_type meta_distinct_3_10002_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_10002_t meta_distinct_3_10002;

header_type hash_meta_distinct_3_10002_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_10002_t hash_meta_distinct_3_10002;

field_list distinct_3_10002_fields {
	hash_meta_distinct_3_10002.sIP;
	hash_meta_distinct_3_10002.dIP;
}

field_list_calculation distinct_3_10002_fields_hash {
	input {
		distinct_3_10002_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_10002{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_10002_regs() {
	bit_or(meta_distinct_3_10002.val,meta_distinct_3_10002.val, 1);
	register_write(distinct_3_10002,meta_distinct_3_10002.idx,meta_distinct_3_10002.val);
}

table update_distinct_3_10002_counts {
	actions {update_distinct_3_10002_regs;}
	size : 1;
}

action do_distinct_3_10002_hashes() {
	modify_field(hash_meta_distinct_3_10002.sIP, meta_map_init_10002.sIP);
	modify_field(hash_meta_distinct_3_10002.dIP, meta_map_init_10002.dIP);
	modify_field(meta_distinct_3_10002.qid, 10002);
	modify_field_with_hash_based_offset(meta_distinct_3_10002.idx, 0, distinct_3_10002_fields_hash, 4096);
	register_read(meta_distinct_3_10002.val, distinct_3_10002, meta_distinct_3_10002.idx);
}

table start_distinct_3_10002 {
	actions {do_distinct_3_10002_hashes;}
	size : 1;
}

action set_distinct_3_10002_count() {
	modify_field(meta_distinct_3_10002.val, 1);
}

table set_distinct_3_10002_count {
	actions {set_distinct_3_10002_count;}
        size: 1;
}

header_type meta_map_init_10001_t {
	 fields {
		sIP: 32;
		dIP: 32;
		proto: 8;
	}
}

metadata meta_map_init_10001_t meta_map_init_10001;

table map_init_10001{
	actions{
		do_map_init_10001;
	}
}

action do_map_init_10001(){
	modify_field(meta_map_init_10001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_10001.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_10001.proto, ipv4.protocol);
}

table map_10001_0{
	actions{
		do_map_10001_0;
	}
}

action do_map_10001_0() {
	bit_and(meta_map_init_10001.dIP, meta_map_init_10001.dIP, 0xff000000);
}

header_type meta_distinct_2_10001_t {
	fields {
		qid : 8;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_10001_t meta_distinct_2_10001;

header_type hash_meta_distinct_2_10001_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_10001_t hash_meta_distinct_2_10001;

field_list distinct_2_10001_fields {
	hash_meta_distinct_2_10001.sIP;
	hash_meta_distinct_2_10001.dIP;
}

field_list_calculation distinct_2_10001_fields_hash {
	input {
		distinct_2_10001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_10001{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_10001_regs() {
	bit_or(meta_distinct_2_10001.val,meta_distinct_2_10001.val, 1);
	register_write(distinct_2_10001,meta_distinct_2_10001.idx,meta_distinct_2_10001.val);
}

table update_distinct_2_10001_counts {
	actions {update_distinct_2_10001_regs;}
	size : 1;
}

action do_distinct_2_10001_hashes() {
	modify_field(hash_meta_distinct_2_10001.sIP, meta_map_init_10001.sIP);
	modify_field(hash_meta_distinct_2_10001.dIP, meta_map_init_10001.dIP);
	modify_field(meta_distinct_2_10001.qid, 10001);
	modify_field_with_hash_based_offset(meta_distinct_2_10001.idx, 0, distinct_2_10001_fields_hash, 4096);
	register_read(meta_distinct_2_10001.val, distinct_2_10001, meta_distinct_2_10001.idx);
}

table start_distinct_2_10001 {
	actions {do_distinct_2_10001_hashes;}
	size : 1;
}

action set_distinct_2_10001_count() {
	modify_field(meta_distinct_2_10001.val, 1);
}

table set_distinct_2_10001_count {
	actions {set_distinct_2_10001_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_30001 : 1;
		qid_30002 : 1;
		qid_10002 : 1;
		qid_10001 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_30001, 1);
	modify_field(meta_fm.qid_30002, 1);
	modify_field(meta_fm.qid_10002, 1);
	modify_field(meta_fm.qid_10001, 1);
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

action set_meta_fm_10002(){
	modify_field(meta_fm.qid_10002, 1);
}

action set_meta_fm_10001(){
	modify_field(meta_fm.qid_10001, 1);
}

action reset_meta_fm_30001(){
	modify_field(meta_fm.qid_30001, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_30002(){
	modify_field(meta_fm.qid_30002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10002(){
	modify_field(meta_fm.qid_10002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_10001(){
	modify_field(meta_fm.qid_10001, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_30001_0{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_30001;
		reset_meta_fm_30001;
	}
}

table filter_30002_0{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_30002;
		reset_meta_fm_30002;
	}
}

table filter_10002_2{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_10002;
		reset_meta_fm_10002;
	}
}

table filter_10002_0{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_10002;
		reset_meta_fm_10002;
	}
}

table filter_10001_1{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_10001;
		reset_meta_fm_10001;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		if (meta_fm.qid_30001== 1){
			apply(filter_30001_0);
		}
		if (meta_fm.qid_30001 == 1){
			apply(map_init_30001);
			apply(map_30001_1);
			apply(start_reduce_2_30001);
			apply(update_reduce_2_30001_counts);
			if(meta_reduce_2_30001.val > 2) {
				apply(set_reduce_2_30001_count);			}
			else if(meta_reduce_2_30001.val == 2) {
				apply(skip_reduce_2_30001_1);
			}
			else {
				apply(drop_reduce_2_30001_1);
			}

			apply(copy_to_cpu_30001);
		}
	}
	if (meta_fm.f1 == 1){
		if (meta_fm.qid_30002== 1){
			apply(filter_30002_0);
		}
		if (meta_fm.qid_30002 == 1){
			apply(map_init_30002);
			apply(map_30002_1);
			apply(start_reduce_2_30002);
			apply(update_reduce_2_30002_counts);
			if(meta_reduce_2_30002.val > 2) {
				apply(set_reduce_2_30002_count);			}
			else if(meta_reduce_2_30002.val == 2) {
				apply(skip_reduce_2_30002_1);
			}
			else {
				apply(drop_reduce_2_30002_1);
			}

			apply(copy_to_cpu_30002);
		}
	}
	if (meta_fm.f1 == 2){
		apply(filter_10002_2);
		if (meta_fm.qid_10002== 1){
			apply(filter_10002_0);
		}
		if (meta_fm.qid_10002 == 1){
			apply(map_init_10002);
			apply(map_10002_1);
			apply(start_distinct_3_10002);
			if(meta_distinct_3_10002.val > 0) {
				apply(drop_distinct_3_10002_1);
			}
			else if(meta_distinct_3_10002.val == 0) {
				apply(skip_distinct_3_10002_1);
			}
			else {
				apply(drop_distinct_3_10002_2);
			}

			apply(update_distinct_3_10002_counts);
			apply(copy_to_cpu_10002);
		}
	}
	if (meta_fm.f1 == 3){
		apply(filter_10001_1);
		if (meta_fm.qid_10001 == 1){
			apply(map_init_10001);
			apply(map_10001_0);
			apply(start_distinct_2_10001);
			if(meta_distinct_2_10001.val > 0) {
				apply(drop_distinct_2_10001_1);
			}
			else if(meta_distinct_2_10001.val == 0) {
				apply(skip_distinct_2_10001_1);
			}
			else {
				apply(drop_distinct_2_10001_2);
			}

			apply(update_distinct_2_10001_counts);
			apply(copy_to_cpu_10001);
		}
	}
}

control egress {
	if (standard_metadata.instance_type != 1) {
		if(meta_fm.f1 < 4) {
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
			if (meta_fm.f1 == 2){
				apply(encap_10002);
			}
			if (meta_fm.f1 == 3){
				apply(encap_10001);
			}
		}


	}
}

