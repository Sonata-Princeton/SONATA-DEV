from sonata_fields import SonataField


class SonataLayer(object):
    field_that_determines_child = None
    target_name = None
    child_layers = {}
    fields = []

    def __init__(self, name, conf, fields=[], offset=0, parent_layer=None, child_layers=None,
                 field_that_determines_child=None, is_payload=False, layer_2_target=None):

        self.name = name
        self.conf = conf
        self.offset = offset
        self.parent_layer = parent_layer
        self.is_payload = is_payload
        self.layer_2_target = layer_2_target
        child_layers_tmp = {}
        fields_tmp = []

        if fields:
            for field in fields:
                fields_tmp.append(SonataField(layer=self,
                                               sonata_name=field["sonata_name"],
                                               target_name=field["target_name"],
                                               size=field["size"]
                                               )
                                   )
        self.fields = fields_tmp
        if child_layers:
            for key, layer_name in child_layers.items():
                child_layers_tmp[key] = SonataLayer(layer_name,
                                                    conf,
                                                    fields=conf[layer_name][layer_2_target[layer_name]]["fields"],
                                                    offset=key,
                                                    parent_layer=self,
                                                    child_layers=conf[layer_name][layer_2_target[layer_name]]["child_layers"],
                                                    field_that_determines_child=None,
                                                    is_payload=conf[layer_name][layer_2_target[layer_name]]["in_payload"],
                                                    layer_2_target=self.layer_2_target)

        self.child_layers = child_layers_tmp

        self.field_that_determines_child = field_that_determines_child

    def __repr__(self):
        return """SonataLayer(name=""" + self.name + """,
        fields=""" + str([field for field in self.fields]) + """
        child_layers=""" + str([str(layer) for key, layer in self.child_layers.items()]) + """ \n"""

    def get_name(self):
        return self.name

    def get_field_prefix(self):
        return self.name

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


class SonataRawFields(object):
    all_fields = None
    all_sonata_fields = None
    all_payload_fields = None

    def __init__(self, root_layer):
        self.root_layer = root_layer
        self.layers = self.root_layer.get_all_child_layers()
        self.get_all_fields()
        self.get_all_sonata_fields()
        self.get_payload_fields()

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
                fields[fld.target_name] = fld
        self.all_sonata_fields = fields

    def get_payload_fields(self):
        fields = dict()
        for layer in self.layers:
            if layer.is_payload:
                for fld in layer.fields:
                    fields[fld.sonata_name] = fld
            # print fields
        self.all_payload_fields = fields

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
    TARGET_NAME = "bmv2"
    INITIAL_LAYER = "Ethernet"

    import json

    with open('/home/vagrant/dev/sonata/fields_mapping.json') as json_data_file:
        data = json.load(json_data_file)

    layers = SonataLayer(INITIAL_LAYER,
                         data,
                         fields=data[INITIAL_LAYER][TARGET_NAME]["fields"],
                         offset=0,
                         parent_layer=None,
                         child_layers=data[INITIAL_LAYER][TARGET_NAME]["child_layers"],
                         field_that_determines_child=None,
                         is_payload = data[INITIAL_LAYER][TARGET_NAME]["in_payload"],
                         )

    # print layers
    children = layers.get_all_child_layers()

    print [c.name for c in children]

    rawField = SonataRawFields(layers)

    print rawField.all_sonata_fields
    print rawField.all_fields


if __name__ == '__main__':
    test()
