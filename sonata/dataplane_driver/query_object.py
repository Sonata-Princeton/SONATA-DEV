class QueryObject(object):
    def __init__(self, id):
        self.id = id
        self.operators = list()
        self.parse_payload = False