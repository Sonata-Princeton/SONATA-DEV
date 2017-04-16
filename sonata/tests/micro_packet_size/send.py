from scapy.all import *
import sys


SERVER = True

if SERVER:
    INTERFACE = 'eth0'
    PCAP_LOCATION = '/home/sonata/SONATA-DEV/sonata/tests/micro_packet_size/campus_dns_1min.pcap'
else:
    INTERFACE = 'out-veth-1'
    PCAP_LOCATION = '/home/vagrant/dev/sonata/tests/micro_packet_size/campus_dns_1min.pcap'


class SONATA(Packet):
    name = "SONATA"
    fields_desc = [ ShortField("qid", 23),
                    DestIPField("dIP", None),
                    ShortField("count", None),]

def create_sonata_traffic(number_of_packets):
    normal_packets = []

    for i in range(number_of_packets):
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        s = SONATA(dIP=dIP, count=25)/'ATTACK'
        normal_packets.append(s)

    return normal_packets

def send_campus_data(mode):
    NUMBER_OF_PACKETS_TO_SEND = 100

    if mode == 'dns':
        packets = rdpcap(PCAP_LOCATION)
        sendp(packets[:NUMBER_OF_PACKETS_TO_SEND], iface=INTERFACE, verbose=0)
    else:
        traffic_dict = []
        traffic_dict.extend(create_sonata_traffic(NUMBER_OF_PACKETS_TO_SEND))
        sendp(traffic_dict, iface=INTERFACE, verbose=0)


mode = sys.argv[1]
send_campus_data(mode)