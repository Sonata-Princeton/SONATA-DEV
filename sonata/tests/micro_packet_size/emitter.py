from scapy.all import *
import struct
import time, sys
import logging


HEADER_FORMAT = {'sIP': 'BBBB', 'dIP': 'BBBB', 'sPort': '>H', 'dPort': '>H',
                 'nBytes': '>H', 'proto': '>H', 'sMac': 'BBBBBB', 'dMac': 'BBBBBB',
                 'qid': '>H', 'count': '>H'}

HEADER_SIZE = {'sIP': 32, 'dIP': 32, 'sPort': 16, 'dPort': 16,
               'nBytes': 16, 'proto': 16, 'sMac': 48, 'dMac': 48,
               'qid': 16, 'count': 16}

SERVER = False
if SERVER:
    SNIFF_INTERFACE = "ens4f0"
    LOG_PATH = "/home/sonata/SONATA-DEV/sonata/tests/micro_packet_size/emitter.log"
else:
    SNIFF_INTERFACE = "m-veth-1"
    LOG_PATH = "/home/vagrant/dev/sonata/tests/micro_packet_size/emitter.log"


class Emitter(object):
    def __init__(self, interface, log_file, mode):
        # Interfaces
        print "********* EMITTER INITIALIZED *********"
        self.sniff_interface = interface
        self.mode = mode
        self.qid_struct = struct.Struct('>H')

        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(log_file)
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)

    def start(self):
        while True:
            print "Now start sniffing the packets from switch"
            self.sniff_packets()

    def sniff_packets(self):
        if self.mode == 'dns':
            sniff(iface=self.sniff_interface, prn=lambda x: self.process_dns(x))
        else:
            sniff(iface=self.sniff_interface, prn=lambda x: self.process_sonata(x))


    def process_dns(self, raw_packet):
        # print "FUNC"
        start = "%.20f" %time.time()
        if raw_packet.haslayer(DNS) and raw_packet.getlayer(DNS).qr == 0:
            qname = raw_packet.getlayer(DNS).qd.qname
            qdcount = raw_packet.getlayer(DNS).qdcount
            # print "DNS: ", "(", qname, qdcount, ")"
            self.logger.info("emitter, dns,"+str(start)+",%.20f"%time.time())

    def process_sonata(self, raw_packet):

        start = "%.20f" %time.time()
        p_str = str(raw_packet)
        # print raw_packet.summary()
        # hexdump(raw_packet)

        qid = int(str(self.qid_struct.unpack(p_str[0:2])[0]))
        ind = 2

        out_headers = [('qid', 16), ('dIP', 32), ('count', 16)]
        parse_payload = True

        output_tuple = []
        count = 0
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

        if parse_payload:
            payload = ''
            for b in str(p_str[ind:]):
                payload += b
            output_tuple.append(payload)

        output_tuple = ['k']+[str(qid)]+output_tuple
        # print output_tuple
        self.logger.info("emitter,sonata,"+str(start)+",%.20f"%time.time())


if __name__ == '__main__':
    MODE = sys.argv[1]
    em = Emitter(SNIFF_INTERFACE, LOG_PATH, MODE)
    em.start()