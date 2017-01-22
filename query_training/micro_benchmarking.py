#!/usr/bin/env python
#  Author:
#  Ankita Pawar (ankscircle@gmail.com)


from multiprocessing.connection import Listener, Client
from micro.topo import initialize_switch
from threading import Thread
import random
import socket
import struct
import time, pickle, logging
import subprocess
from micro.topo import CLI_PATH, THRIFTPORT, BASE_PATH
from fabric_manager.switch_config.utils import reset_switch_state

FM_SOCKET = ('localhost', 8989)
MACRO_BENCH_FILE = 'macro_bench.log'
DELTA_COMMANDS_FILE = BASE_PATH + "delta_commands.txt"
MICRO_BENCHMARKING_PATH = BASE_PATH + "micro_bench.pickle"

def start_fabric_managers():
    # Start the fabric managers local to each data plane element

    fm_listener = Listener(FM_SOCKET)
    while True:
        conn = fm_listener.accept()
        raw_data = conn.recv()


def start_switch_for_delta_update():
    # Start the fabric managers local to each data plane element
    initialize_switch()


def generate_random_reduction_keys():
    number_of_rk = [1, 10, 100, 1000, 10000]

    json_for_rk = {}
    for range_rk in number_of_rk:
        json_for_rk[range_rk] = []
        for i in range(range_rk):
            json_for_rk[range_rk].append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))


    return json_for_rk

def send_commands_to_dp(COMMAND_PATH, cli_path = CLI_PATH, p4_json_path = BASE_PATH + "join.json", thrift_port=THRIFTPORT):
    cmd = [cli_path, p4_json_path, str(thrift_port)]
    with open(COMMAND_PATH, "r") as f:
        print " ".join(cmd)
        try:
            output = subprocess.check_output(cmd, stdin = f)
            #print output
        except subprocess.CalledProcessError as e:
            print e
            #print e.output
            raise RuntimeError

def write_to_file(path, content):
    with open(path, 'w') as fp:
        fp.write(content)

if __name__ == "__main__":

    recording = {}

    recording['fm_send'] = {}
    recording['switch_update'] = {}
    recording['switch_reset'] = {}


    fm_thread = Thread(name='fabric_manager', target=start_fabric_managers)
    fm_thread.daemon = True
    fm_thread.start()
    start_switch_for_delta_update()

    json_for_reduction_keys = generate_random_reduction_keys()
    print json_for_reduction_keys

    print "========================Testing FM send time========================"

    for number_of_rk in json_for_reduction_keys:
        recording['fm_send'][number_of_rk] = {}
        start = time.time()
        serialized_reduction_keys = pickle.dumps(json_for_reduction_keys[number_of_rk])
        conn = Client(FM_SOCKET)
        conn.send(serialized_reduction_keys)
        recording['fm_send'][number_of_rk] = { 'start': start, 'end': time.time()}


    print "========================Testing Switch update time========================"

    for number_of_rk in json_for_reduction_keys:
        recording['switch_update'][number_of_rk] = {}
        recording['switch_reset'][number_of_rk] = {}

        start = time.time()
        commands = ''
        for reduction_key in json_for_reduction_keys[number_of_rk]:
            filter_table_fname = 'forward'
            action = 'set_default_nhop'
            command = 'table_add '+filter_table_fname+' '+ action + ' '+str(reduction_key) +' => 1 00:00:00:00:00:01\n'
            commands += command

        write_to_file(DELTA_COMMANDS_FILE, commands)
        send_commands_to_dp(DELTA_COMMANDS_FILE)
        recording['switch_update'][number_of_rk] = { 'start': start, 'end': time.time()}

        print "\t=========Testing Switch reset time========="
        start = time.time()
        reset_switch_state()
        send_commands_to_dp(BASE_PATH + "commands.txt")
        print "finished:", number_of_rk
        recording['switch_reset'][number_of_rk] = { 'start': start, 'end': time.time()}

    with open(MICRO_BENCHMARKING_PATH,'w') as f:
        print "Dumping refined Queries ..."
        pickle.dump(recording, f)





