#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine.query_generator import *
from query_engine.sonata_queries import *
from utils import *
from pyspark import SparkContext
import os
import pickle

# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes",
                 "proto", "sMac", "dMac"]


class QueryTraining(object):
    sc = SparkContext(appName="SONATA-Training")
    # Load data
    baseDir = os.path.join('/home/vagrant/dev/data/sample_data/')
    flows_File = os.path.join(baseDir, 'sample_data.csv')
    ref_levels = range(0, 33, 16)

    def __init__(self, refined_queries = None, fname_rq_read = '', fname_rq_write = '',
                 query_generator = None, fname_qg = ''):
        self.training_data = (self.sc.textFile(self.flows_File)
                              .map(parse_log_line)
                              .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[2:]))))
                              .cache())

        if refined_queries is None:
            if fname_rq_read == '':
                self.process_refined_queries(query_generator, fname_qg, fname_rq_write)
            else:
                with open(fname_rq_read, 'r') as f:
                    self.refined_queries = pickle.load(f)
        else:
            self.refined_queries = refined_queries

    def process_refined_queries(self, query_generator, fname_qg, fname_rq_write):
        # Update the query Generator Object (either passed directly, or filename specified)
        if query_generator is None:
            if fname_qg == '':
                fname_qg = 'query_engine/query_dumps/query_generator_object_1.pickle'
            with open(fname_qg,'r') as f:
                query_generator = pickle.load(f)

        self.query_generator = query_generator
        self.max_reduce_operators = self.query_generator.max_reduce_operators
        self.qid_2_sonata_query = query_generator.qid_2_query

        # Add timestamp for each key
        self.add_timestamp_key()

        # Update the intermediate query mappings and filter mappings
        self.update_intermediate_queries()

        # Update filters for each SONATA Query
        self.update_filter()

        # Generate refined queries
        self.generate_refined_queries()
        print self.refined_queries

        # Dump refined queries
        self.dump_refined_queries(fname_rq_write)

    def generate_refined_queries(self):
        refined_queries = {}
        for (qid, sonata_query) in self.qid_2_sonata_query.iteritems():
            print "Exploring Sonata Query", qid
            refined_queries[qid] = {}
            reduction_key = list(sonata_query.get_reduction_key()-set(['ts']))[0]
            print "Reduction Key:", reduction_key

            for ref_level in ref_levels[1:]:
                print "Refinement Level", ref_level
                refined_queries[qid][ref_level] = {}
                refined_query_id = 10000*qid+ref_level
                refined_sonata_query = PacketStream(refined_query_id)
                refined_sonata_query.basic_headers = BASIC_HEADERS
                refined_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))
                for operator in sonata_query.operators:
                    copy_sonata_operators_to_spark(refined_sonata_query, operator)

                tmp1, _ = get_intermediate_spark_queries(self.max_reduce_operators, refined_sonata_query)
                for iter_qid in tmp1:
                    print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                    refined_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]
        self.refined_queries

    def update_filter(self):
        for (prev_qid, curr_qid) in self.filter_mappings:
            prev_query = self.spark_intermediate_queries[prev_qid]
            sonata_query_id, filter_id, spread = self.filter_mappings[(prev_qid, curr_qid)]
            mean = self.get_mean(prev_query)
            stdev = self.get_stdev(prev_query)
            thresh = mean+spread*stdev
            sonata_query = self.qid_2_sonata_query[sonata_query_id]
            filter_ctr = 1
            for operator in sonata_query.operators:
                if operator.name == 'Filter':
                    if filter_ctr == filter_id:
                        operator.func = ('geq',thresh)
                        print "Updated threshold for ", sonata_query_id, operator
                        break
                    else:
                        filter_ctr += 1

    def update_intermediate_queries(self):
        spark_intermediate_queries = {}
        filter_mappings = {}
        for (qid, sonata_query) in self.qid_2_sonata_query.iteritems():
            print qid, sonata_query
            # Initialize Spark Query
            tmp1, tmp2 = get_intermediate_spark_queries(query_generator.max_reduce_operators, sonata_query)
            spark_intermediate_queries.update(tmp1)
            filter_mappings.update(tmp2)
            #break
        print spark_intermediate_queries.keys(), filter_mappings
        self.filter_mappings = filter_mappings
        self.spark_intermediate_queries = spark_intermediate_queries


    def add_timestamp_key(self):
        for qid in self.qid_2_query:
            query = self.qid_2_query[qid]
            print qid
            print "Before:", query
            for operator in query.operators:
                operator.keys = tuple(['ts'] + list(operator.keys))
            print "After:", query

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

    def dump_refined_queries(self, fname_rq_write):
        with open(fname_rq_write,'w') as f:
            pickle.dump(self.refined_queries, f)


if __name__ == "__main__":
    fname_rq_read = 'query_engine/query_dumps/refined_queries_1.pickle'
    qt = QueryTraining(fname_rq_read=fname_rq_read)




