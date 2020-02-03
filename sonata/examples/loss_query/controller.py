#!/usr/bin/python3
import json

from scapy.all import *

import base64
from interfaces import get_out

EPOCH_LEN = {}
for p in range(10):
    EPOCH_LEN[p] = float(2 ** (20 + p)) / float(10 ** 6)

EPOCH_POWER = 0  # SET TO MATCH LOSS_QUERY.P4!


def int_to_IP(num):
    return '.'.join([str((num >> 8 * i) % 256) for i in [3, 2, 1, 0]])


def parse_register_val(val_int):
    val_hex = hex(val_int)[2:].zfill(14)
    epoch = int(val_hex[0:2], 16)
    count = int(val_hex[2:6], 16)
    IP = int_to_IP(int(val_hex[6:14], 16))
    return epoch, count, IP


class Controller(object):
    def __init__(self):
        self.count = 0
        self.reader_thread = Thread(name='reader_thread', target=self.read_registers)
        self.sniffing_thread = Thread(name='sniffing_thread', target=self.sniff_interface)

        self.data = {}

        self.epoch_len = EPOCH_LEN[EPOCH_POWER]
        self.start_time = -1
        self.current_epoch = 0

        self.collecting_registers = Lock()
        self.experiment_start = Event()
        self.stop_cond = Event()

    # noinspection PyUnresolvedReferences
    def read_registers(self):
        self.experiment_start.wait()
        print("Starting experiment. Epoch 0: %ss" % self.start_time)

        while True:
            if self.stop_cond.is_set():
                break
            time.sleep(self.epoch_len)

            self.collecting_registers.acquire()

            with open("register_commands.txt", 'a') as f:
                f.write("register_read collision_counts %s\n" % self.current_epoch)
                f.write("register_read egress_collision_counts %s\n" % self.current_epoch)

            print("Epoch %s: %ss" % (self.current_epoch, time.time()))

            IP_results = {}
            collision_results = {}

            register_out_lines = get_out("simple_switch_CLI < register_commands.txt")[1].splitlines()

            line_index = -1
            found = False
            for i, line in enumerate(register_out_lines):
                if line.startswith("RuntimeCmd:"):
                    line_index = i
                    found = True
                    break

            # read registers and collect output
            while found and line_index < len(register_out_lines):
                # pdb.set_trace()
                next_line = register_out_lines[line_index]
                if "collision" in next_line:  # collision count
                    print("collision_counts")
                    next_line_parse = re.search(r"collision_counts\[(\d+)\]= (\d+)", next_line)
                    if not next_line_parse:
                        print("ERROR! Could not parse output")
                    ingress_epoch, ingress_count = [int(x) for x in next_line_parse.groups()]

                    next_line = register_out_lines[line_index + 1]
                    next_line_parse = re.search(r"egress_collision_counts\[(\d+)\]= (\d+)", next_line)
                    if not next_line_parse:
                        print("ERROR! Could not parse output")
                    egress_epoch, egress_count = [int(x) for x in next_line_parse.groups()]

                    if ingress_epoch == egress_epoch:
                        if ingress_epoch in collision_results and collision_results[ingress_epoch] != ingress_count - egress_count:
                            print("ERROR!! Same epoch but different results??")
                        collision_results[ingress_epoch] = ingress_count - egress_count
                    else:
                        print("WARNING: Different epochs!")

                elif "counts" in next_line:  # counts
                    print("IP counts")
                    next_line_parse = re.search(r"counts_.\[(\d+)\]= (\d+)", next_line)
                    if not next_line_parse:
                        print("ERROR! Could not parse output")
                    ingress_key, ingress_val = [int(x) for x in next_line_parse.groups()]
                    ingress_epoch, ingress_count, ingress_IP = parse_register_val(ingress_val)

                    next_line = register_out_lines[line_index + 1]
                    next_line_parse = re.search(r"egress_counts_.\[(\d+)\]= (\d+)", next_line)
                    if not next_line_parse:
                        print("ERROR! Could not parse output")
                    egress_key, egress_val = [int(x) for x in next_line_parse.groups()]
                    egress_epoch, egress_count, egress_IP = parse_register_val(egress_val)

                    if ingress_epoch != egress_epoch:
                        print("WARNING: Different epochs!")
                    IP_results[ingress_IP] = ingress_count - egress_count
                else:
                    break
                line_index += 2
            self.data[self.current_epoch] = (IP_results, collision_results)
            self.current_epoch += 1
            if os.path.exists("register_commands.txt"):
                os.remove("register_commands.txt")
            self.collecting_registers.release()

    def process_packet(self, pkt):
        if self.stop_filter(pkt):
            return
        self.collecting_registers.acquire()
        # pdb.set_trace()
        pkt_str = base64.b16encode(bytes(pkt))
        ingress_timestamp_ns = int(pkt_str[:12], 16)
        ingress_stage = int(pkt_str[12:14], 16)
        ingress_key = int(pkt_str[14:22], 16)
        egress_stage = int(pkt_str[22:24], 16)
        egress_key = int(pkt_str[24:32], 16)
        epoch = int(pkt_str[32:34], 16)
        rest = Ether(base64.b16decode(pkt_str[34:]))
        with open("packets.log", 'a') as f:
            f.write("%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % (pkt, pkt_str, ingress_timestamp_ns, ingress_stage, ingress_key, egress_stage, egress_key, epoch))

        source_IP = rest[IP].src

        if rest[IP].version == 0:  # RESTART TIMESTAMP
            self.start_time = ingress_timestamp_ns / (10 ** 9)
            self.experiment_start.set()

        elif ingress_stage != 4:
            with open("register_commands.txt", 'a') as f:
                f.write("register_read counts_%s %s\n" % (ingress_stage, egress_key)) # NOTE EGRESS KEY!! Can we make this assumption?
                f.write("register_read egress_counts_%s %s\n" % (egress_stage, egress_key))

        self.collecting_registers.release()

        # issue: check the current epoch for collisions. (How do we get the current epoch #, from script or server?
        # SOLVED: Epochs are now synced with an "experiment start" packet.

    def stop_filter(self, pkt):
        if IP in pkt and pkt[IP].version == 1:
            self.stop_cond.set()
            return True
        return False

    def sniff_interface(self):
        sniff(iface="out-veth-2", prn=self.process_packet, stop_filter=self.stop_filter)
        print("SNIFFING STOPPED")

    def run(self):
        if os.path.exists("register_commands.txt"):
            os.remove("register_commands.txt")
        self.sniffing_thread.start()
        self.reader_thread.start()
        self.stop_cond.wait()

        self.sniffing_thread.join()
        self.reader_thread.join()

        with open("results/%s.json" % (datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")), 'w') as f:
            json.dump(self.data, f)


if __name__ == "__main__":
    c = Controller()
    c.run()
