class QueryObject(object):
    def __init__(self, id):
        self.id = id
        self.operators = list()
        self.parse_payload = False
        self.payload_fields = list()

    def __repr__(self):
        out = 'In'
        for operator in self.operators:
            out += operator.__repr__()
        return out