#!/usr/bin/python
from sonata.dataplane_driver.p4_old.p4_dataplane import P4DataPlane
from sonata.dataplane_driver.utils import write_to_file
from sonata.tests.micro_bench.utils import get_sequential_code, get_recirculation_code, send_created_traffic
import threading, time
import logging
import sys

BASE_PATH = '/home/vagrant/dev/sonata/tests/micro_bench/results/'

class Sender(threading.Thread):
    def __init__(self, duration, packets_per_second, veth):
        threading.Thread.__init__(self)
        self.daemon = True
        self.veth = veth
        self.duration = duration
        self.packets_per_second = packets_per_second

    def run(self):
        send_created_traffic(self.duration, self.veth, self.packets_per_second)

class Receiver(threading.Thread):
    def __init__(self, total_seconds, veth, type, queries, packet_per_second):
        threading.Thread.__init__(self)
        self.daemon = True
        self.receiver_stats_file = "/sys/class/net/%s/statistics/rx_packets"%veth
        self.monitoring_seconds = total_seconds
        self.extra_monitoring = 5

        self.type = type
        self.queries = queries
        self.packet_per_second = packet_per_second

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(BASE_PATH+"Receiver.log")
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def run(self):

        for second in range(0, self.monitoring_seconds+self.extra_monitoring):
            with open(self.receiver_stats_file) as f:
                for line in f:
                    in_stat = int(line)
            time.sleep(1)
            with open(self.receiver_stats_file) as f:
                for line in f:
                    out_stat = int(line)
            rate = (out_stat-in_stat)
            print "Rate: ", rate, " per seconds\n"
            logging_info = [self.type, str(self.packet_per_second), str(self.queries), str(self.monitoring_seconds), str(rate)]
            compose_line = ",".join(logging_info)
            self.logger.info(compose_line)

if __name__ == '__main__':

    NUMBER_OF_QUERIES = int(sys.argv[1])
    p4_type = sys.argv[2]
    # P4_TYPES = ['recirculate', 'sequential']
    # NUMBER_OF_QUERIES_ARRAY = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    #
    # for p4_type in P4_TYPES:

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
    # NUMBER_OF_QUERIES = 100
    NUMBER_OF_PACKETS_PER_SECOND = 100
    TOTAL_DURATION = 30

    VETH_SEND = "out-veth-1"
    VETH_RECIEVE = "out-veth-3"

    if p4_type == 'recirculate': p4_src,p4_commands = get_recirculation_code(NUMBER_OF_QUERIES)
    else: p4_src,p4_commands = get_sequential_code(NUMBER_OF_QUERIES)
    write_to_file(P4_COMPILED, p4_src)

    commands_string = "\n".join(p4_commands)
    write_to_file(P4_COMMANDS, commands_string)

    dataplane = P4DataPlane(interfaces, SWITCH_PATH, CLI_PATH, THRIFTPORT, P4C_BM_SCRIPT)
    dataplane.compile_p4(P4_COMPILED, JSON_P4_COMPILED)

    # initialize dataplane and run the configuration
    dataplane.initialize(JSON_P4_COMPILED, P4_COMMANDS)

    receiver = Receiver(TOTAL_DURATION, VETH_RECIEVE, p4_type, NUMBER_OF_QUERIES, NUMBER_OF_PACKETS_PER_SECOND)
    receiver.start()

    time.sleep(1)
    sender = Sender(TOTAL_DURATION, NUMBER_OF_PACKETS_PER_SECOND, VETH_SEND)
    sender.start()

    receiver.join()
    sender.join()



    dataplane.net.stop()



