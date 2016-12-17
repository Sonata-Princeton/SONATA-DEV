#define TABLE_WIDTH 16
#define TABLE_SIZE 4096
#define THRESHOLD 2

header_type meta_reduce_t {
	fields {
		reduceIndex : TABLE_WIDTH;
		reduceVal : 8;
	}
}

metadata meta_reduce_t meta_reduce;

field_list reduce_fields {
	ipv4.dstAddr;
}

field_list_calculation reduce_fields_hash {
    input {
       reduce_fields;
    }
    algorithm : crc32;
    output_width : TABLE_WIDTH;
}

register reduce {
	width : TABLE_WIDTH;
	instance_count : TABLE_SIZE;
}

action update_reduce_regs() {
   add_to_field(meta_reduce.reduceVal, 1);
   register_write(reduce, meta_reduce.reduceIndex, meta_reduce.reduceVal);
}

table update_reduce_counts {
    actions {update_reduce_regs;}
    size : 1;
}

action do_reduce_hashes() {
		modify_field_with_hash_based_offset(meta_reduce.reduceIndex, 0, reduce_fields_hash, TABLE_SIZE);
    register_read(meta_reduce.reduceVal, reduce, meta_reduce.reduceIndex);
}

table start_reduce {
    actions {do_reduce_hashes;}
    size : 1;
}

action set_to_one() {
    modify_field(meta_reduce.reduceVal, 1);
}

table set_count {
	actions {set_to_one;}
	size: 1;
}
