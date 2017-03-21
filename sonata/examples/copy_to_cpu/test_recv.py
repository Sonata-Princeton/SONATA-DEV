from scapy.all import *


def process_packet(raw_packet):
    '''
    callback function executed for each capture packet
    '''
    p_str = str(raw_packet)
    hexdump(raw_packet)
    print p_str


sniff(iface = "out-veth-3", prn = lambda x: process_packet(x))
