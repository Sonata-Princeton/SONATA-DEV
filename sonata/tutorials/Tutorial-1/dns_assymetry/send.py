from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener

NORMAL_PACKET_COUNT = 10
ATTACK_PACKET_COUNT = 10

IFACE = "out-veth-1"
dns_port = 53

def create_normal_traffic():
    number_of_packets = NORMAL_PACKET_COUNT
    normal_packets = []

    for i in range(number_of_packets):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / TCP() / "SONATA NORMAL"
        normal_packets.append(p)
        # normal_packets.append(p1)
        # normal_packets.append(p2)

    return normal_packets


def create_attack_traffic():
    number_of_packets = ATTACK_PACKET_COUNT
    attack_packets = []

    IP1 = '99.7.186.25'

    IP2 = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    p2 = Ether() / IP(dst=IP2, src=IP1) / UDP(dport=dns_port)
    attack_packets.append(p2)

    for i in range(number_of_packets):
        IP2 = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p1 = Ether() / IP(dst=IP1, src=IP2) / UDP(sport=dns_port)
        attack_packets.append(p1)

    return attack_packets


def send_created_traffic():
    traffic_dict = {}
    attack = True

    total_duration = 60
    attack_duration = 50
    attack_start_time = 5

    for i in range(0, total_duration):
        traffic_dict[i] = []
        traffic_dict[i].extend(create_normal_traffic())
        if i >= attack_start_time and i < attack_start_time + attack_duration:
            traffic_dict[i].extend(create_attack_traffic())

    print "******************** Sending Normal Traffic *************************"
    for i in range(0, total_duration):
        # print "Sending traffic for ts: " + str(i)
        start = time.time()
        if i >= attack_start_time and i < attack_start_time + attack_duration and attack:
            attack = False
            print "******************** Sending Asymmetric Traffic *************************"
        if i == attack_start_time + attack_duration:
            attack = False

        if not attack and i > attack_start_time + attack_duration:
            attack = True
            print "******************** Sending Normal Traffic *************************"

        sendp(traffic_dict[i], iface=IFACE, verbose=0)
        total = time.time() - start
        sleep_time = 1 - total
        print "Sending", len(traffic_dict[i]), "packets at T=", i, "before sleeping for", sleep_time, "seconds."
        if sleep_time > 0:
            time.sleep(sleep_time)


send_created_traffic()
