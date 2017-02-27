import math
from query_engine.sonata_queries import *
from config import *
from netaddr import *
def parse_log_line(logline):
    return tuple(logline.split(","))

def shard_training_data(sc, flows_File, T):

    training_data = (sc.textFile(flows_File)
                          .map(parse_log_line)
                          .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                          .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(sPort) == '53')
                          )
    print "Collecting the training data for the first time ..."
    training_data = sc.parallelize(training_data.collect())
    print "Collecting timestamps for the experiment ..."
    timestamps = training_data.map(lambda s: s[0]).distinct().collect()
    print "Timestamps are: ", timestamps
    return timestamps, training_data

def add_timestamp_key(qid_2_query):
    def add_timestamp_to_query(q):
        # This function will be useful if we need to add ts in recursion
        for operator in q.operators:
            operator.keys = tuple(['ts'] + list(operator.keys))

    for qid in qid_2_query:
        query = qid_2_query[qid]
        add_timestamp_to_query(query)
    return qid_2_query


def generate_intermediate_queries(sonata_query, refinement_level):
    number_intermediate_queries = len(filter(lambda s: s in ['Distinct', 'Reduce', 'Filter'], [x.name for x in sonata_query.operators]))
    sonata_intermediate_queries = {}
    prev_qid = 0
    filter_mappings = {}
    filters_marked = {}
    for max_operators in range(1,1+number_intermediate_queries):
        qid = (1000*sonata_query.qid)+max_operators
        tmp_query = (PacketStream(sonata_query.qid))
        tmp_query.basic_headers = BASIC_HEADERS
        ctr = 0
        filter_ctr = 0
        for operator in sonata_query.operators:
            if operator.name != 'Join':
                if ctr < max_operators:
                    copy_operators(tmp_query, operator)
                else:
                    break
                if operator.name in ['Distinct', 'Reduce', 'Filter']:
                    ctr += 1
                if operator.name == 'Filter':
                    filter_ctr += 1
                    if (qid, refinement_level, filter_ctr) not in filters_marked:
                        filters_marked[(qid, refinement_level, filter_ctr)] = sonata_query.qid
                        filter_mappings[(prev_qid, qid, refinement_level)] = (sonata_query.qid, filter_ctr, operator.func[1])
            else:
                copy_operators(tmp_query, operator)

        sonata_intermediate_queries[qid] = tmp_query
        prev_qid = qid

    return sonata_intermediate_queries, filter_mappings
