#!/usr/bin/python
from scapy.all import *

def process(pkt):
    pkt.show()

sniff(iface="out-veth-2", prn=process)