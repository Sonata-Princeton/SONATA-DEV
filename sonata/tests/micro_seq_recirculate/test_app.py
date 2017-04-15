#!/usr/bin/python
from sonata.tests.micro_seq_recirculate.utils import send_created_traffic
import threading, time
import logging
import sys, threading, os
from sonata.query_engine.sonata_queries import *
from multiprocessing.connection import Client
import pickle
from sonata.core.partition import get_dataplane_query

SERVER = True

if SERVER:
    BASE_PATH = '/home/sonata/SONATA-DEV/sonata/tests/micro_seq_recirculate/results/'
    VETH_SEND = "out-veth-1"
    VETH_RECIEVE = "out-veth-3"
    dp_driver_conf = ('172.17.0.101', 6666)
else:
    BASE_PATH = '/home/vagrant/dev/sonata/tests/micro_seq_recirculate/results/'
    VETH_SEND = "out-veth-1"
    VETH_RECIEVE = "out-veth-3"
    dp_driver_conf = ('localhost', 6666)

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

class Switch(threading.Thread):
    def __init__(self,p4_json_path, switch_path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.switch_path = switch_path
        self.p4_json_path = p4_json_path

    def run(self):
        COMMAND = "sudo %s %s -i 11@m-veth-1 -i 12@m-veth-2 -i 13@m-veth-3 --thrift-port 22222 &"%(self.switch_path, self.p4_json_path)
        print COMMAND
        os.system(COMMAND)

def send_to_dp_driver(message_type, content, conf):
    # Send compiled query expression to fabric manager
    # start = time.time()
    message = {message_type: {0: content, 1: 1}}
    serialized_queries = pickle.dumps(message)
    conn = Client(conf)
    conn.send(serialized_queries)
    # self.logger.info("runtime,fm_" + message_type + "," + str(start) + "," + str(time.time()))
    time.sleep(1)
    conn.close()
    return ''

if __name__ == '__main__':

    NUMBER_OF_QUERIES = int(sys.argv[1])
    p4_type = sys.argv[2]
    NUMBER_OF_PACKETS_PER_SECOND = 100
    TOTAL_DURATION = 30

    # New Queries
    q1 = (PacketStream(1)
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 1))
          .map(keys=('dIP',))
          )

    dp_query = get_dataplane_query(q1, 1, 6)

    queries = {}

    for qid in range(0, NUMBER_OF_QUERIES):
        queries[qid] = dp_query


    send_to_dp_driver('init',queries,dp_driver_conf)
    time.sleep(3)

    if not SERVER:
        receiver = Receiver(TOTAL_DURATION, VETH_RECIEVE, p4_type, NUMBER_OF_QUERIES, NUMBER_OF_PACKETS_PER_SECOND)
        receiver.start()

        time.sleep(1)
        sender = Sender(TOTAL_DURATION, NUMBER_OF_PACKETS_PER_SECOND, VETH_SEND)
        sender.start()

        receiver.join()
        sender.join()


