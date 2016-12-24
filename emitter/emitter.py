from scapy.all import *
import struct
from multiprocessing.connection import Listener


header_format = {"sIP":'BBBB', "dIP":'BBBB',
              "sPort": 'H', "dPort": 'H',
              "nBytes": 'H', "proto": 'H',
              "sMac": 'BBBBBB', "dMac":'BBBBBB',
              "qid":'B', "count": 'B'}

header_size = {"sIP":32, "dIP":32, "sPort": 16, "dPort": 16,
               "nBytes": 16, "proto": 8, "sMac": 48, "dMac":48,
               "qid":8, "count": 8}

class Emitter(object):

    def __init__(self, conf, queries):
        self.spark_stream_address = conf['spark_stream_address']
        self.spark_stream_port = conf['spark_stream_port']
        self.sniff_interface = conf['sniff_interface']
        self.queries = queries
        self.listener = Listener((self.spark_stream_address, self.spark_stream_port))
        self.qid_2_query = {}
        self.count_struct = struct.Struct('B')
        for query in self.queries:
            self.qid_2_query[query.qid] = query

    def start(self):
        while True:
            print "Waiting for socket"
            self.spark_conn = self.listener.accept()
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
        #hexdump(raw_packet)
        qid = str(self.count_struct.unpack(p_str[0])[0])
        if qid in self.qid_2_query:
            query = self.qid_2_query[qid]
            out_headers = query.operators[-1].out_headers
            output_tuple = []
            ind = 1
            for fld in out_headers:
                strct = struct.Struct(header_format[fld])
                ctr = header_size[fld]/8
                if 'IP' in fld:
                    output_tuple.append(".".join([str(x) for x in list(strct.unpack(p_str[ind:ind+ctr]))]))
                elif 'Mac' in fld:
                    output_tuple.append(":".join([str(x) for x in list(strct.unpack(p_str[ind:ind+ctr]))]))
                else:
                    output_tuple.append(strct.unpack(p_str[ind:ind+ctr]))
                ind += ctr
                output_tuple.append()
            output_tuple = ['k']+output_tuple
            send_tuple = ",".join(output_tuple)
            print "Tuple:", send_tuple
            self.send_data(send_tuple + "\n")


if __name__ == '__main__':
    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': "out-veth-2"}
    Emitter(emitter_conf)
