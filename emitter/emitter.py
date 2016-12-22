from scapy.all import *
import struct
from multiprocessing.connection import Listener

class Emitter(object):

    ip_format = 'BBBB'
    count_format = 'B'

    def __init__(self, conf):
        self.spark_stream_address = conf['spark_stream_address']
        self.spark_stream_port = conf['spark_stream_port']
        self.sniff_interface = conf['sniff_interface']
        self.ip_struct = struct.Struct(self.ip_format)
        self.count_struct = struct.Struct(self.count_format)
        self.listener = Listener((self.spark_stream_address, self.spark_stream_port))



    def start(self):
        while True:
            print "Waiting for socket"
            self.spark_conn = self.listener.accept()
            print "Now start sniffing the packets from switch"
            self.sniff_packets()

    def send_data(self, data):
        print "send_data:", data
        self.spark_conn.send_bytes(data)
        print "done sending data..."

    def sniff_packets(self):
        sniff(iface = self.sniff_interface, prn = lambda x: self.process_packet(x))

    def process_packet(self, raw_packet):
        '''
        callback function executed for each capture packet
        '''
        p_str = str(raw_packet)
        hexdump(raw_packet)
        send_tuple = ""
        qid = str(self.count_struct.unpack(p_str[0])[0])
        print qid
        if qid == '1':
            sIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[1:5]))])
            dIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[5:9]))])
            qid = (qid)
            output_tuple = tuple([qid, tuple([dIP, sIP])])
            send_tuple = str(output_tuple)
            send_tuple = ",".join(['k',qid, dIP, sIP])
            print "Tuple:", send_tuple
            self.send_data(send_tuple + "\n")
            print "returned from sending to Spark"
        elif qid == '2':
            # TODO: Generalize the logic for parsing packet's metadata
            sIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[1:5]))])
            dIP = ".".join([str(x) for x in list(self.ip_struct.unpack(p_str[5:9]))])
            qid = (qid)
            output_tuple = tuple([qid, tuple([dIP, sIP])])
            #send_tuple = str(output_tuple)
            send_tuple = ",".join(['k', qid, dIP, sIP])
            print "Tuple:", send_tuple
            self.send_data(send_tuple + "\n")
            print "returned from sending to Spark"



if __name__ == '__main__':
    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': "out-veth-2"}
    Emitter(emitter_conf)
