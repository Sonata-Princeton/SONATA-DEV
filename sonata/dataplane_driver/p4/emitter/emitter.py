from scapy.all import *
from multiprocessing.connection import Listener
import time
import logging
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
        self.db_conf = conf['db']
        # queries has the following format
        # queries = dict with qid as key
        # -> per qid we have again a dict with the following key, values:
        #       - key: parse_payload, value: boolean
        #       - key: headers, values: list of tuples with (field name, field size)

        self.queries = queries
        self.qid_field = Field(target_name='qid', sonata_name='qid', size=QID_SIZE,
                               format='>H', offset=0)

        self.cnx = mysql.connector.connect(**self.db_conf)

        self.read_file = conf['read_file']
        self.write_file = conf['write_file']

        self.bmv2_cli = conf['BMV2_CLI']
        self.thrift_port = conf['thrift_port']
        self.emitter_read_timeout = conf['read_timeout']

        print self.queries, self.emitter_read_timeout

        self.reader_thread = Thread(name='reader_thread', target=self.start_reader)
        self.reader_thread.start()

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(conf['log_path'] + "emitter.log")
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def start(self):
        while True:
            print "Waiting for socket"
            self.spark_conn = self.listener.accept()

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
                        self.process_register_values(register)
                print "woke up", qid
            time.sleep(self.emitter_read_timeout)

    def send_data(self, data):
        self.spark_conn.send_bytes(data)

    def process_register_values(self, register):
        cnx = mysql.connector.connect(**self.db_conf)
        cursor = cnx.cursor(buffered=True)
        query = "SELECT id, qid, tuple, indexLoc FROM indexStore"
        cursor.execute(query)
        store = {}
        with open(self.read_file, 'w') as f:
            for (id, qid, tuple, indexLoc) in cursor:
                store[indexLoc] = {'tuple': tuple, 'id': id }
                f.write("register_read "+register+" " + str(indexLoc) + "\n")
            f.flush()
            f.close()
        cursor.close()
        cnx.close()
        success, out = get_out(self.bmv2_cli + " --thrift-port " + str(self.thrift_port) + " < " + self.read_file + " | grep -o -e \"$1.*[1-9][0-9]*$\"")
        # print store
        # print success, out
        output = {}
        if success:
            with open(self.write_file, 'w') as f:
                for line in out.split('\n'):
                    if line:
                        m = re.search('.*\[(.*)\]\=\s+(.*)', line)
                        output[m.group(1)] = m.group(2)
                        f.write("register_write "+register+" " + str(m.group(1)) + " 0\n")
                f.flush()
                f.close()

            success3, out3 = get_out(self.bmv2_cli + " --thrift-port " + str(self.thrift_port) + " < " + self.write_file)
            print "Write Register: " + str(success3) + " "
        ids = []

        for indexLoc in store.keys():
            if str(indexLoc) in output.keys():
                out = store[indexLoc]['tuple'] + ","+output[str(indexLoc)] + "\n"
                print out
                self.send_data(out)

                ids.append(store[indexLoc]['id'])

        if ids:
            ids_str = ",".join([str(id) for id in ids])
            delete_indexes = ("DELETE FROM indexStore WHERE id in ("+ids_str+")")
            cnx = mysql.connector.connect(**self.db_conf)
            cursor = cnx.cursor(buffered=True)
            cursor.execute(delete_indexes)
            cnx.commit()
            cursor.close()
            cnx.close()

        # print ids

    def store_tuple_to_db(self, tuple):

        tuples = tuple.split(",")
        index = tuples[-1]
        qid = tuples[1]

        cnx = mysql.connector.connect(**self.db_conf)
        cursor = cnx.cursor(buffered=True)
        add_index = ("INSERT INTO indexStore "
                     "(qid, tuple, indexLoc) "
                     "VALUES (%s, %s, %s)")
        newTuple = ",".join(tuples[:-1])
        data_index = (int(qid), newTuple, int(index))
        # INSERT INTO DB
        cursor.execute(add_index, data_index)
        cnx.commit()
        cursor.close()
        cnx.close()
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
                    print send_tuple
                    self.store_tuple_to_db(send_tuple)
                else:
                    if qid == 10032: print send_tuple
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
