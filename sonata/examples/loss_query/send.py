#!/usr/bin/python
from scapy.all import *

pkt = Ether()/IP()
sendp(pkt, iface="m-veth-2")