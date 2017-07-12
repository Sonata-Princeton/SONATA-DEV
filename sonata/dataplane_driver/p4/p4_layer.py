from p4_field import P4Field


class P4Layer(object):
    def __init__(self, name, fields=[], offset=0, parent_layers={}, child_layers={}):
        self.name = name
        self.offset = offset
        self.fields = fields
        self.parent_layers = parent_layers
        self.child_layers = child_layers

    def get_parent_layers(self):
        return self.parent_layers

    def get_child_layers(self):
        return self.child_layers

    def generate_header_specification(self):
        out = "header_type "+self.name+"_t {\n\t\tfields {\n"
        for fld in self.fields:
            out += "\t\t\t\t"+fld.target_name+" : "+str(fld.size)+";\n"
        out += "\t\t}\n}\n\n"
        return out

    def generate_parser_definition(self):
        return ""


class Ethernet(P4Layer):
    def __init__(self):
        P4Layer.__init__(self, "ethernet")
        self.fields = [P4Field(self, "dstAddr", "dstMac", 48),
                       P4Field(self, "srcAddr", "srcMac", 48),
                       P4Field(self, "etherType", "ethType", 16)]
        field_that_determine_child = self.fields[-1]
        child_layers = {"0x0800": IPV4()}

    def generate_parser_definition(self):
        return ""


class IPV4(P4Layer):
    def __init__(self):
        P4Layer.__init__(self, "ipv4")
        self.fields = [P4Field(self, "version", "version", 4),
                       P4Field(self, "ihl", "ihl", 4),
                       P4Field(self, "diffserv", "diffserv", 8),
                       P4Field(self, "totalLen", "totalLen", 16),
                       P4Field(self, "identification", "identification", 16),
                       P4Field(self, "flags", "flags", 3),
                       P4Field(self, "fragOffset", "fragOffset", 13),
                       P4Field(self, "ttl", "ttl", 8),
                       P4Field(self, "protocol", "proto", 8),
                       P4Field(self, "hdrChecksum", "hdrChecksum", 16),
                       P4Field(self, "srcAddr", "srcIP", 32),
                       P4Field(self, "dstAddr", "dstIP", 32)
                       ]
        self.field_that_determine_child = self.fields[-4]  # protocol determines the next layer to parse
        child_layers = {6: TCP(), 17: UDP()}

    def generate_parser_definition(self):
        return ""


class TCP(P4Layer):
    def __init__(self):
        P4Layer.__init__(self, "tcp")
        self.fields = [P4Field(self, "srcPort", "sport", 16),
                       P4Field(self, "dstPort", "dport", 16),
                       P4Field(self, "seqNo", "seqNo", 32),
                       P4Field(self, "ackNo", "ackNo", 32),
                       P4Field(self, "dataOffset", "dataOffset", 4),
                       P4Field(self, "res", "res", 3),
                       P4Field(self, "ecn", "ecn", 3),
                       P4Field(self, "ctrl", "ctrl", 6),
                       P4Field(self, "window", "window", 16),
                       P4Field(self, "checksum", "checksum", 16),
                       P4Field(self, "urgentPtr", "urgentPtr", 16)
                       ]
        self.field_that_determine_child = None

    def generate_parser_definition(self):
        return ""


class UDP(P4Layer):
    def __init__(self):
        P4Layer.__init__(self, "tcp")
        self.fields = [P4Field(self, "srcPort", "sport", 16),
                       P4Field(self, "dstPort", "dport", 16),
                       P4Field(self, "length_", "len", 16),
                       P4Field(self, "checksum", "checksum", 16)]
        self.field_that_determine_child = None

    def generate_parser_definition(self):
        return ""


def test():
    layers = [Ethernet(), IPV4(), TCP()]
    for layer in layers:
        print layer.generate_header_specification()

if __name__ == '__main__':
    test()