from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener

INTERFACE = 'eth0'

def load_data():
    print "load_data called"
    data = {}
    fname = "/home/arp/SONATA-DEV/data/udp_traffic_equinix-chicago.20160121-130000.UTC.csv"
    with open(fname, 'r') as f:
        for line in f:
            tmp = line.split("\n")[0].split(",")
            ts = round(float(line.split(",")[0]),0)
            if ts not in data:
                data[ts] = []
            data[ts].append(tuple(line.split("\n")[0].split(",")))
    print "Number of TS: ", len(data.keys())
    return data


def send_packet(pkt_tuple):
    (sIP, sPort, dIP, dPort, nBytes, proto, sMac, dMac) = pkt_tuple
    p = Ether() / IP(dst=dIP, src=sIP) / TCP(dport=int(dPort), sport=int(sPort)) / "SONATA"
    sendp(p, iface = "out-veth-1", verbose=0)

def create_normal_traffic(number_of_packets):
    normal_packets = []

    for i in range(number_of_packets):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / TCP() / "SONATA NORMAL"
        normal_packets.append(p)

    return normal_packets

def create_attack_traffic(number_of_packets):
    dIP = '99.7.186.25'
    sIPs = []
    attack_packets = []

    for i in range(number_of_packets):
        sIPs.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))

    for sIP in sIPs:
        p = Ether() / IP(dst=dIP, src=sIP) / TCP() / "ATTACK"
        attack_packets.append(p)

    return attack_packets

def compose_packet(pkt_tuple):
    random_number = random.randint(1, 10000)
    payload_string = "SONATA"+str(random_number)
    (sIP, sPort, dIP, dPort, nBytes, proto, sMac, dMac) = pkt_tuple
    p = Ether() / IP(dst=dIP, src=sIP) / TCP(dport=int(dPort), sport=int(sPort)) / payload_string
    return p


def send_dummy_packets(mode):
    if mode == 0:
        sIPs = ['112.7.186.20', '112.7.186.19', '112.7.186.19', '112.7.186.18']
        for sIP in sIPs:
            p = Ether() / IP(dst='112.7.186.25', src=sIP) / TCP() / "SONATA"
            p.summary()
            sendp(p, iface = "out-veth-1", verbose=0)
    else:
        sIPs = ['121.7.186.20', '121.7.186.19', '121.7.186.19', '121.7.186.18']
        for sIP in sIPs:
            p = Ether() / IP(dst='121.7.186.25', src=sIP) / TCP() / "ATTACK"
            p.summary()
            sendp(p, iface = "out-veth-1", verbose=0)



def send_dummy_packets_stream():
    sIPs = ['112.7.186.20', '112.7.186.19', '112.7.186.19', '112.7.186.18']
    for sIP in sIPs:
        send_tuple = ",".join([qid, dIP, sIP])+"\n"
        print "Tuple: ", send_tuple

class PicklablePacket:
    """A container for scapy packets that can be pickled (in contrast
    to scapy packets themselves)."""
    def __init__(self, pkt):
        self.contents = str(pkt)
        self.time = pkt.time

    def __call__(self):
        """Get the original scapy packet."""
        pkt = scapy.Ether(self.contents)
        pkt.time = self.time
        return pkt

def send_created_traffic():
    traffic_dict = {}
    for i in range(0, 20):
        traffic_dict[i] = []
        if i > 5 and i < 11:
            traffic_dict[i].extend(create_attack_traffic(500))
            traffic_dict[i].extend(create_normal_traffic(350))
        else:
            traffic_dict[i].extend(create_normal_traffic(500))

    for i in range(0, 20):
        print "Sending traffic for ts: " + str(i)
        start = time.time()
        sendp(traffic_dict[i], iface=INTERFACE, verbose=0)
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)


def send_packets(use_composed = True):
    '''
    reads packets from IPFIX data file,
    sorts the time stamps, and
    sends them at regular intervals to P4-enabled switch.
    '''
    ipfix_data = load_data()
    ordered_ts = ipfix_data.keys()
    ordered_ts.sort()
    print "Total flow entries:", len(ordered_ts)

    packet_count = {}
    composed_packets = {}
    attack_packets = {}
    if use_composed:
        with open("/home/arp/SONATA-DEV/data/composed_packets.pickle",'r') as f:
            composed_packets = pickle.load(f)
            #print composed_packets
    else:
        start = time.time()
        ctr = 1
        for ts in ordered_ts:
            composed_packets[ts] = []
            attack_packets[ts] = []

            pkt_tuples = ipfix_data[ts][:1000]
            packet_count[ts] = len(ipfix_data[ts])
            if ctr >= 10 and ctr <= 30:
                attack_packets[ts].extend(create_attack_traffic())
            for pkt_tuple in pkt_tuples:
                composed_packets[ts].append(compose_packet(pkt_tuple[2:]))
            ctr += 1

        with open("composed_packets.pickle",'w') as f:
            pickle.dump(composed_packets, f)

        end = time.time()
        print "Time to compose: ", str(end-start)


    print packet_count

    ctr = 1
    counter = {}
    for ts in ordered_ts:
        counter[ts] = 0
        start = time.time()
        print "Number of packets in:", ts, " are ", len(composed_packets[ts])
        #outgoing_packets = composed_packets[ts]
        outgoing_packets = composed_packets[ts]
        if ctr >= 10 and ctr <= 30:
            counter[ts] += 1000
            print "Sending Attack traffic..."
            #attack_packets = create_attack_traffic()
            sendp(attack_packets[ts], iface = "out-veth-1", verbose=0)
            sendp(outgoing_packets[:100], iface = "out-veth-1", verbose=0)
        else:
            sendp(outgoing_packets, iface = "out-veth-1", verbose=0)
        counter[ts] += 1000
        total = time.time()-start
        sleep_time = 0.5-total
        print "Finished Sending...", str(total), "sleeping for: ", sleep_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        ctr += 1

#send_packets(False)
send_created_traffic()
"""
print "Sending dummy packets: ...."
send_dummy_packets(0)
send_dummy_packets(1)
time.sleep(1)
"""