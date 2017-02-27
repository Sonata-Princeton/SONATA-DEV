"""
This module translates each shard of size W into
hypothesis graph
"""

from utils import *
from query_engine.sonata_queries import *
from config import *
import copy
import numpy as np

class Hypothesis(object):
    def __init__(self, query_training):
        self.filter_mappings = {}
        self.qid_2_queries_refined = {}
        self.refined_sonata_queries = {}

        self.query_training = query_training

        self.generate_refined_queries()

    def generate_refined_queries(self, fname_rq_write = ''):
        # Add timestamp for each key
        self.query_training.qid_2_query = add_timestamp_key(self.query_training.qid_2_query)

        # Generate refined queries
        self.generate_refined_intermediate_sonata_queries()

        self.update_filter()
        print self.refined_sonata_queries
        """
        print self.refined_sonata_queries

        worst_case_queries = {}

        for qid in self.refined_sonata_queries:
            if 32 in self.refined_sonata_queries[qid]:
                refined_query_id = 1000*(10000*(qid)+32)+1
                worst_case_queries[qid] = self.refined_sonata_queries[qid][32][refined_query_id]

        self.worst_case_queries = worst_case_queries

        print self.worst_case_queries
        self.get_query_output_for_worst_case()

        self.generate_refined_spark_queries()
        print self.refined_queries

        # Dump refined queries
        if fname_rq_write != '':
            self.dump_refined_queries(fname_rq_write)
        """

    def generate_refined_intermediate_sonata_queries(self):
        qid_2_queries_refined = {}
        refined_sonata_queries = {}

        # First update the Sonata queries for different levels
        for (qid, sonata_query) in self.query_training.qid_2_query.iteritems():
            if qid in self.query_training.qid_2_query:
                refined_sonata_queries[qid] = {}
                reduction_key = self.query_training.qid_2_query[qid].reduction_key


                for ref_level in self.query_training.ref_levels[1:]:

                    refined_sonata_queries[qid][ref_level] = {}
                    refined_query_id = 10000*qid+ref_level

                    # base refined query + headers
                    refined_sonata_query = PacketStream(refined_query_id)
                    refined_sonata_query.basic_headers = BASIC_HEADERS

                    # Add refinement level, eg: 32, 24
                    refined_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))

                    # Copy operators to the new refined sonata query
                    for operator in sonata_query.operators:
                        if operator.name == 'Join':
                            operator.in_stream = 'self.training_data.'
                        copy_operators(refined_sonata_query, operator)

                    qid_2_queries_refined[refined_query_id] = refined_sonata_query

                    # generate intermediate queries for this refinement level
                    sonata_intermediate_queries, filter_mappings_tmp = generate_intermediate_queries(refined_sonata_query, ref_level)
                    self.filter_mappings.update(filter_mappings_tmp)

                    for iter_qid in sonata_intermediate_queries:
                        refined_sonata_queries[qid][ref_level][iter_qid] = sonata_intermediate_queries[iter_qid]

        self.qid_2_queries_refined = qid_2_queries_refined
        self.refined_sonata_queries = refined_sonata_queries


    def update_filter(self):
        spark_queries = {}
        reversed_ref_levels = self.query_training.ref_levels[1:]
        reversed_ref_levels.sort(reverse=True)
        print reversed_ref_levels
        level_32_sonata_query = None
        satisfied_sonata_spark_query = None

        for ref_level in reversed_ref_levels:
            print "Refinement Level", ref_level

            for (prev_qid, curr_qid, ref_level_tmp) in self.filter_mappings:
                if ref_level == ref_level_tmp:
                    prev_parent_qid = prev_qid/10000000
                    current_parent_qid = curr_qid/10000000

                    reduction_key = self.query_training.qid_2_query[current_parent_qid].reduction_key
                    print  self.query_training.qid_2_query, current_parent_qid, reduction_key
                    qids_after_this_filter = filter(lambda x: x >=curr_qid,
                                           self.refined_sonata_queries[current_parent_qid][ref_level].keys())

                    prev_sonata_query = self.refined_sonata_queries[prev_parent_qid][ref_level][prev_qid]
                    curr_sonata_query = self.refined_sonata_queries[current_parent_qid][ref_level][curr_qid]

                    if ref_level != 32:
                        satisfied_sonata_query = PacketStream(level_32_sonata_query.qid)
                        satisfied_sonata_query.basic_headers = BASIC_HEADERS
                        for operator in level_32_sonata_query.operators:
                            copy_operators(satisfied_sonata_query, operator)
                        satisfied_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))

                        satisfied_sonata_spark_query = spark.PacketStream(prev_qid)
                        satisfied_sonata_spark_query.basic_headers = BASIC_HEADERS
                        for operator in satisfied_sonata_query.operators:
                            copy_sonata_operators_to_spark(satisfied_sonata_spark_query, operator)

                # Get the Spark queries corresponding to the prev and curr sonata queries
                    if prev_qid not in spark_queries:
                        prev_spark_query = spark.PacketStream(prev_qid)
                        prev_spark_query.basic_headers = BASIC_HEADERS
                        for operator in prev_sonata_query.operators:
                            copy_sonata_operators_to_spark(prev_spark_query, operator)

                        spark_queries[prev_qid] = prev_spark_query
                    else:
                        prev_spark_query = spark_queries[prev_qid]

                    _, filter_id, spread = self.filter_mappings[(prev_qid, curr_qid, ref_level)]
                    #thresh = -1

                    thresh = self.get_thresh(prev_spark_query, spread, ref_level, satisfied_sonata_spark_query, reduction_key)

                    # Update all the following intermediate Sonata Queries
                    for tmp_qid in qids_after_this_filter:
                        filter_ctr = 1
                        son_query = self.refined_sonata_queries[current_parent_qid][ref_level][tmp_qid]
                        for operator in son_query.operators:
                            if operator.name == 'Filter':
                                if filter_ctr == filter_id:
                                    operator.func = ('geq',thresh)
                                    print "Updated threshold for ", curr_qid, operator
                                    break
                                else:
                                    filter_ctr += 1
                    self.refined_sonata_queries[current_parent_qid][ref_level][curr_qid] = copy.deepcopy(curr_sonata_query)

                    if ref_level == 32:
                        level_32_sonata_query = copy.deepcopy(curr_sonata_query)


    def get_thresh(self, spark_query, spread, refinement_level, satisfied_sonata_spark_query, reduction_key):
        if refinement_level == 32:
            query_string = 'self.query_training.training_data.'+spark_query.compile()+'.map(lambda s: s[1]).collect()'
            data = [float(x) for x in (eval(query_string))]
            thresh = 0.0
            if len(data) > 0:
                thresh = int(np.percentile(data, int(spread)))
                print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data,75), \
                    "95 %", np.percentile(data,95), "99 %", np.percentile(data,99)
            print "Thresh:", thresh
            #satisfied_sonata_query
            #satisfied_out = 'self.query_training.training_data.'+spark_query.compile()+'.filter(lambda s: s[1]> int('+str(thresh)+'))'

        else:
            refined_satisfied_out = 'self.query_training.training_data.' + satisfied_sonata_spark_query.compile() + '.map(lambda s: (s, 1)).reduceByKey(lambda x,y: x+y)'
            #print refined_satisfied_out
            query_string = 'self.query_training.training_data.'+spark_query.compile()+'.join('+refined_satisfied_out+').map(lambda s: s[1][0]).collect()'
            print query_string
            data = [float(x) for x in (eval(query_string))]
            thresh = min(data)
            print data, thresh

            original_query_string = 'self.query_training.training_data.'+spark_query.compile()+'.map(lambda s: s[1]).collect()'
            data = [float(x) for x in (eval(original_query_string))]
            if len(data) > 0:
                print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data,75), \
                    "95 %", np.percentile(data,95), "99 %", np.percentile(data,99)

        return thresh