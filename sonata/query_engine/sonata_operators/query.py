#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)


class Query(object):
    """
    Abstract Query Class
    """
    basic_headers = ['ipv4.hdrChecksum', 'tcp.dport', 'ethernet.dstMac', 'udp.len',
                     'ethernet.srcMac', 'udp.sport', 'udp.dport', 'tcp.res', 'ipv4.ihl', 'ipv4.diffserv',
                     'ipv4.totalLen', 'ipv4.dstIP', 'ipv4.flags', 'ipv4.protocol', 'udp.checksum', 'tcp.seqNo',
                     'ipv4.ttl', 'tcp.ackNo', 'ipv4.srcIP', 'ipv4.version', 'ipv4.identification',
                     'tcp.window', 'tcp.checksum', 'tcp.dataOffset', 'ipv4.fragOffset', 'tcp.sport',
                     'tcp.urgentPtr', 'ethernet.ethType']

    # payload_headers = ['dns.ns.type', 'dns.ancount','dns.an.rrname', 'dns.an.ttl','dns.an.rdata']
    refinement_headers = ["ipv4.dstIP", "ipv4.srcIP"]

    def __init__(self, *args, **kwargs):
        self.fields = []
        self.keys = []
        self.values = []
        self.expr = ''
        self.name = ''

    def get_init_keys(self):
        return self.keys

    def eval(self):
        """
        evaluate this policy
        :param ?
        :type pkt: ?
        :rtype: ?
        """
        return self.expr