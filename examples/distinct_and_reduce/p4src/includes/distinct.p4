#define TABLE_WIDTH 16
#define TABLE_SIZE 4096
#define DISTINCT 0

header_type meta_distinct_t {
	fields {
		distinctIndex : TABLE_WIDTH;
		distinctVal : 1;
	}
}

metadata meta_distinct_t meta_distinct;

field_list distinct_fields {
	ipv4.srcAddr;
	ipv4.dstAddr;
}

field_list_calculation distinct_fields_hash {
    input {
       distinct_fields;
    }
    algorithm : crc32;
    output_width : TABLE_WIDTH;
}

register distinct {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

action update_distinct_regs() {
    bit_or(meta_distinct.distinctVal, meta_distinct.distinctVal, 1);
    register_write(distinct, meta_distinct.distinctIndex, meta_distinct.distinctVal);
}

table update_distinct_counts {
    actions {update_distinct_regs;}
    size : 1;
}

action do_distinct_hashes() {
    modify_field_with_hash_based_offset(meta_distinct.distinctIndex, 0, distinct_fields_hash, TABLE_SIZE);
    register_read(meta_distinct.distinctVal, distinct, meta_distinct.distinctIndex);
}

table start_distinct {
    actions {do_distinct_hashes;}
    size : 1;
}
