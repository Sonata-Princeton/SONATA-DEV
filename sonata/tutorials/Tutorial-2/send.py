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


def create_normal_traffic():
    number_of_packets = NORMAL_PACKET_COUNT
    normal_packets = []

    for i in range(5):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / TCP(flags='S')
        normal_packets.append(p)

    for i in range(number_of_packets):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / TCP(flags='A')
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
        # TCP SYN Packets
        p = Ether() / IP(dst=dIP, src=sIP) / TCP(dport=5555, flags='S')

        attack_packets.append(p)

    return attack_packets


def send_packets():
    all_traffic = []

    all_traffic.extend(create_normal_traffic())
    all_traffic.extend(create_attack_traffic())
    sendp(all_traffic, iface=IFACE, verbose=0)

send_packets()
