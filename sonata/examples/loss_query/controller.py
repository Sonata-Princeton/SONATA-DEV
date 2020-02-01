#!/usr/bin/python
from scapy.all import *
from collections import OrderedDict
from threading import Thread, Event, Lock
import os
import time
from interfaces import get_out

EPOCH_LEN = { # ms
    0: 1.24,
    1: 2.48,
    2: 4.096,
    3: 8.192,
    4: 16.384
}

EPOCH_POWER = 0

class Controller(object):
    def __init__(self):
        self.count = 0
        self.reader_thread = Thread(name='reader_thread', target=self.read_registers)
        self.reader_thread.start()

        self.sniffing_thread = Thread(name='sniffing_thread', target=self.sniff_interface())

        self.data = OrderedDict()

        self.collecting_registers = Lock()

        self.epoch_len = EPOCH_LEN[EPOCH_POWER]

    def read_registers(self):
        last_time = time.time() / 1000
        IP_index = 0
        while True:
            curr_time = time.time() / 1000
            if last_time - curr_time > self.epoch_len:
                self.collecting_registers.acquire()
                last_time = curr_time
                results = {}

                register_out_lines = get_out("simple_switch_CLI < register_commands_txt").splitlines()
                line_index = -1
                for i, line in enumerate(register_out_lines):
                    if line.startswith("RuntimeCmd:"):
                        line_index = i
                        break
                while True:
                    next_line = register_out_lines[line_index]
                    if not "collision" in line: #IP
                        #
                    else:

                            register_num = line.split("= ")[1]
                        else: # collision count
                self.data = OrderedDict()

                if os.path.exists("register_commands.txt"):
                  os.remove("register_commands.txt")
                IP_index = -1
                self.collecting_registers.release()


    def process_packet(self, pkt):
        self.collecting_registers.acquire()
        pkt_str = str(pkt).encode("hex")
        ingress_stage = int(pkt_str[0], 16)
        ingress_key = int(pkt_str[1:5], 16)
        egress_stage = int(pkt_str[5], 16)
        egress_key = int(pkt_str[6:10], 16)
        rest = Ether(pkt_str[10:].decode("hex"))

        source_IP = rest[IP].src

        self.data[source_IP] = ((ingress_stage, ingress_key), (egress_stage, egress_key))

        with open('register_commands.txt', 'a') as f:
            if ingress_stage == 4:
                f.write("register_read collision_counts %s\n" % (ingress_key))
            else:
                f.write("register_read counts_%s %s\n" % (ingress_stage, ingress_key))
            if egress_stage == 9:
                f.write("register_read egress_collision_counts %s\n" % (egress_key))
            else:
                f.write("register_read egress_counts_%s %s\n" % (egress_stage, egress_key))

        pkt.show()

        self.collecting_registers.release()

    def sniff_interface(self):
        sniff(iface="out-veth-2", prn=self.process_packet)

    def run(self):
        self.sniffing_thread.start()


if __name__ == "__main__":
    c = Controller()
    c.run()