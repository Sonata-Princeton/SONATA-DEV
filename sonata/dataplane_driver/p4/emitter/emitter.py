from scapy.all import *
import struct
from multiprocessing.connection import Listener
import time
import logging

HEADER_FORMAT = {'sIP': 'BBBB', 'dIP': 'BBBB', 'sPort': '>H', 'dPort': '>H',
                 'nBytes': '>H', 'proto': '>H', 'sMac': 'BBBBBB', 'dMac': 'BBBBBB',
                 'qid': '>H', 'count': '>H'}

HEADER_SIZE = {'sIP': 32, 'dIP': 32, 'sPort': 16, 'dPort': 16,
               'nBytes': 16, 'proto': 16, 'sMac': 48, 'dMac': 48,
               'qid': 16, 'count': 16}


class Emitter(object):
    def __init__(self, conf, queries):
        # Interfaces
        print "********* EMITTER INITIALIZED *********"
        self.spark_stream_address = conf['spark_stream_address']
        self.spark_stream_port = conf['spark_stream_port']
        self.sniff_interface = conf['sniff_interface']

        self.listener = Listener((self.spark_stream_address, self.spark_stream_port))
        self.spark_conn = None

        # queries has the following format
        # queries = dict with qid as key
        # -> per qid we have again a dict with the following key, values:
        #       - key: parse_payload, value: boolean
        #       - key: headers, values: list of tuples with (field name, field size)
        self.queries = queries
        self.qid_struct = struct.Struct('>H')

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(conf['log_file'])
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def start(self):
        while True:
            print "Waiting for socket"
            self.spark_conn = self.listener.accept()
            print "Now start sniffing the packets from switch"
            self.sniff_packets()

    def send_data(self, data):
        self.spark_conn.send_bytes(data)

    def sniff_packets(self):
        sniff(iface=self.sniff_interface, prn=lambda x: self.process_packet(x))

    def process_packet(self, raw_packet):
        '''
        callback function executed for each capture packet
        '''

        start = time.time()
        p_str = str(raw_packet)
        # raw_packet.show()
        # hexdump(raw_packet)

        qid = int(str(self.qid_struct.unpack(p_str[0:2])[0]))
        ind = 2
        # print str(self.queries)
        while qid in self.queries and qid != 0:
            query = self.queries[qid]
            out_headers = query['headers']

            output_tuple = []
            count = 0
            # if str(qid) == '30032': print "Headers ", out_headers
            for fld, size in out_headers[1:]:
                hdr_format = HEADER_FORMAT[fld]
                strct = struct.Struct(hdr_format)
                ctr = HEADER_SIZE[fld]/8

                if 'IP' in fld:
                    output_tuple.append(".".join([str(x) for x in list(strct.unpack(p_str[ind:ind+ctr]))]))
                elif 'Mac' in fld:
                    output_tuple.append(":".join([str(x) for x in list(strct.unpack(p_str[ind:ind+ctr]))]))
                else:
                    count = strct.unpack(p_str[ind:ind+ctr])[0]
                    output_tuple.append(strct.unpack(p_str[ind:ind+ctr])[0])
                ind += ctr

            if query['parse_payload']:
                payload = ''
                if raw_packet.haslayer(Raw):
                    temp = str(raw_packet.getlayer(Raw).load)
                    payload = temp.replace('\n', '').replace('\r', '')
                    payload = "ATTACK"
                output_tuple.append(payload)

            output_tuple = ['k']+[str(qid)]+output_tuple
            send_tuple = ",".join([str(x) for x in output_tuple])

            # TODO removed this packet is unrelated stuff - maybe it is necessary
            self.send_data(send_tuple + "\n")

            self.logger.info("emitter,"+ str(qid) + ","+str(start)+","+str(time.time()))

            qid = int(str(self.qid_struct.unpack(p_str[ind:ind+2])[0]))
            ind += 2


if __name__ == '__main__':
    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': "out-veth-2"}
    Emitter(emitter_conf)
