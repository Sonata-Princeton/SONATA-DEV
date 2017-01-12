from query_engine.query_generator import *
from query_engine.sonata_queries import *
from pyspark import SparkContext
import os
import pickle

# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes",
                 "proto", "sMac", "dMac"]


def parseDNSData(logline):
    return tuple(logline.split(","))


def add_timestamp_key(qid_2_query):
    for qid in qid_2_query:
        query = qid_2_query[qid]
        print qid
        print "Before:", query
        for operator in query.operators:
            operator.keys = tuple(['ts'] + list(operator.keys))
        print "After:", query
    return qid_2_query


class Learning(object):
    sc = SparkContext(appName="SONATA-Training")
    # Load data
    baseDir = os.path.join('/home/vagrant/dev/data/sample_data/')
    flows_File = os.path.join(baseDir, 'sample_data.csv')

    def __init__(self):
        self.training_data = (self.sc.textFile(self.flows_File)
                              .map(parseDNSData)
                              .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[2:]))))
                              .cache())

    def get_mean(self, spark_query):
        query_string = 'self.training_data.'+spark_query.compile()+'.map(lambda s: s[1]).mean()'
        #print query_string
        mean = eval(query_string)
        print "Mean:", mean
        return mean

    def get_stdev(self, spark_query):
        query_string = 'self.training_data.'+spark_query.compile()+'.map(lambda s: s[1]).stdev()'
        #print query_string
        stdev = eval(query_string)
        print "Stdev:", stdev
        return stdev


def get_intermediate_spark_queries(max_reduce_operators, sonata_query):
    reduce_operators = filter(lambda s: s in ['Distinct', 'Reduce'], [x.name for x in sonata_query.operators])
    spark_intermediate_queries = {}
    prev_qid = 0
    filter_mappings = {}
    filters_marked = {}
    for max_reduce_operators in range(1,2+len(reduce_operators)):
        qid = 1000*sonata_query.qid+max_reduce_operators
        tmp_spark_query = (spark.PacketStream(sonata_query.qid))
        tmp_spark_query.basic_headers = BASIC_HEADERS
        ctr = 0
        filter_ctr = 0
        for operator in sonata_query.operators:
            if ctr < max_reduce_operators:
                copy_sonata_operators_to_spark(tmp_spark_query, operator)
            else:
                break
            if operator.name in ['Distinct', 'Reduce']:
                ctr += 1
            if operator.name == 'Filter':
                filter_ctr += 1
                if (sonata_query.qid, filter_ctr) not in filters_marked:
                    filters_marked[(sonata_query.qid, filter_ctr)] = qid
                    filter_mappings[(prev_qid,qid)] = (sonata_query.qid, filter_ctr, operator.func[1])

        spark_intermediate_queries[qid] = tmp_spark_query
        print max_reduce_operators, qid, tmp_spark_query
        prev_qid = qid
    return spark_intermediate_queries, filter_mappings


def update_filter(td, qid_2_sonata_query, spark_intermediate_queries, filter_mappings):
    for (prev_qid, curr_qid) in filter_mappings:
        prev_query = spark_intermediate_queries[prev_qid]
        sonata_query_id, filter_id, spread = filter_mappings[(prev_qid, curr_qid)]
        mean = td.get_mean(prev_query)
        stdev = td.get_stdev(prev_query)
        thresh = mean+spread*stdev
        sonata_query = qid_2_sonata_query[sonata_query_id]
        filter_ctr = 1
        for operator in sonata_query.operators:
            if operator.name == 'Filter':
                if filter_ctr == filter_id:
                    operator.func = ('geq',thresh)
                    print "Updated threshold for ", sonata_query_id, operator
                    break
                else:
                    filter_ctr += 1

    return qid_2_sonata_query

def generate_refined_queries(query_generator):
    refined_queries = {}
    qid_2_sonata_query = query_generator.qid_2_query
    for (qid, sonata_query) in qid_2_sonata_query.iteritems():
        print "Exploring Sonata Query", qid
        refined_queries[qid] = {}
        reduction_key = list(sonata_query.get_reduction_key())[0]
        print "Reduction Key:", reduction_key
        ref_levels = range(0, 33, 16)
        for ref_level in ref_levels[1:]:
            print "Refinement Level", ref_level
            refined_queries[qid][ref_level] = {}
            refined_query_id = 10000*qid+ref_level
            refined_sonata_query = PacketStream(refined_query_id)
            refined_sonata_query.basic_headers = BASIC_HEADERS
            refined_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))
            for operator in sonata_query.operators:
                copy_sonata_operators_to_spark(refined_sonata_query, operator)

            tmp1, _ = get_intermediate_spark_queries(query_generator.max_reduce_operators, refined_sonata_query)
            for iter_qid in tmp1:
                print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                refined_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]
    return refined_queries


if __name__ == "__main__":
    learning_object = Learning()
    fname = 'query_engine/query_dumps/query_generator_object_1.pickle'
    with open(fname,'r') as f:
        query_generator = pickle.load(f)

    qid_2_sonata_query = query_generator.qid_2_query
    # Add timestamp for each key
    qid_2_sonata_query = add_timestamp_key(qid_2_sonata_query)

    spark_intermediate_queries = {}
    filter_mappings = {}
    for (qid, sonata_query) in qid_2_sonata_query.iteritems():
        print qid, sonata_query
        # Initialize Spark Query
        tmp1, tmp2 = get_intermediate_spark_queries(query_generator.max_reduce_operators, sonata_query)
        spark_intermediate_queries.update(tmp1)
        filter_mappings.update(tmp2)
        #break
    print spark_intermediate_queries.keys(), filter_mappings
    qid_2_sonata_query = update_filter(learning_object, qid_2_sonata_query, spark_intermediate_queries, filter_mappings)
    refined_queries = generate_refined_queries(query_generator)
    print refined_queries

    fname = 'query_engine/query_dumps/refined_queries_1.pickle'
    with open(fname,'w') as f:
        pickle.dump(refined_queries, f)
