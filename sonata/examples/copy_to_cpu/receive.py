from scapy.all import *
from struct import *
import time
from multiprocessing.connection import Listener


class spark_source(object):

    ip_format = 'BBBB'
    count_format = 'B'

    def __init__(self, spark_stream_address, spark_stream_port, sniff_interface):
        self.spark_stream_address = spark_stream_address
        self.spark_stream_port = spark_stream_port
        self.sniff_interface = sniff_interface
        self.ip_struct = struct.Struct(self.ip_format)
        self.count_struct = struct.Struct(self.count_format)
        self.listener = Listener((self.spark_stream_address, self.spark_stream_port), backlog=10)
        #while True:
        print "Waiting for socket"
        #self.spark_conn = self.listener.accept()
        print "Now start sniffing the packets from switch"
        self.sniff_packets()

    def send_data(self, data):
        self.spark_conn.send_bytes(data)

    def sniff_packets(self):
        sniff(iface = self.sniff_interface, prn = lambda x: self.process_packet(x))

    def process_packet(self, raw_packet):
        '''
        callback function executed for each capture packet
        '''
        p_str = str(raw_packet)
        hexdump(raw_packet)
        print p_str
        """
        n_packet = Ether(raw_packet[2:])
        src_ip = ''
        dst_ip = ''
        if (IP in n_packet):
            src_ip = str(packet[IP].src)
            dst_ip = str(packet[IP].dst)
        # TODO: Generalize the logic for parsing packet's metadata
        #sIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[:4]))])
        #dIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[4:8]))])
        #count = str(self.count_struct.unpack(p_str[8])[0])
        output_tuple = (src_ip, dst_ip)
        send_tuple = ",".join([dst_ip, src_ip])+"\n"
        print "Tuple: ", send_tuple
        #self.send_data(send_tuple)
        """

spark_stream_address = 'localhost'
spark_stream_port = 8989
sniff_interface = "out-veth-2"
spark_source(spark_stream_address, spark_stream_port, sniff_interface)
