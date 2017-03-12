from scapy.all import *
from struct import *
import time
from multiprocessing.connection import Listener


class spark_source(object):

    ip_format = 'BBBB'
    count_format = 'BB'
    qid_format = '>H'

    def __init__(self, spark_stream_address, spark_stream_port, sniff_interface):
        self.spark_stream_address = spark_stream_address
        self.spark_stream_port = spark_stream_port
        self.sniff_interface = sniff_interface
        self.ip_struct = struct.Struct(self.ip_format)
        self.qid_struct = struct.Struct(self.qid_format)
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
        qid = str(self.qid_struct.unpack(p_str[0:2])[0])
        #new = "".join(reversed(tmp))
        #print new
        #qid = [x for x in struct.unpack('h',new)]
        print qid
        if qid == '10001':
            # TODO: Generalize the logic for parsing packet's metadata
            sIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[2:6]))])
            dIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[6:10]))])
            output_tuple = (sIP, dIP)
            send_tuple = ",".join([qid, dIP, sIP])+"\n"
        else:
            # TODO: Generalize the logic for parsing packet's metadata
            dIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[2:6]))])
            #dIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[4:8]))])
            count = str(self.count_struct.unpack(p_str[6:8])[0])
            output_tuple = (dIP, count)
            send_tuple = ",".join([qid, dIP, count])+"\n"
        print "Tuple: ", send_tuple
        #self.send_data(send_tuple)

spark_stream_address = 'localhost'
spark_stream_port = 8989
sniff_interface = "out-veth-2"
spark_source(spark_stream_address, spark_stream_port, sniff_interface)
