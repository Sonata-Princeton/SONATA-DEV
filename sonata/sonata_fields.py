

class SonataField(object):
    sonata_name = ""
    targets = []
    target_2_name = []

    def __init__(self, sonata_name, targets, target_2_name):
        self.sonata_name = sonata_name
        self.targets = targets
        self.target_2_name = target_2_name
