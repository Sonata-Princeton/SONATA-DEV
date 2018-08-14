#!/usr/bin/env python
# Author: Arpit Gupta (arpitg@cs.princeton.edu)


# TODO Support out_header, METADATA and packet
def get_p4_field(field_name, raw_p4_fields, meta_name=None, other_name=None):
    field_split = field_name.split("__")
    raw_field = field_split[0]

    if len(field_split) > 1:
        modifier = field_split[1]
    else:
        modifier = None

    sonata_field = raw_p4_fields.get_target_field(raw_field)
    p4_field = P4Field(target_name=sonata_field.target_name, sonata_name=sonata_field.sonata_name,
                       size=sonata_field.size, meta_name=meta_name, other_name=other_name,
                       sonata_layer=sonata_field.layer, modifier=modifier)
    return p4_field


class P4Field(object):
    # TODO: If modifier is None, this is qid/count/index. We want to use "__in" on meta, but not field.
    # TODO: IF modifier exists, use it on both meta and field.
    def __init__(self, target_name, sonata_name, size,
                 meta_name=None, other_name=None, sonata_layer=None,
                 modifier=None):
        self.target_name = target_name
        self.sonata_name = sonata_name
        self.size = size
        self.meta_name = meta_name
        self.other_name = other_name
        self.sonata_layer = sonata_layer
        self.modifier = modifier

    def get_sonata_field(self):
        return self.sonata_name

    def get_target_field(self):
        return self.target_name

    def get_field(self):
        field_name = self.target_name.replace(".", "_")
        if self.modifier:
            field_name += "__" + self.modifier
        return field_name

    def get_meta_field(self):
        field = self.get_field()
        meta_name = self.meta_name
        if self.modifier:
            meta_name += "__" + self.modifier
        else:
            meta_name += "__in"
        meta_field = meta_name + "." + field
        return meta_field

    def get_other_field(self):
        field = self.get_field()
        other_field = self.other_name + "." + field
        return other_field

    def is_egress(self):
        return self.modifier == "out"

    def __repr__(self):
        return "P4Field(target=" + self.target_name + ", sonata=" + self.sonata_name + ", size=" + str(self.size) +")"
