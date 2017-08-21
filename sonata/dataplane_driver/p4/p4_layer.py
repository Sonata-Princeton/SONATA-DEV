#!/usr/bin/env python
# Author: Arpit Gupta (arpitg@cs.princeton.edu)

# from p4_field import P4Field


def get_p4_layer(layer):
    p4_layer = P4Layer(layer.name, layer.fields, layer.offset, layer.parent_layer,
                       layer.child_layers, layer.field_that_determines_child)

    return p4_layer


class P4Layer(object):
    field_that_determines_child = None

    def __init__(self, name, fields=[], offset=0, parent_layer=None, child_layers=None,
                 field_that_determines_child=None):
        self.name = name
        self.offset = offset
        self.fields = fields
        self.parent_layer = parent_layer
        self.child_layers = child_layers
        self.field_that_determines_child = field_that_determines_child

    def get_name(self):
        return self.name

    def get_parent_layers(self):
        return self.parent_layer

    def get_child_layers(self):
        return self.child_layers

    def get_header_specification_code(self):
        out = "header_type " + self.name + "_t {\n\tfields {\n"
        for fld in self.fields:
            field_name = fld.target_name.split(".")[1]
            out += "\t\t" + field_name + " : " + str(fld.size) + ";\n"
        out += "\t}\n}\n\n"
        out += 'header %s_t %s;\n\n' % (self.name, self.name)
        return out

    def get_parser_code(self, all_layers):
        out = "parser parse_" + self.name + " {\n\textract(" + self.name + ");\n"
        if self.field_that_determines_child is not None:
            fld_to_check = self.fields[int(self.field_that_determines_child)]
            sub_field = fld_to_check.target_name.split(".")[1]
            out += "\treturn select(latest." + sub_field + ") {\n"
            for k, v in self.child_layers.iteritems():
                if v.name in [l.name for l in all_layers]:
                    out += "\t\t" + str(k) + " : parse_" + v.name + ";\n"
            out += "\t\tdefault: ingress;\n\t}\n"
        else:
            out += "\treturn ingress;\n"
        out += "}\n\n"
        return out

    def get_field_prefix(self):
        return self.name
        # if self.parent_layer is None:
        #     # No parent layer, just return the name of the layer as output
        #     return self.name
        # else:
        #     # TODO Handle the case where a layer can have multiple parents
        #     return self.parent_layer.get_field_prefix() + "." + self.name

    def get_all_child_layers(self):
        out = [self]
        if self.child_layers is not None:
            for child in self.child_layers:
                out += self.child_layers[child].get_all_child_layers()
        return out

    def get_all_parent_layers(self):
        out = [self]
        if self.parent_layer is not None:
            out += self.parent_layer.get_all_parent_layers()
        return out


class OutHeaders(P4Layer):
    def __init__(self, name="", fields=[], parent_layer=None, child_layer=None):
        P4Layer.__init__(self, name)
        self.parent_layer = parent_layer
        self.child_layers = {0: child_layer}

    def get_header_specification_code(self):
        out = "header_type " + self.name + "_t {\n\tfields {\n"
        for fld in self.fields:
            out += "\t\t" + fld.target_name.replace(".", "_") + " : " + str(fld.size) + ";\n"
        out += "\t}\n}\n"
        out += 'header %s_t %s;\n\n' % (self.name, self.name)
        return out

    def get_parser_code(self):
        return "extract("+self.name+");"

    def __repr__(self):
        return "OutHeaders(layer=" +self.name+ ", fields=" + str(self.fields) + ")"


class P4RawFields(object):
    all_fields = None
    all_sonata_fields = None

    def __init__(self, root_layer):
        self.root_layer = root_layer
        self.layers = self.root_layer.get_all_child_layers()
        self.get_all_fields()
        self.get_all_sonata_fields()

    def get_all_fields(self):
        fields = dict()
        for layer in self.layers:
            prefix = layer.get_field_prefix()
            for fld in layer.fields:
                fields[prefix + "." + str(fld.target_name)] = fld
        self.all_fields = fields

    def get_all_sonata_fields(self):
        fields = dict()
        for layer in self.layers:
            for fld in layer.fields:
                fields[fld.sonata_name] = fld
        self.all_sonata_fields = fields

    def get_layers_for_fields(self, query_specific_fields):
        layers = []
        for field_name in query_specific_fields:
            fld = self.all_sonata_fields[field_name]
            curr_layer = fld.layer
            if curr_layer.parent_layer is None:
                layers += [curr_layer]
            else:
                layers += [curr_layer] + curr_layer.get_all_parent_layers()

        return list(set(layers))

    def get_target_field(self, sonata_field_name):
        return self.all_sonata_fields[sonata_field_name]


def test():
    p4_fields = P4RawFields(Ethernet())
    # query_specific_fields = ['ethernet.dstMac', 'udp.sport']
    # layers = p4_fields.get_layers_for_fields(query_specific_fields)
    # assert "udp" in [layer.name for layer in layers]
    # assert "tcp" not in [layer.name for layer in layers]


if __name__ == '__main__':
    test()
