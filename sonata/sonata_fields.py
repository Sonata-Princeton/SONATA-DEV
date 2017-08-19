

class SonataField(object):
    sonata_name = ""
    target_name = ""
    size = 0
    layer = None

    def __init__(self, layer, sonata_name, target_name, size):

        self.layer = layer
        self.sonata_name = sonata_name
        self.target_name = target_name
        self.size = size

    def __repr__(self):
        return "SonataField(layer="+str(self.layer.name)+",s="+self.sonata_name+", t="+self.target_name+", size="+str(self.size)+")"
