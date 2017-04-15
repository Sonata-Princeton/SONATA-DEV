from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener

SERVER = True

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
    for i in range(0, 20):
        traffic_dict[i] = []
        if i > 5 and i < 11:
            traffic_dict[i].extend(create_attack_traffic(100))
            traffic_dict[i].extend(create_normal_traffic(100))
        else:
            traffic_dict[i].extend(create_normal_traffic(200))

    for i in range(0, 20):
        print "Sending traffic for ts: " + str(i)
        start = time.time()
        sendp(traffic_dict[i], iface=INTERFACE, verbose=0)
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)

def send_campus_data():
    packets = rdpcap(PCAP_LOCATION)
    DURATION = 60
    T = len(packets)/DURATION

    ctr = 0
    for ts in range(0,60):
        packets_for_ts = []
        start = time.time()
        print "For TS: ", ts, "Range: ", ctr, ":", ctr+T
        packets_for_ts = packets[ctr:ctr+T]
        if ts > 20 and ts < 31:
            # 304 packets on server
            packets_for_ts.extend(create_attack_traffic(304))
        sendp(packets_for_ts, iface = INTERFACE, verbose=0)
        ctr += T
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)

send_campus_data()
# send_created_traffic()