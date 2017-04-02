#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

from sonata.dataplane_driver.p4_old.p4_dataplane import P4DataPlane
from sonata.dataplane_driver.utils import write_to_file

batch_interval = 0.5
window_length = 1
sliding_interval = 1

RESULTS_FOLDER = '/home/vagrant/dev/sonata/tests/micro_bench/recirculate/'

featuresPath = ''
redKeysPath = ''

basic = """
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

def get_sequential_code(NUMBER_OF_QUERIES):

    source = ""
    extract_header = ""
    ingress_loop = ""
    app_metadata = ""

    for qid in range(0, NUMBER_OF_QUERIES):
        qid_source, qid_extract_header, qid_ingress_loop, qid_app_metadata = get_query_composed(qid)

        source += qid_source + "\n"
        extract_header += qid_extract_header + "\n"
        ingress_loop += qid_ingress_loop + "\n"
        app_metadata += qid_app_metadata
    parse_headers = """parser parse_out_header {
	%s
	return parse_ethernet;
}   """%(extract_header)
    ingress = """
control ingress {
    apply(send_original_out);
}
"""

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

    FINAL_CODE = basic + "\n" + source + "\n" + parse_headers + "\n" + app_metadata +"\n" + ingress + "\n" + egress
    COMMANDS = ["table_set_default send_original_out do_send_original_out"]
    return FINAL_CODE, COMMANDS


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


    FINAL_CODE = basic + "\n" + source + "\n" + parse_headers + "\n" + ingress + "\n" + egress
    COMMANDS = ["table_set_default recirculate_to_ingress do_recirculate_to_ingress",
                "table_set_default send_original_out do_send_original_out"]
    return FINAL_CODE, COMMANDS

if __name__ == '__main__':

    p4_type = 'sequential'

    target_conf = {
        'compiled_srcs': '/home/vagrant/dev/sonata/tests/micro_bench/'+p4_type+'/compiled_srcs/',
        'json_p4_compiled': 'compiled_test.json',
        'p4_compiled': 'compiled_test.p4',
        'p4c_bm_script': '/home/vagrant/p4c-bmv2/p4c_bm/__main__.py',
        'bmv2_path': '/home/vagrant/bmv2',
        'bmv2_switch_base': '/targets/simple_switch',
        'switch_path': '/simple_switch',
        'cli_path': '/sswitch_CLI',
        'thriftport': 22222,
        'p4_commands': 'commands.txt',
        'p4_delta_commands': 'delta_commands.txt'
    }
    
    # Code Compilation
    COMPILED_SRCS = target_conf['compiled_srcs']
    JSON_P4_COMPILED = COMPILED_SRCS + target_conf['json_p4_compiled']
    P4_COMPILED = COMPILED_SRCS + target_conf['p4_compiled']
    P4C_BM_SCRIPT = target_conf['p4c_bm_script']

    # Initialization of Switch
    BMV2_PATH = target_conf['bmv2_path']
    BMV2_SWITCH_BASE = BMV2_PATH + target_conf['bmv2_switch_base']

    SWITCH_PATH = BMV2_SWITCH_BASE + target_conf['switch_path']
    CLI_PATH = BMV2_SWITCH_BASE + target_conf['cli_path']
    THRIFTPORT = target_conf['thriftport']

    P4_COMMANDS = COMPILED_SRCS + target_conf['p4_commands']
    P4_DELTA_COMMANDS = COMPILED_SRCS + target_conf['p4_delta_commands']

    # interfaces
    interfaces = {
        'receiver': ['m-veth-1', 'out-veth-1'],
        'sender': ['m-veth-2', 'out-veth-2'],
        'original': ['m-veth-3', 'out-veth-3']
    }
    NUMBER_OF_QUERIES = 3

    p4_src,p4_commands = get_sequential_code(NUMBER_OF_QUERIES)
    write_to_file(P4_COMPILED, p4_src)

    commands_string = "\n".join(p4_commands)
    write_to_file(P4_COMMANDS, commands_string)

    dataplane = P4DataPlane(interfaces, SWITCH_PATH, CLI_PATH, THRIFTPORT, P4C_BM_SCRIPT)
    dataplane.compile_p4(P4_COMPILED, JSON_P4_COMPILED)

    # initialize dataplane and run the configuration
    dataplane.initialize(JSON_P4_COMPILED, P4_COMMANDS)



