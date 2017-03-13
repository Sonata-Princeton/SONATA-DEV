class QueryObject(object):
    def __init__(self, id):
        self.id = id
        self.operators = list()
        self.parse_payload = False

def send_to_dp_driver(type, message):
    return [0,3,5]

def sonata_2_dp_query(query):
    dp_query = QueryObject(query.qid)
    for operator in query.operators:
        dp_query.operators.append(operator)

    return None
