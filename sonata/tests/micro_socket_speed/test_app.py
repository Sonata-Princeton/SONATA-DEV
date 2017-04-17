#!/usr/bin/python
from sonata.dataplane_driver.p4_old.p4_dataplane import P4DataPlane
from sonata.dataplane_driver.utils import write_to_file
from sonata.tests.micro_tables.utils import get_sequential_code, get_filter_table
import random, logging, time
from sonata.dataplane_driver.utils import get_out

import os
import threading
from multiprocessing.connection import Client, Listener
import pickle

SERVER = False

if SERVER:
    recv_socket = ("localhost", 6666)
    sender_socket = ("localhost", 6666)
    BASE_PATH = '/home/sonata/SONATA-DEV/sonata/tests/micro_socket_speed/'
    HOME_BASE = '/home/sonata/'
else:
    recv_socket = ("localhost", 6666)
    sender_socket = ("localhost", 6666)
    BASE_PATH = '/home/vagrant/dev/sonata/tests/micro_socket_speed/'
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

def send_filter_updates(number_of_entries, conf):
    table_name = "example"

    commands = []
    for i in range(0, number_of_entries):
        IP = "%d.%d.0.0" % (random.randint(0, 255),random.randint(0, 255))
        CMD = "table_add %s _nop  %s/16 =>"%(table_name, IP)
        commands.append(CMD)

    start = "%.20f" %time.time()

    message_type = "delta"
    message = {message_type: {0: commands, 1: 1}}
    serialized_queries = pickle.dumps(message)
    conn = Client(conf)
    conn.send(serialized_queries)
    conn.close()

    end = "%.20f"%time.time()
    logger.info("update|"+str(number_of_entries)+"|"+str(start)+","+end)

class Socket(threading.Thread):
    def __init__(self,socket):
        threading.Thread.__init__(self)
        self.daemon = True
        self.socket = socket

    def run(self):
        dpd_listener = Listener(self.socket)
        while True:
            conn = dpd_listener.accept()
            raw_data = conn.recv()
            message = pickle.loads(raw_data)

if __name__ == '__main__':

    NUMBER_OF_QUERIES = 1
    MAX_TABLE_ENTRIES = 100000

    Socket(recv_socket).start()

    time.sleep(1)

    incr = 10
    ctr = 0
    entries = []

    for i in range(0, 50):
        ctr += 10
        entries.append(ctr)

    # entries = [1, 10, 10, 100]
    logger = create_return_logger(BASE_PATH+"results/tables.log")

    for entry in entries:
        send_filter_updates(entry, sender_socket)
        time.sleep(1)