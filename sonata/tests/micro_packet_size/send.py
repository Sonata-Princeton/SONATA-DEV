from scapy.all import *
import os
import sys
import glob
import math, time
import sys


# INTERFACE = 'eth0'
INTERFACE = 'm-veth-2'

class SONATA(Packet):
    name = "SONATA"
    fields_desc = [ ShortField("qid", 23),
                    DestIPField("dIP", None),
                    ShortField("count", None),]

def create_sonata_traffic(number_of_packets):
    normal_packets = []

    for i in range(number_of_packets):
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        s = SONATA(dIP=dIP, count=1)
        normal_packets.append(s)

    return normal_packets

def create_dns_traffic(number_of_packets):
    sIPs = []
    attack_packets = []

    for i in range(number_of_packets):
        sIPs.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))

    for sIP in sIPs:
        p = IP(dst=sIP)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="www.thepacketgeek.com"))
        attack_packets.append(p)

    return attack_packets

def send_created_traffic(mode):
    traffic_dict = {}
    for i in range(0, 20):
        traffic_dict[i] = []

        if mode == 'dns':
            traffic_dict[i].extend(create_dns_traffic(50))
        else:
            traffic_dict[i].extend(create_sonata_traffic(50))

    for i in range(0, 20):
        print "Sending traffic for ts: " + str(i)
        start = time.time()
        sendp(traffic_dict[i], iface=INTERFACE, verbose=0)
        total = time.time()-start
        sleep_time = 1-total
        if sleep_time > 0:
            time.sleep(sleep_time)


mode = sys.argv[1]
send_created_traffic(mode)