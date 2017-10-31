class QueryObject(object):
    def __init__(self, id):
        self.id = id
        self.operators = list()
        self.parse_payload = False
        self.filter_payload = False
        self.filter_payload_str = ''
        self.payload_fields = list()
        self.read_register = False

    def __repr__(self):
        out = 'In'
        for operator in self.operators:
            out += '\n\t'+operator.__repr__()
        return out