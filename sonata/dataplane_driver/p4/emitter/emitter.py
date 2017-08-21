from scapy.all import *
import struct
from multiprocessing.connection import Listener
import time
import logging
from datetime import datetime
from emitter_field import Field, IPField, MacField, PayloadField
from scapy.config import conf
import mysql.connector
from threading import Thread
from sonata.dataplane_driver.utils import get_out
import re

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
        self.qid_field = Field(target_name='qid', sonata_name='qid', size=QID_SIZE,
                               format='>H', offset=0)

        config = {
            'user': 'root',
            'password': 'root',
            'host': '127.0.0.1',
            'database': 'sonata',
            'raise_on_warnings': True,
            'use_pure': False,
        }

        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

        self.reader_thread = Thread(name='reader_thread', target=self.start_reader)
        self.reader_thread.start()
        print self.queries
        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(conf['log_path'] + "emitter.log")
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def start(self):
        while True:
            # print "Waiting for socket"
            self.spark_conn = self.listener.accept()

            print "*********************************************************************"
            print "*                           System Ready                            *"
            print "*********************************************************************\n\n"

            print "Now start sniffing the packets from switch"
            self.sniff_packets()

    def start_reader(self):
        while True:
            cursor = self.cnx.cursor()
            query = "SELECT id, qid, tuple, indexLoc FROM indexStore"
            cursor.execute(query)
            store = {}
            with open("CLI_commands.txt", 'w') as f:
                for (id, qid, tuple, indexLoc) in cursor:
                    # print "From Database: ", id, qid, tuple,indexLoc
                    store[indexLoc] = tuple
                    f.write("register_read reduce_10032_6 " + str(indexLoc) + "\n")
                f.flush()
                f.close()
            cursor.close()
            success, out = get_out("~/bmv2/tools/runtime_CLI.py --thrift-port 22222 < /home/vagrant/dev/CLI_commands.txt | grep -o -e \"$1.*[1-9][0-9]*$\"")

            output = {}
            if success:
                for line in out.split('\n'):
                    if line:
                        m = re.search('.*\[(.*)\]\=  (.*)', line)
                        output[m.group(1)] = m.group(2)

            print output

            for indexLoc in store.keys():
                if str(indexLoc) in output.keys():
                    out = store[indexLoc] + ","+output[str(indexLoc)] + "\n"
                    # print out
                    self.send_data(out)
            time.sleep(10)
        return 0

    def send_data(self, data):
        self.spark_conn.send_bytes(data)

    def store_tuple_to_db(self, tuple):

        tuples = tuple.split(",")
        index = tuples[-1]
        qid = tuples[1]

        add_index = ("INSERT INTO indexStore "
                     "(qid, tuple, indexLoc) "
                     "VALUES (%s, %s, %s)")
        newTuple = ",".join(tuples[:-1])
        data_index = (int(qid), newTuple, int(index))
        # INSERT INTO DB
        self.cursor.execute(add_index, data_index)
        self.cnx.commit()
        # print "store_tuple_to_db"

    def sniff_packets(self):
        print "Interface confirming: ", self.sniff_interface
        sniff(iface=str(self.sniff_interface), prn=lambda x: self.process_packet(x))

    def process_packet(self, raw_packet):
        '''
        callback function executed for each capture packet
        '''
        p_str = str(raw_packet)
        offset = 0
        # Read first two bits to extract query id (first field for all out headers is qid)
        self.qid_field.offset = offset
        qid = int(self.qid_field.extract_field(p_str))
        offset = self.qid_field.get_updated_offset()
        ctr = 0
        ctr += self.qid_field.ctr
        output_tuple = []

        while True:
            start = "%.20f" % time.time()
            if int(qid) in [int(x) for x in self.queries.keys()] and int(qid) != 0:
                query = self.queries[qid]
                out_headers = query['headers']
                output_tuple = list()

                if out_headers is not None:
                    for fld in out_headers.fields[1:]:
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

                conf.l3types.register_num2layer(3, Ether)
                ctr += 4
                new_raw_packet = conf.l3types[3](p_str[ctr:])

                if query['parse_payload']:
                    payload_fields = query['payload_fields']
                    for fld in payload_fields:
                        payload_field = PayloadField(fld)
                        extracted_value = payload_field.extract_field(new_raw_packet)
                        output_tuple.append(extracted_value)

                output_tuple = ['k'] + [str(qid)] + output_tuple
                send_tuple = ",".join([str(x) for x in output_tuple])
                self.logger.debug(send_tuple)

                if query['reads_register']:
                    # print send_tuple
                    self.store_tuple_to_db(send_tuple)
                else:
                    self.send_data(send_tuple + "\n")
                self.logger.info("emitter," + str(qid) + "," + str(start) + ",%.20f" % time.time())

                self.qid_field.offset = offset
                # Read first two bits for the next out header layer
                qid = self.qid_field.extract_field(p_str)
                ctr += self.qid_field.ctr
                if qid in self.queries.keys() and qid != 0:
                    # we need to parse another layer for this packet
                    offset = self.qid_field.get_updated_offset()
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
    Emitter(emitter_conf)
