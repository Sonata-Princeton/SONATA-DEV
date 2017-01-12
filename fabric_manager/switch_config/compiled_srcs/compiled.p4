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
	extract(out_header_50001);
	extract(out_header_50002);
	extract(out_header_60002);
	extract(out_header_60001);
	return parse_ethernet;
}

header_type out_header_50001_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_50001_t out_header_50001;

field_list copy_to_cpu_fields_50001{
	standard_metadata;
	hash_meta_reduce_4_50001;
	meta_reduce_4_50001;
	meta_map_init_50001;
	meta_fm;
}

action do_copy_to_cpu_50001() {
	clone_ingress_pkt_to_egress(50201, copy_to_cpu_fields_50001);
}

table copy_to_cpu_50001 {
	actions {do_copy_to_cpu_50001;}
	size : 1;
}

table encap_50001 {
	actions { do_encap_50001; }
	size : 1;
}

action do_encap_50001() {
	add_header(out_header_50001);
	modify_field(out_header_50001.qid, meta_reduce_4_50001.qid);
	modify_field(out_header_50001.dIP, meta_map_init_50001.dIP);
	modify_field(out_header_50001.count, meta_reduce_4_50001.val);
}

header_type out_header_50002_t {
	fields {
		qid : 16;
		sIP : 32;
		dIP : 32;
		proto : 16;}
}

header out_header_50002_t out_header_50002;

field_list copy_to_cpu_fields_50002{
	standard_metadata;
	meta_map_init_50002;
	meta_fm;
}

action do_copy_to_cpu_50002() {
	clone_ingress_pkt_to_egress(50202, copy_to_cpu_fields_50002);
}

table copy_to_cpu_50002 {
	actions {do_copy_to_cpu_50002;}
	size : 1;
}

table encap_50002 {
	actions { do_encap_50002; }
	size : 1;
}

action do_encap_50002() {
	add_header(out_header_50002);
	modify_field(out_header_50002.qid, meta_map_init_50002.qid);
	modify_field(out_header_50002.sIP, meta_map_init_50002.sIP);
	modify_field(out_header_50002.dIP, meta_map_init_50002.dIP);
	modify_field(out_header_50002.proto, meta_map_init_50002.proto);
}

header_type out_header_60002_t {
	fields {
		qid : 16;
		sIP : 32;}
}

header out_header_60002_t out_header_60002;

field_list copy_to_cpu_fields_60002{
	standard_metadata;
	meta_map_init_60002;
	meta_fm;
}

action do_copy_to_cpu_60002() {
	clone_ingress_pkt_to_egress(60202, copy_to_cpu_fields_60002);
}

table copy_to_cpu_60002 {
	actions {do_copy_to_cpu_60002;}
	size : 1;
}

table encap_60002 {
	actions { do_encap_60002; }
	size : 1;
}

action do_encap_60002() {
	add_header(out_header_60002);
	modify_field(out_header_60002.qid, meta_map_init_60002.qid);
	modify_field(out_header_60002.sIP, meta_map_init_60002.sIP);
}

header_type out_header_60001_t {
	fields {
		qid : 16;
		sIP : 32;}
}

header out_header_60001_t out_header_60001;

field_list copy_to_cpu_fields_60001{
	standard_metadata;
	meta_map_init_60001;
	meta_fm;
}

action do_copy_to_cpu_60001() {
	clone_ingress_pkt_to_egress(60201, copy_to_cpu_fields_60001);
}

table copy_to_cpu_60001 {
	actions {do_copy_to_cpu_60001;}
	size : 1;
}

table encap_60001 {
	actions { do_encap_60001; }
	size : 1;
}

action do_encap_60001() {
	add_header(out_header_60001);
	modify_field(out_header_60001.qid, meta_map_init_60001.qid);
	modify_field(out_header_60001.sIP, meta_map_init_60001.sIP);
}

table drop_distinct_3_50001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_3_50001_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_3_50001_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_4_50001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_4_50001_1 {
	actions {mark_drop;}
	size : 1;
}

table drop_distinct_2_60001_1 {
	actions {mark_drop;}
	size : 1;
}

table skip_distinct_2_60001_1 {
	actions {_nop;}
	size : 1;
}

table drop_distinct_2_60001_2 {
	actions {mark_drop;}
	size : 1;
}

table skip_reduce_3_60001_1 {
	actions {_nop;}
	size : 1;
}

table drop_reduce_3_60001_1 {
	actions {mark_drop;}
	size : 1;
}

table map_init_50001{
	actions{
		do_map_init_50001;
	}
}

action do_map_init_50001(){
	modify_field(meta_map_init_50001.qid, 50001);
	modify_field(meta_map_init_50001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_50001.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_50001.proto, ipv4.protocol);
}

header_type meta_map_init_50001_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_50001_t meta_map_init_50001;

table map_50001_1{
	actions{
		do_map_50001_1;
	}
}

action do_map_50001_1() {
	bit_and(meta_map_init_50001.dIP, meta_map_init_50001.dIP, 0xffff0000);
}

header_type meta_distinct_3_50001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_3_50001_t meta_distinct_3_50001;

header_type hash_meta_distinct_3_50001_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_3_50001_t hash_meta_distinct_3_50001;

field_list distinct_3_50001_fields {
	hash_meta_distinct_3_50001.sIP;
	hash_meta_distinct_3_50001.dIP;
}

field_list_calculation distinct_3_50001_fields_hash {
	input {
		distinct_3_50001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_3_50001{
	width : 32;
	instance_count : 4096;
}

action update_distinct_3_50001_regs() {
	bit_or(meta_distinct_3_50001.val,meta_distinct_3_50001.val, 1);
	register_write(distinct_3_50001,meta_distinct_3_50001.idx,meta_distinct_3_50001.val);
}

table update_distinct_3_50001_counts {
	actions {update_distinct_3_50001_regs;}
	size : 1;
}

action do_distinct_3_50001_hashes() {
	modify_field(hash_meta_distinct_3_50001.sIP, meta_map_init_50001.sIP);
	modify_field(hash_meta_distinct_3_50001.dIP, meta_map_init_50001.dIP);
	modify_field(meta_distinct_3_50001.qid, 50001);
	modify_field_with_hash_based_offset(meta_distinct_3_50001.idx, 0, distinct_3_50001_fields_hash, 4096);
	register_read(meta_distinct_3_50001.val, distinct_3_50001, meta_distinct_3_50001.idx);
}

table start_distinct_3_50001 {
	actions {do_distinct_3_50001_hashes;}
	size : 1;
}

action set_distinct_3_50001_count() {
	modify_field(meta_distinct_3_50001.val, 1);
}

table set_distinct_3_50001_count {
	actions {set_distinct_3_50001_count;}
        size: 1;
}

header_type meta_reduce_4_50001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_4_50001_t meta_reduce_4_50001;

header_type hash_meta_reduce_4_50001_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_4_50001_t hash_meta_reduce_4_50001;

field_list reduce_4_50001_fields {
	hash_meta_reduce_4_50001.dIP;
}

field_list_calculation reduce_4_50001_fields_hash {
	input {
		reduce_4_50001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_4_50001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_4_50001_regs() {
	add_to_field(meta_reduce_4_50001.val, 1);
	register_write(reduce_4_50001,meta_reduce_4_50001.idx,meta_reduce_4_50001.val);
}

table update_reduce_4_50001_counts {
	actions {update_reduce_4_50001_regs;}
	size : 1;
}

action do_reduce_4_50001_hashes() {
	modify_field(hash_meta_reduce_4_50001.dIP, meta_map_init_50001.dIP);
	modify_field(meta_reduce_4_50001.qid, 50001);
	modify_field_with_hash_based_offset(meta_reduce_4_50001.idx, 0, reduce_4_50001_fields_hash, 4096);
	register_read(meta_reduce_4_50001.val, reduce_4_50001, meta_reduce_4_50001.idx);
}

table start_reduce_4_50001 {
	actions {do_reduce_4_50001_hashes;}
	size : 1;
}

action set_reduce_4_50001_count() {
	modify_field(meta_reduce_4_50001.val, 1);
}

table set_reduce_4_50001_count {
	actions {set_reduce_4_50001_count;}
        size: 1;
}

table map_init_50002{
	actions{
		do_map_init_50002;
	}
}

action do_map_init_50002(){
	modify_field(meta_map_init_50002.qid, 50002);
	modify_field(meta_map_init_50002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_50002.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_50002.proto, ipv4.protocol);
}

header_type meta_map_init_50002_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_50002_t meta_map_init_50002;

table map_50002_2{
	actions{
		do_map_50002_2;
	}
}

action do_map_50002_2() {
	bit_and(meta_map_init_50002.dIP, meta_map_init_50002.dIP, 0xffffffff);
}

table map_init_60002{
	actions{
		do_map_init_60002;
	}
}

action do_map_init_60002(){
	modify_field(meta_map_init_60002.qid, 60002);
	modify_field(meta_map_init_60002.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_60002.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_60002.proto, ipv4.protocol);
}

header_type meta_map_init_60002_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_60002_t meta_map_init_60002;

table map_60002_2{
	actions{
		do_map_60002_2;
	}
}

action do_map_60002_2() {
	bit_and(meta_map_init_60002.sIP, meta_map_init_60002.sIP, 0xffffffff);
}

table map_init_60001{
	actions{
		do_map_init_60001;
	}
}

action do_map_init_60001(){
	modify_field(meta_map_init_60001.qid, 60001);
	modify_field(meta_map_init_60001.sIP, ipv4.srcAddr);
	modify_field(meta_map_init_60001.dIP, ipv4.dstAddr);
	modify_field(meta_map_init_60001.proto, ipv4.protocol);
}

header_type meta_map_init_60001_t {
	 fields {
		qid: 16;
		sIP: 32;
		dIP: 32;
		proto: 16;
	}
}

metadata meta_map_init_60001_t meta_map_init_60001;

table map_60001_1{
	actions{
		do_map_60001_1;
	}
}

action do_map_60001_1() {
	bit_and(meta_map_init_60001.sIP, meta_map_init_60001.sIP, 0xffff0000);
}

header_type meta_distinct_2_60001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_2_60001_t meta_distinct_2_60001;

header_type hash_meta_distinct_2_60001_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_2_60001_t hash_meta_distinct_2_60001;

field_list distinct_2_60001_fields {
	hash_meta_distinct_2_60001.sIP;
	hash_meta_distinct_2_60001.dIP;
}

field_list_calculation distinct_2_60001_fields_hash {
	input {
		distinct_2_60001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register distinct_2_60001{
	width : 32;
	instance_count : 4096;
}

action update_distinct_2_60001_regs() {
	bit_or(meta_distinct_2_60001.val,meta_distinct_2_60001.val, 1);
	register_write(distinct_2_60001,meta_distinct_2_60001.idx,meta_distinct_2_60001.val);
}

table update_distinct_2_60001_counts {
	actions {update_distinct_2_60001_regs;}
	size : 1;
}

action do_distinct_2_60001_hashes() {
	modify_field(hash_meta_distinct_2_60001.sIP, meta_map_init_60001.sIP);
	modify_field(hash_meta_distinct_2_60001.dIP, meta_map_init_60001.dIP);
	modify_field(meta_distinct_2_60001.qid, 60001);
	modify_field_with_hash_based_offset(meta_distinct_2_60001.idx, 0, distinct_2_60001_fields_hash, 4096);
	register_read(meta_distinct_2_60001.val, distinct_2_60001, meta_distinct_2_60001.idx);
}

table start_distinct_2_60001 {
	actions {do_distinct_2_60001_hashes;}
	size : 1;
}

action set_distinct_2_60001_count() {
	modify_field(meta_distinct_2_60001.val, 1);
}

table set_distinct_2_60001_count {
	actions {set_distinct_2_60001_count;}
        size: 1;
}

header_type meta_reduce_3_60001_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_3_60001_t meta_reduce_3_60001;

header_type hash_meta_reduce_3_60001_t {
	fields {
		sIP : 32;
	}
}

metadata hash_meta_reduce_3_60001_t hash_meta_reduce_3_60001;

field_list reduce_3_60001_fields {
	hash_meta_reduce_3_60001.sIP;
}

field_list_calculation reduce_3_60001_fields_hash {
	input {
		reduce_3_60001_fields;
	}
	algorithm : crc32;
	output_width : 32;
}

register reduce_3_60001{
	width : 32;
	instance_count : 4096;
}

action update_reduce_3_60001_regs() {
	add_to_field(meta_reduce_3_60001.val, 1);
	register_write(reduce_3_60001,meta_reduce_3_60001.idx,meta_reduce_3_60001.val);
}

table update_reduce_3_60001_counts {
	actions {update_reduce_3_60001_regs;}
	size : 1;
}

action do_reduce_3_60001_hashes() {
	modify_field(hash_meta_reduce_3_60001.sIP, meta_map_init_60001.sIP);
	modify_field(meta_reduce_3_60001.qid, 60001);
	modify_field_with_hash_based_offset(meta_reduce_3_60001.idx, 0, reduce_3_60001_fields_hash, 4096);
	register_read(meta_reduce_3_60001.val, reduce_3_60001, meta_reduce_3_60001.idx);
}

table start_reduce_3_60001 {
	actions {do_reduce_3_60001_hashes;}
	size : 1;
}

action set_reduce_3_60001_count() {
	modify_field(meta_reduce_3_60001.val, 1);
}

table set_reduce_3_60001_count {
	actions {set_reduce_3_60001_count;}
        size: 1;
}

header_type meta_fm_t {
	fields {
		qid_50001 : 1;
		qid_50002 : 1;
		qid_60002 : 1;
		qid_60001 : 1;
		f1 : 8;
		is_drop : 1;
	}
}

metadata meta_fm_t meta_fm;

action init_meta_fm() {
	modify_field(meta_fm.qid_50001, 1);
	modify_field(meta_fm.qid_50002, 1);
	modify_field(meta_fm.qid_60002, 1);
	modify_field(meta_fm.qid_60001, 1);
	modify_field(meta_fm.is_drop, 0);
}

table init_meta_fm {
	actions {init_meta_fm;}
	size: 1;
}

action set_meta_fm_50001(){
	modify_field(meta_fm.qid_50001, 1);
}

action set_meta_fm_50002(){
	modify_field(meta_fm.qid_50002, 1);
}

action set_meta_fm_60002(){
	modify_field(meta_fm.qid_60002, 1);
}

action set_meta_fm_60001(){
	modify_field(meta_fm.qid_60001, 1);
}

action reset_meta_fm_50001(){
	modify_field(meta_fm.qid_50001, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_50002(){
	modify_field(meta_fm.qid_50002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_60002(){
	modify_field(meta_fm.qid_60002, 0);
	modify_field(meta_fm.is_drop, 1);
}

action reset_meta_fm_60001(){
	modify_field(meta_fm.qid_60001, 0);
	modify_field(meta_fm.is_drop, 1);
}

table filter_50001_2{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_50001;
		reset_meta_fm_50001;
	}
}

table filter_50002_3{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_50002;
		reset_meta_fm_50002;
	}
}

table filter_50002_1{
	reads {
		ipv4.dstAddr: lpm;
	}
	actions{
		set_meta_fm_50002;
		reset_meta_fm_50002;
	}
}

table filter_60002_3{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_60002;
		reset_meta_fm_60002;
	}
}

table filter_60002_1{
	reads {
		ipv4.srcAddr: lpm;
	}
	actions{
		set_meta_fm_60002;
		reset_meta_fm_60002;
	}
}

table filter_60001_4{
	reads {
		ipv4.protocol: exact;
	}
	actions{
		set_meta_fm_60001;
		reset_meta_fm_60001;
	}
}

control ingress {
	apply(init_meta_fm);
	if (meta_fm.f1 == 0){
		apply(filter_50001_2);
		if (meta_fm.qid_50001 == 1){
					apply(map_init_50001);
			apply(map_50001_1);
			apply(start_distinct_3_50001);
			apply(start_reduce_4_50001);
			if(meta_distinct_3_50001.val > 0) {
				apply(drop_distinct_3_50001_1);
			}
			else if(meta_distinct_3_50001.val == 0) {
				apply(skip_distinct_3_50001_1);
			}
			else {
				apply(drop_distinct_3_50001_2);
			}

			apply(update_distinct_3_50001_counts);
			apply(update_reduce_4_50001_counts);
			if(meta_reduce_4_50001.val > 2) {
				apply(set_reduce_4_50001_count);			}
			else if(meta_reduce_4_50001.val == 2) {
				apply(skip_reduce_4_50001_1);
			}
			else {
				apply(drop_reduce_4_50001_1);
			}

			apply(copy_to_cpu_50001);
		}
	}
	if (meta_fm.f1 == 1){
		apply(filter_50002_3);
		if (meta_fm.qid_50002== 1){
			apply(filter_50002_1);
		}
		if (meta_fm.qid_50002 == 1){
					apply(map_init_50002);
			apply(map_50002_2);
			apply(copy_to_cpu_50002);
		}
	}
	if (meta_fm.f1 == 2){
		apply(filter_60002_3);
		if (meta_fm.qid_60002== 1){
			apply(filter_60002_1);
		}
		if (meta_fm.qid_60002 == 1){
					apply(map_init_60002);
			apply(map_60002_2);
			apply(copy_to_cpu_60002);
		}
	}
	if (meta_fm.f1 == 3){
		apply(filter_60001_4);
		if (meta_fm.qid_60001 == 1){
					apply(map_init_60001);
			apply(map_60001_1);
			apply(start_distinct_2_60001);
			apply(start_reduce_3_60001);
			if(meta_distinct_2_60001.val > 0) {
				apply(drop_distinct_2_60001_1);
			}
			else if(meta_distinct_2_60001.val == 0) {
				apply(skip_distinct_2_60001_1);
			}
			else {
				apply(drop_distinct_2_60001_2);
			}

			apply(update_distinct_2_60001_counts);
			apply(update_reduce_3_60001_counts);
			if(meta_reduce_3_60001.val > 2) {
				apply(set_reduce_3_60001_count);			}
			else if(meta_reduce_3_60001.val == 2) {
				apply(skip_reduce_3_60001_1);
			}
			else {
				apply(drop_reduce_3_60001_1);
			}

			apply(copy_to_cpu_60001);
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
				apply(encap_50001);
			}
			if (meta_fm.f1 == 1){
				apply(encap_50002);
			}
			if (meta_fm.f1 == 2){
				apply(encap_60002);
			}
			if (meta_fm.f1 == 3){
				apply(encap_60001);
			}
		}


	}
}

