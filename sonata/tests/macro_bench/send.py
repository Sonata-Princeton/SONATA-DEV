from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener
import math
from random import randint

SERVER = False
NORMAL_PACKET_COUNT = 50
ATTACK_PACKET_COUNT = 50
if SERVER:
    INTERFACE = 'eth0'
    PCAP_LOCATION = '/home/sonata/SONATA-DEV/sonata/tests/macro_bench/campus_udp_1min.pcap'
else:
    INTERFACE = 'out-veth-1'
    PCAP_LOCATION = '/home/vagrant/dev/sonata/tests/macro_bench/campus_udp_1min.pcap'

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


def send_dummy_packets_stream():
    sIPs = ['112.7.186.20', '112.7.186.19', '112.7.186.19', '112.7.186.18']
    for sIP in sIPs:
        send_tuple = ",".join([qid, dIP, sIP])+"\n"
        print "Tuple: ", send_tuple

def send_created_traffic():
    traffic_dict = {}
    attack = True
    total_duration = 20
    attack_duration = 5
    attack_start_time = 10
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

        sendp(traffic_dict[i], iface="out-veth-1", verbose=0)
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)

def send_campus_data():
    packets = rdpcap(PCAP_LOCATION)
    DURATION = 60
    T = len(packets)/DURATION

    packets_based_on_ts = {}



    for packet in packets:
        ts = math.ceil(packet.time)
        if ts not in packets_based_on_ts:
            packets_based_on_ts[ts] = []

        packets_based_on_ts[ts].append(packet)


    timestamps = packets_based_on_ts.keys()
    timestamps.sort()

    # packet_count = []
    # for ts in timestamps:
    #     packet_count.append(len(packets_based_on_ts[ts]))

    # print packet_count
    packet_count = []
    ctr = 0
    for ts in timestamps:
        print "Timstamp: ",ts
        total = 0
        start = time.time()
        rand = randint(0,50)
        packets_based_on_ts[ts] = packets_based_on_ts[ts][:100+rand]
        total = 100+rand
        if ctr > 20 and ctr < 31:
            # 304 packets on server
            packets_based_on_ts[ts].extend(create_attack_traffic(304))
            total += 304
        ctr += 1
        packet_count.append(total)
        sendp(packets_based_on_ts[ts], iface = INTERFACE, verbose=0)
        total = time.time()-start
        sleep_time = 1 - total
        print sleep_time

        if sleep_time > 0:
            time.sleep(sleep_time)

    print packet_count

# send_campus_data()
send_created_traffic()