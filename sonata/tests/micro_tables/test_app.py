#!/usr/bin/python
from sonata.dataplane_driver.p4_old.p4_dataplane import P4DataPlane
from sonata.dataplane_driver.utils import write_to_file
from sonata.tests.micro_tables.utils import get_sequential_code, get_filter_table
import random, logging, time
from sonata.dataplane_driver.utils import get_out

import os
import threading

SERVER = True

if SERVER:
    internal_interfaces = {"ens1f0": 11, "ens1f1":10, "ens4f0": 12}
    BASE_PATH = '/home/sonata/SONATA-DEV/sonata/tests/micro_tables/'
    HOME_BASE = '/home/sonata/'
else:
    internal_interfaces = {"m-veth-1": 11, "m-veth-2":12, "m-veth-3": 13}
    BASE_PATH = '/home/vagrant/dev/sonata/tests/micro_tables/'
    HOME_BASE = '/home/vagrant/'

def create_return_logger(PATH):
    # create a logger for the object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create file handler which logs messages
    fh = logging.FileHandler(PATH)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger

def delete_entries_from_table(number_of_entries,table_name,dataplane,JSON_P4_COMPILED,P4_DELTA_COMMANDS, logger):
    commands_string = ""
    for i in range(0, number_of_entries):
        CMD = "table_delete %s %s"%(table_name, i)
        commands_string += CMD + "\n"

    start = "%.20f" %time.time()
    dataplane.send_delta_commands(commands_string)
    end = "%.20f"%time.time()

    logger.info("delete|"+str(number_of_entries)+"|"+str(start)+","+end)


def add_entries_to_table(number_of_entries, table_name, p4_dataplane_obj, JSON_P4_COMPILED, P4_DELTA_COMMANDS, logger):


    commands_string = ""
    for i in range(0, number_of_entries):
        IP = "%d.%d.0.0" % (random.randint(0, 255),random.randint(0, 255))
        CMD = "table_add %s _nop  %s/16 =>"%(table_name, IP)
        commands_string += CMD + "\n"

    start = "%.20f" %time.time()
    p4_dataplane_obj.send_delta_commands(commands_string)
    end = "%.20f"%time.time()

    logger.info("update|"+str(number_of_entries)+"|"+str(start)+","+end)

class Switch(threading.Thread):
    def __init__(self,p4_json_path, switch_path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.switch_path = switch_path
        self.p4_json_path = p4_json_path

    def run(self):
        compose_interfaces = ""
        for inter,port in internal_interfaces.iteritems():
            new_interface = " -i %s@%s "%(port,inter)
            compose_interfaces +=new_interface

        COMMAND = "sudo %s %s %s --thrift-port 22222"%(self.switch_path, self.p4_json_path, compose_interfaces)
        print COMMAND
        os.system(COMMAND)

def initialize_the_switch(p4_json_path, switch_path):
    CMDS = [switch_path, p4_json_path, '-i','11@m-veth-1','-i','12@m-veth-2','-i','13@m-veth-3','--thrift-port','22222']
    COMMAND = "nohup sudo %s %s -i 11@m-veth-1 -i 12@m-veth-2 -i 13@m-veth-3 --thrift-port 22222 >/dev/null 2>&1"%(switch_path, p4_json_path)
    print COMMAND
    # os.spawnl(os.P_NOWAIT, COMMAND)
    os.system(COMMAND)
    # subprocess.Popen(CMDS)
    time.sleep(1)
    # print COMMAND
    # get_out(COMMAND)

if __name__ == '__main__':

    NUMBER_OF_QUERIES = 1
    MAX_TABLE_ENTRIES = 100000

    target_conf = {
        'compiled_srcs': BASE_PATH +'compiled_srcs/',
        'json_p4_compiled': 'compiled_test.json',
        'p4_compiled': 'compiled_test.p4',
        'p4c_bm_script': HOME_BASE + 'p4c-bmv2/p4c_bm/__main__.py',
        'bmv2_path': HOME_BASE + 'bmv2',
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

    p4_src,p4_commands,filter_table_name = get_sequential_code(NUMBER_OF_QUERIES, MAX_TABLE_ENTRIES)

    write_to_file(P4_COMPILED, p4_src)

    commands_string = "\n".join(p4_commands)
    write_to_file(P4_COMMANDS, commands_string)

    dataplane = P4DataPlane(interfaces, SWITCH_PATH, CLI_PATH, THRIFTPORT, P4C_BM_SCRIPT)
    dataplane.compile_p4(P4_COMPILED, JSON_P4_COMPILED)
    dataplane.create_interfaces()

    cmd = dataplane.switch_path + " >/dev/null 2>&1"
    get_out(cmd)

    # initialize_the_switch(JSON_P4_COMPILED, SWITCH_PATH)
    Switch(JSON_P4_COMPILED, SWITCH_PATH).start()

    time.sleep(1)

    dataplane.send_commands(JSON_P4_COMPILED, P4_COMMANDS)

    # initialize dataplane and run the configuration
    # dataplane.initialize(JSON_P4_COMPILED, P4_COMMANDS)

    incr = 10
    ctr = 0
    entries = []

    for i in range(0, 50):
        ctr += 10
        entries.append(ctr)

    # entries = [1, 10, 10, 100]
    logger = create_return_logger(BASE_PATH+"results/tables.log")

    for entry in entries:
        add_entries_to_table(entry,filter_table_name,dataplane,JSON_P4_COMPILED,P4_DELTA_COMMANDS,logger)
        delete_entries_from_table(entry,filter_table_name,dataplane,JSON_P4_COMPILED,P4_DELTA_COMMANDS,logger)