#!/usr/bin/python3
from scapy.all import *
import sys

s1 = conf.L2socket(iface="m-veth-1")
s2 = conf.L2socket(iface="m-veth-2")

def int2ip(num):
    return '.'.join( [ str((num >> 8*i) % 256)  for i in [3,2,1,0] ])

def start():
    pkt = Ether() / IP(version=0)
    pkt.show()
    input("Press Enter...")
    s1.send(pkt)

def end():
    pkt = Ether() / IP(version=1)
    pkt.show()
    s2.send(pkt)


def send(pkts, count=1):
    input("Sending %s packets %s times each. Press Enter..." % (len(pkts), count))
    for pkt in pkts:
        for j in range(count):
            s1.send(pkt)

if sys.argv[1] == "end":
    end()
    sys.exit(0)

num_packets = int(sys.argv[1])

start()

packets = []
for i in range(1, 2**6):
    pkt_IP = int2ip(i)
    packets.append(Ether() / IP(src=pkt_IP))

send(packets, count=num_packets)