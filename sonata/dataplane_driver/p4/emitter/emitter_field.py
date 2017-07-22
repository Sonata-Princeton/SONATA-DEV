#!/usr/bin/env python
# Author: Arpit Gupta (arpitg@cs.princeton.edu)

#from scapy.all import *
import struct


class Field(object):
    def __init__(self, target_name, sonata_name, size, format='>H', offset=0):
        self.target_name = target_name
        self.sonata_name = sonata_name
        self.size = size
        self.format = format
        self.unpack_struct = struct.Struct(format)
        self.offset = offset

    def get_sonata_name(self):
        return self.sonata_name

    def get_target_name(self):
        return self.target_name

    def extract_field(self, packet_as_string):
        return str(self.unpack_struct.unpack(packet_as_string[self.offset:self.offset + self.size])[0])

    def get_updated_offset(self):
        return self.offset + self.size


class IPField(Field):
    byte_size = 8
    size = 32
    format='BB'

    def __init__(self, target_name, sonata_name, offset):
        Field.__init__(self, target_name, sonata_name, self.size, self.format, offset)

    def extract_field(self, packet_as_string):
        ctr = self.size / self.byte_size
        return ".".join([str(x) for x in list(self.unpack_struct.unpack(packet_as_string[self.offset:self.offset + ctr]))])


class MacField(Field):
    byte_size = 8
    size = 48
    format='BB'

    def __init__(self, target_name, sonata_name, offset):
        Field.__init__(self, target_name, sonata_name, self.size, self.format, offset)

    def extract_field(self, packet_as_string):
        ctr = self.size / self.byte_size
        return ".".join([str(x) for x in list(self.unpack_struct.unpack(packet_as_string[self.offset:self.offset + ctr]))])