#!/usr/bin/env python
# Author: Arpit Gupta (arpitg@cs.princeton.edu)

from scapy.all import *
import struct

"""
dns.ns.type
dns, ns, type
if has_layer(dns)
    if has_layer(ns)
        return ns.type
"""

scapy_fields_supported = {
                            'dns.ns.type': "DNS.ns.type",
                            'dns.ancount': 'DNS.ancount',
                            'dns.an.rrname': 'DNS.an.rrname',
                            'dns.an.ttl': 'DNS.an.ttl',
                            'dns.an.rdata': 'DNS.an.rdata'
                        }


class PayloadField(object):
    def __init__(self, sonata_name):
        self.target_name = scapy_fields_supported[sonata_name]
        self.sonata_name = sonata_name

    def get_sonata_name(self):
        return self.sonata_name

    def get_target_name(self):
        return self.target_name

    def extract_field(self, raw_packet):
        layer = self.target_name.split('.')[0]
        layer_str = "raw_packet.haslayer(" + layer + ")"
        extracted_value = ''
        has_field = True
        if eval(layer_str):
            cum_str = 'raw_packet'
            for intermediate_field in self.target_name.split('.')[1:-1]:
                cum_str += '.' + intermediate_field
                if not eval(cum_str):
                    has_field = False
                    break
            if has_field:
                extracted_value = str(eval(cum_str + "." + self.target_name.split('.')[-1]))

        return extracted_value


class Field(object):
    byte_size = 8

    def __init__(self, target_name, sonata_name, size, format='>H', offset=0):
        self.target_name = target_name
        self.sonata_name = sonata_name
        self.size = size
        self.format = format
        self.unpack_struct = struct.Struct(format)
        self.offset = offset
        self.ctr = self.size / self.byte_size

    def get_sonata_name(self):
        return self.sonata_name

    def get_target_name(self):
        return self.target_name

    def extract_field(self, packet_as_string):
        # print self.sonata_name, self.target_name
        # print self.offset, self.offset, self.ctr
        return str(self.unpack_struct.unpack(packet_as_string[self.offset:self.offset + self.ctr])[0])

    def get_updated_offset(self):
        return self.offset + self.ctr


class IPField(Field):
    byte_size = 8
    size = 32
    format = 'BBBB'

    def __init__(self, target_name, sonata_name, offset=0):
        Field.__init__(self, target_name, sonata_name, self.size, self.format, offset)
        self.ctr = self.size / self.byte_size

    def extract_field(self, packet_as_string):
        return ".".join(
            [str(x) for x in list(self.unpack_struct.unpack(packet_as_string[self.offset:self.offset + self.ctr]))])


class MacField(Field):
    byte_size = 8
    size = 48
    format = 'BBBBBB'

    def __init__(self, target_name, sonata_name, offset):
        Field.__init__(self, target_name, sonata_name, self.size, self.format, offset)
        self.ctr = self.size / self.byte_size

    def extract_field(self, packet_as_string):
        return ".".join(
            [str(x) for x in list(self.unpack_struct.unpack(packet_as_string[self.offset:self.offset + self.ctr]))])
