from scapy.all import *
import time


BASIC = """
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
	recirculate_flag : 16;
	}
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


action do_send_original_out() {
	    modify_field(standard_metadata.egress_spec, 13);
}

table send_original_out {
	actions { do_send_original_out; }
	size : 1;
}
header_type meta_fm_t {
	fields {
		f1 : 8;
	}
}

metadata meta_fm_t meta_fm;
"""


def get_query_composed(id):


    map = """
//Map
header_type meta_map_init_%s_t {
     fields {
        qid: 16;
        dMac: 48;
        sIP: 32;
        proto: 16;
        sMac: 48;
        nBytes: 16;
        dPort: 16;
        sPort: 16;
        dIP: 32;
    }
}

metadata meta_map_init_%s_t meta_map_init_%s;
            """ % (id, id, id)

    distinct = """
header_type meta_distinct_%s_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_distinct_%s_t meta_distinct_%s;

header_type hash_meta_distinct_%s_t {
	fields {
		sIP : 32;
		dIP : 32;
	}
}

metadata hash_meta_distinct_%s_t hash_meta_distinct_%s;
            """% (id, id, id, id,id,id)

    reduce = """
//Reduce
header_type meta_reduce_%s_t {
	fields {
		qid : 16;
		val : 32;
		idx : 32;
	}
}

metadata meta_reduce_%s_t meta_reduce_%s;

header_type hash_meta_reduce_%s_t {
	fields {
		dIP : 32;
	}
}

metadata hash_meta_reduce_%s_t hash_meta_reduce_%s;
            """% (id, id, id, id,id,id)

    header = """
header_type out_header_%s_t {
	fields {
		qid : 16;
		dIP : 32;
		count : 16;
	}
}

header out_header_%s_t out_header_%s;
"""% (id, id, id)

    source = header + "\n" + map + "\n" + reduce + "\n" + distinct + "\n"
    extract_header = """extract(out_header_%s);""" % id

    ingress_loop = "if(meta_fm.f1==%s){}" % id
    app_metadata = "drop_%s: 1;\nsatisfied_%s: 1;"%(id, id)

    return source, extract_header, ingress_loop, app_metadata


def get_registers(number_of_registers):
    register = ""
    apply_code = ""
    commands = []
    registers = []
    for i in range(0, number_of_registers):
        register += """
register reduce_%s {
    width: 32;
    instance_count: 4096;
}
table use_reduce_%s {
    actions {
        do_use_reduce_%s;
    }
    size : 1;
}

action do_use_reduce_%s() {
	   	register_write(reduce_%s, 0, 1);
}
\n"""%(i, i, i, i, i)

        apply_code += "apply(use_reduce_%s);"%(i) +"\n"
        commands.append("table_set_default use_reduce_%s do_use_reduce_%s"%(i,i))
        registers.append("reduce_%s"%i)
    return register,apply_code,commands,registers

def get_sequential_code(NUMBER_OF_REGISTERS):

    source = ""
    extract_header = ""
    ingress_loop = ""
    app_metadata = ""
    register_code,apply_code,register_commands,registers = get_registers(NUMBER_OF_REGISTERS)

    parse_headers = """parser parse_out_header {
	%s
	return parse_ethernet;
}   """%(extract_header)
    ingress = """
control ingress {
    %s
    apply(send_original_out);
}
"""%(apply_code)

    egress = """
control egress {
}"""

    app_metadata = """///Sequential
header_type meta_app_data_t {
	fields {
		%s
		clone: 1;
	}
}

metadata meta_app_data_t meta_app_data;"""%(app_metadata)


    FINAL_CODE = BASIC + "\n" + source + "\n" + register_code +"\n" + parse_headers + "\n" + app_metadata + "\n" + ingress + "\n" + egress
    COMMANDS = ["table_set_default send_original_out do_send_original_out"] + register_commands
    return FINAL_CODE, COMMANDS,registers


def get_recirculation_code(NUMBER_OF_QUERIES):

    source = ""
    extract_header = ""
    ingress_loop = ""


    for qid in range(0, NUMBER_OF_QUERIES):
        qid_source, qid_extract_header, qid_ingress_loop, _ = get_query_composed(qid)

        source += qid_source + "\n"
        extract_header += qid_extract_header + "\n"
        ingress_loop += qid_ingress_loop + "\n"

    parse_headers = """parser parse_out_header {
	%s
	return parse_ethernet;
}   """%(extract_header)
    ingress = """
control ingress {
    %s
    if(meta_fm.f1 == %s) {apply(send_original_out);}
}""" % (ingress_loop, NUMBER_OF_QUERIES)

    egress = """
control egress {
    if(standard_metadata.instance_type != 1) {
        if(meta_fm.f1 < %s)
        {
            apply(recirculate_to_ingress);
        }
    }
}"""%(NUMBER_OF_QUERIES)


    FINAL_CODE = BASIC + "\n" + source + "\n" + parse_headers + "\n" + ingress + "\n" + egress
    COMMANDS = ["table_set_default recirculate_to_ingress do_recirculate_to_ingress",
                "table_set_default send_original_out do_send_original_out"]
    return FINAL_CODE, COMMANDS


def send_created_traffic(duration, veth, NUMBER_OF_PACKETS_PER_SECOND):
    traffic_dict = {}
    for i in range(0, duration):
        traffic_dict[i] = []
        traffic_dict[i].extend(create_normal_traffic(NUMBER_OF_PACKETS_PER_SECOND))

    for i in range(0, duration):
        start = time.time()
        print "Sending traffic for ts: " + str(i)
        sendp(traffic_dict[i], iface=veth, verbose=0)
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)


def create_normal_traffic(number_of_packets):
    normal_packets = []

    for i in range(number_of_packets):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(ttl=255, dst=dIP, src=sIP) / TCP() / "SONATA NORMAL"
        normal_packets.append(p)

    return normal_packets