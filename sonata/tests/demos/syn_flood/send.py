from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener


NORMAL_PACKET_COUNT = 50
ATTACK_PACKET_COUNT = 60


IFACE = "out-veth-1"
#IFACE = "m-veth-1"

def send_packet(pkt_tuple):
    (sIP, sPort, dIP, dPort, nBytes, proto, sMac, dMac) = pkt_tuple
    p = Ether() / IP(dst=dIP, src=sIP) / TCP(dport=int(dPort), sport=int(sPort)) / "SONATA"
    sendp(p, iface = IFACE, verbose=0)

def create_normal_traffic():
    number_of_packets = NORMAL_PACKET_COUNT
    normal_packets = []

    for i in range(number_of_packets):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / TCP() / "SONATA NORMAL"
        # print p.summary()
        normal_packets.append(p)

    return normal_packets

def create_attack_traffic():
    number_of_packets = ATTACK_PACKET_COUNT
    dIP = '99.7.186.25'
    sIPs = []
    attack_packets = []

    for i in range(number_of_packets):
        sIPs.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))

    for sIP in sIPs:
        p = Ether() / IP(dst=dIP, src=sIP) / UDP(sport=53)/DNS(nscount=1, ns=DNSRR(type=46))
        # print p.show()
        # print sIP, p.proto, p.sport, p.ns.type
        # print len(str(p)), "Ether(): ", len(str(Ether())), "IP: ", len(str(IP(dst=dIP, src=sIP))), \
        #     "UDP: ",len(str(UDP(sport=53))),"DNS: ", len(str(DNS(nscount=1, ns=DNSRR(type=46)))), "\n"
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
            sendp(p, iface = IFACE, verbose=0)
    else:
        sIPs = ['121.7.186.20', '121.7.186.19', '121.7.186.19', '121.7.186.18']
        for sIP in sIPs:
            p = Ether() / IP(dst='121.7.186.25', src=sIP) / TCP() / "ATTACK"
            p.summary()
            sendp(p, iface = IFACE, verbose=0)



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
    attack = True

    total_duration = 30
    attack_duration = 10
    attack_start_time = 5

    for i in range(0, total_duration):
        traffic_dict[i] = []
        traffic_dict[i].extend(create_normal_traffic())
        if i >= attack_start_time and i < attack_start_time+attack_duration:
            traffic_dict[i].extend(create_attack_traffic())

    print "******************** Sending Normal Traffic *************************"
    for i in range(0, total_duration):
        # print "Sending traffic for ts: " + str(i)
        start = time.time()
        if i >= attack_start_time and i < attack_start_time+attack_duration and attack:
            attack = False
            print "******************** Sending Attack Traffic *************************"
        if i == attack_start_time+attack_duration:
            attack = False

        if not attack and i > attack_start_time+attack_duration:
            attack = True
            print "******************** Sending Normal Traffic *************************"

        sendp(traffic_dict[i], iface=IFACE, verbose=0)
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)

send_created_traffic()
