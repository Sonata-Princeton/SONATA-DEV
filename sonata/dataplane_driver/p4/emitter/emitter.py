from scapy.all import *
import struct
from multiprocessing.connection import Listener
import time
import logging
from datetime import datetime
from emitter_field import Field, IPField, MacField

QID_SIZE = 16
BYTE_SIZE = 8

class Emitter(object):
    def __init__(self, conf, queries):
        # Interfaces
        print "Emitter Started"
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
        self.qid_field = Field(target_name='qid', sonata_name='qid', size=QID_SIZE/BYTE_SIZE,
                               format='>H', offset=0)

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(conf['log_file'])
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def start(self):
        while True:
            # print "Waiting for socket"
            self.spark_conn = self.listener.accept()

            print "*********************************************************************"
            print "*                           System Ready                            *"
            print "*********************************************************************\n\n"

            # print "Now start sniffing the packets from switch"
            self.sniff_packets()

    def send_data(self, data):
        self.spark_conn.send_bytes(data)

    def sniff_packets(self):
        sniff(iface=self.sniff_interface, prn=lambda x: self.process_packet(x))

    def process_packet(self, raw_packet):
        '''
        callback function executed for each capture packet
        '''

        p_str = str(raw_packet)
        # raw_packet.show()
        # hexdump(raw_packet)
        offset = 0

        # Read first two bits to extract query id (first field for all out headers is qid)
        qid = self.qid_field.extract_field(p_str)

        output_tuple = []

        while True:
            start = "%.20f" %time.time()
            if qid in self.queries and qid != 0:
                query = self.queries[qid]
                out_headers = query['headers']
                output_tuple = list()

                if out_headers is not None:
                    for fld in out_headers.fields:
                        fld_name = fld.sonata_name
                        fld_size = fld.size
                        if 'IP' in fld_name:
                            fld = IPField(fld_name, fld_name, offset)
                        elif 'Mac' in fld_name:
                            fld = MacField(fld_name, fld_name, offset)
                        else:
                            fld = Field(fld_name, fld_name, offset)

                        offset += fld.get_updated_offset()
                        output_tuple.append(fld.extract_field())

                if query['parse_payload']:
                    payload_fields = query['payload_fields']
                    # TODO: get rid of this hardcoding
                    payload_fields = ['dns.ns.type']
                    for fld in payload_fields:
                        fld_str = 'raw_packet.'+fld
                        payload_fld = eval(fld_str)
                        output_tuple.append(payload_fld)

                output_tuple = ['k']+[str(qid)]+output_tuple
                send_tuple = ",".join([str(x) for x in output_tuple])
                self.logger.debug(send_tuple)
                self.send_data(send_tuple + "\n")
                self.logger.info("emitter,"+ str(qid) + ","+str(start)+",%.20f"%time.time())

                self.qid_field.offset = offset
                # Read first two bits for the next out header layer
                qid = self.qid_field.extract_field(p_str)
                if qid in self.queries and qid != 0:
                    # we need to parse another layer for this packet
                    offset += qid.get_updated_offset()
                    continue
                else:
                    # we have extracted all layers for this packet now
                    break

if __name__ == '__main__':
    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': "out-veth-2"}
    Emitter(emitter_conf)
