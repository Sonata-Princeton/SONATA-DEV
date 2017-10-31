from scapy.all import *
from multiprocessing.connection import Listener
import time
import logging
from sonata.dataplane_driver.p4.emitter.emitter_field import Field, IPField, MacField, PayloadField
from scapy.config import conf
from sonata.dataplane_driver.p4.p4_layer import OutHeaders
from threading import Thread
from sonata.dataplane_driver.utils import get_out
import re

QID_SIZE = 16
BYTE_SIZE = 8


class Emitter(object):
    tuple_dict = {}

    def __init__(self, sniff_interface):
        # Interfaces
        print "Emitter Started"
        self.sniff_interface = sniff_interface

        # queries has the following format
        # queries = dict with qid as key
        # -> per qid we have again a dict with the following key, values:
        #       - key: parse_payload, value: boolean
        #       - key: headers, values: list of tuples with (field name, field size)

        query1 = {}
        query1['headers'] = OutHeaders("query1")
        query1['headers'].fields = [Field(target_name='tcp.flags', sonata_name='tcp_flags', size=8),
                             IPField(target_name='ipv4.dstIP', sonata_name='ipv4_dstIP')]
        query1['parse_payload'] = None
        query1['payload_fields'] = None
        query1['filter_payload'] = None
        query1['reads_register'] = False
        query1['registers'] = None

        query2 = {}
        query2['headers'] = OutHeaders("query2")

        query2['headers'].fields = [IPField(target_name='ipv4.dstIP', sonata_name='ipv4_dstIP')]
        query2['parse_payload'] = None
        query2['payload_fields'] = None
        query2['filter_payload'] = None
        query2['reads_register'] = False
        query2['registers'] = None

        query3 = {}
        query3['headers'] = OutHeaders("query3")
        query3['headers'].fields = [IPField(target_name='ipv4.dstIP', sonata_name='ipv4_dstIP'),
                                    Field(target_name='index', sonata_name='index', size=16)]
        query3['parse_payload'] = None
        query3['payload_fields'] = None
        query3['filter_payload'] = None
        query3['reads_register'] = True
        query3['registers'] = ['reduce_1']

        query4 = {}
        query4['headers'] = OutHeaders("query4")
        query4['headers'].fields = [IPField(target_name='ipv4.dstIP', sonata_name='ipv4_dstIP'),
                                    Field(target_name='index', sonata_name='index', size=16)]
        query4['parse_payload'] = None
        query4['payload_fields'] = None
        query4['filter_payload'] = None
        query4['reads_register'] = True
        query4['registers'] = ['reduce_1']

        self.queries = {
                        1: query1,
                        2: query2,
                        3: query3,
                        4: query4
                       }
        self.qid_field = Field(target_name='qid', sonata_name='qid', size=QID_SIZE,
                               format='>H', offset=0)

        self.bmv2_cli = '/home/vagrant/bmv2/targets/simple_switch/sswitch_CLI'
        self.thrift_port = 22222

        # print self.queries #, self.emitter_read_timeout

        self.reader_thread = Thread(name='reader_thread', target=self.start_reader)
        self.reader_thread.start()

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler('/home/vagrant/dev/sonata/tutorial/Part-1/' + "receiver.log")
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def start(self):
        while True:
            print "Waiting for socket"
            print "*********************************************************************"
            print "*                           System Ready                            *"
            print "*********************************************************************\n\n"

            print "Now start sniffing the packets from switch"
            self.sniff_packets()

    def start_reader(self):
        while True:
            for qid in self.queries.keys():
                if self.queries[qid]['registers']:
                    for register in self.queries[qid]['registers']:
                        self.process_register_values(qid, register)
                print "woke up", qid
            time.sleep(5)

    # def send_data(self, data):
        # self.spark_conn.send_bytes(data)

    def process_register_values(self, read_qid, register):
        store = {}

        if self.tuple_dict.keys():
            read_register_cmds = ""
            for indexLoc in self.tuple_dict.keys():
                store[indexLoc] = self.tuple_dict[indexLoc]['tuple']
                read_register_cmds +="register_read "+register+" " + str(indexLoc) + "\n"

            success, out = get_out("echo \"" + read_register_cmds + "\" | " + self.bmv2_cli + " --thrift-port " + str(self.thrift_port) + " | grep -o -e \"$1.*[1-9][0-9]*$\"")

            output = {}
            if success:
                write_register_cmds = ""
                for line in out.split('\n'):
                    if line:
                        m = re.search('.*\[(.*)\]\=\s+(.*)', out)
                        output[m.group(1)] = m.group(2)
                        write_register_cmds += "register_write "+register+" " + str(m.group(1)) + " 0\n"

                success3, out3 = get_out("echo \"" + write_register_cmds + "\" | " + self.bmv2_cli + " --thrift-port " + str(self.thrift_port))

            for indexLoc in store.keys():
                if str(indexLoc) in output.keys():
                    out = store[indexLoc] + ","+output[str(indexLoc)]
                    self.logger.info(out)
                    self.tuple_dict.pop(indexLoc, None)

    def store_tuple_to_dict(self, tuple):

        tuples = tuple.split(",")
        index = int(tuples[-1])
        qid = tuples[1]
        newTuple = ",".join(tuples[:-1])

        data_index = {'tuple': newTuple, 'id': qid }

        if index not in self.tuple_dict:
            self.tuple_dict[index] = {}

        self.tuple_dict[index] = data_index

    def sniff_packets(self):
        print "Interface confirming: ", self.sniff_interface
        sniff(iface=str(self.sniff_interface), prn=lambda x: self.process_packet(x))

    def process_packet(self, raw_packet):
        '''
        callback function executed for each capture packet
        '''
        p_str = str(raw_packet)
        # hexdump(raw_packet)
        # if raw_packet.haslayer(Raw):
        #     print str(raw_packet.getlayer(Raw).load)
        offset = 0
        # Read first two bits to extract query id (first field for all out headers is qid)
        self.qid_field.offset = offset
        qid = int(self.qid_field.extract_field(p_str))
        offset = self.qid_field.get_updated_offset()
        ctr = 0
        ctr += self.qid_field.ctr

        while True:
            start = "%.20f" % time.time()
            if int(qid) in [int(x) for x in self.queries.keys()] and int(qid) != 0:
                query = self.queries[qid]
                out_headers = query['headers']
                output_tuple = list()
                if out_headers is not None:
                    for fld in out_headers.fields:
                        fld_name = fld.target_name
                        fld_size = fld.size
                        if 'IP' in fld_name:
                            fld = IPField(fld_name, fld_name, offset)
                        elif 'Mac' in fld_name:
                            fld = MacField(fld_name, fld_name, offset)
                        else:
                            format = ''
                            if fld_size == 8:
                                format = 'B'
                            elif fld_size == 16:
                                format = '>H'
                            fld = Field(fld_name, fld_name, fld_size, format, offset)

                        offset = fld.get_updated_offset()
                        ctr += fld.ctr
                        field_value = fld.extract_field(p_str)
                        output_tuple.append(field_value)

                payload_fields = query['payload_fields']
                if query['parse_payload'] and payload_fields != ['payload']:
                    conf.l3types.register_num2layer(3, Ether)
                    ctr += 4
                    new_raw_packet = conf.l3types[3](p_str[ctr:])

                    for fld in payload_fields:
                        payload_field = PayloadField(fld)
                        extracted_value = payload_field.extract_field(new_raw_packet)
                        output_tuple.append(extracted_value)

                output_tuple = ['k'] + [str(qid)] + output_tuple
                send_tuple = ",".join([str(x) for x in output_tuple])

                if query['filter_payload']:
                    output_payload = '0'
                    if raw_packet.haslayer(Raw):
                        payload = str(raw_packet.getlayer(Raw).load)
                        if query['filter_payload_str'] in payload:
                            output_payload = query['filter_payload_str']

                if query['filter_payload']:
                    send_tuple += "," + output_payload
                if query['reads_register']:
                    self.store_tuple_to_dict(send_tuple)
                else:
                    self.logger.info(send_tuple)

                self.qid_field.offset = offset
                # Read first two bits for the next out header layer
                next_qid = self.qid_field.extract_field(p_str)

                qid = int(next_qid)
                if int(qid) in [int(x) for x in self.queries.keys()] and int(qid) != 0:
                    # we need to parse another layer for this packet
                    offset = self.qid_field.get_updated_offset()
                    ctr += self.qid_field.ctr
                    continue
                else:
                    # we have extracted all layers for this packet now
                    break
            else:
                break


if __name__ == '__main__':
    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': "out-veth-2"}
    emitter = Emitter("out-veth-2")
    emitter.start()
