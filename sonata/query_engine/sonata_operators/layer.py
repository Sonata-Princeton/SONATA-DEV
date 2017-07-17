from fields import Field


class Proto(object):
    __slot__ = ["name", "fields"]

    def __int__(self, name, fields):
        self.name = name
        self.fields = fields

    # TODO this will be overwritten by target specific parsers
    def get_field(self, x):
        return x


class Ether(Proto):
    name = "Ether"
    fields = {"src": Field("src"), "dst": Field("dst"), "type": Field("type")}


class IP(Proto):
    name = "IP"
    fields = {"src": Field("src"), "dst": Field("dst"), "ttl": Field("ttl")}


class TCP(Proto):
    name = "TCP"
    fields = {"sport": Field("sport"), "dport": Field("dport"), "seq": Field("seq"), "ack": Field("ack"),
              "window": Field("window")}


class DNS(Proto):
    name = "DNS"
    fields = {"rr": DNSRR(), "qr": DNSQR()}


class DNSQR(Proto):
    name = "DNS Question Record"
    fields = {"qname": Field("qname"), "qtype": Field("qtype"), "qclass": Field("qclass")}


class DNSRR(Proto):
    name = "DNS Resource Record"
    fields = {"rrname": Field("rrname"), "type": Field("type"), "ttl": Field("ttl"), "rclass": Field("rclass")}
