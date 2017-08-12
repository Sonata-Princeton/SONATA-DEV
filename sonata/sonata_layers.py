from sonata_fields import SonataField


class SonataLayer(object):
    field_that_determines_child = None
    target_name = None
    child_layers = {}
    fields = []

    def __init__(self, name, target_name, conf, fields=[], offset=0, parent_layer=None, child_layers=None,
                 field_that_determines_child=None):
        self.name = name
        self.target_name = target_name
        self.conf = conf
        self.offset = offset
        self.parent_layer = parent_layer
        print child_layers
        child_layers_tmp = {}

        if fields:
            for field in fields:
                self.fields.append(SonataField(layer=self,
                                               sonata_name=field["sonata_name"],
                                               target_name=field["target_name"],
                                               size=field["size"]
                                               )
                                   )

        if child_layers:
            for key, layer_name in child_layers.items():
                print "Adding: " + layer_name + " in " + name + " for " + self.name
                child_layers_tmp[key] = SonataLayer(layer_name,
                                target_name,
                                conf,
                                fields=conf[layer_name][target_name]["fields"],
                                offset=key,
                                parent_layer=self,
                                child_layers=conf[layer_name][target_name]["child_layers"],
                                field_that_determines_child=None)

        self.child_layers = child_layers_tmp
        # print self.name, self.child_layers

        self.field_that_determines_child = field_that_determines_child

    def __repr__(self):
        return """SonataLayer(name="""+self.name+""",
        fields=""" + str([field for field in self.fields]) + """
        child_layers=""" + str([str(layer) for key, layer in self.child_layers.items()]) + """ \n"""
    def get_name(self):
        return self.name

    def get_parent_layers(self):
        return self.parent_layer

    def get_child_layers(self):
        return self.child_layers

def test():

    TARGET_NAME = "bmv2"
    INITIAL_LAYER = "Ethernet"

    import json

    with open('/home/vagrant/dev/sonata/fields_mapping.json') as json_data_file:
        data = json.load(json_data_file)

    print data[INITIAL_LAYER][TARGET_NAME]

    layers = SonataLayer(INITIAL_LAYER,
                TARGET_NAME,
                data,
                fields=data[INITIAL_LAYER][TARGET_NAME]["fields"],
                offset=0,
                parent_layer=None,
                child_layers=data[INITIAL_LAYER][TARGET_NAME]["child_layers"],
                field_that_determines_child=None
                )

    print layers

if __name__ == '__main__':
    test()