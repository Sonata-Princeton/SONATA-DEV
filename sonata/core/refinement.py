#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from sonata.core.utils import *
import sonata.streaming_driver.query_object as spark
from partition import Partition


def get_refined_query_id(query, ref_level):
    # print "get_refined_query_id", ref_level, query
    return 10000*query.qid + ref_level


def get_thresh(training_data, spark_query, spread, refinement_level, satisfied_sonata_spark_query, ref_levels):
    if refinement_level == ref_levels[-1]:
        # test_str = 'training_data.' + spark_query.compile() + '.collect()'
        # print test_str
        # test_data = eval(test_str)
        # print test_data[:5]
        query_string = 'training_data.' + spark_query.compile() + '.map(lambda s: s[1]).collect()'
        # print query_string
        data = [float(x) for x in (eval(query_string))]
        thresh = 0.0
        if len(data) > 0:
            thresh = int(np.percentile(data, float(spread)))
            print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data, 75), \
                "95 %", np.percentile(data, 95), "99 %", np.percentile(data, 99), "99.9 %", np.percentile(data, 99.9), \
                "99.99 %", np.percentile(data, 99.99), "99.999 %", np.percentile(data, 99.999)
        if thresh == 1:
            thresh += 1
        #thresh = 5
        print "Thresh:", thresh, refinement_level

    else:
        refined_satisfied_out = 'training_data.' + satisfied_sonata_spark_query.compile() + \
                                '.map(lambda s: (s, 1)).reduceByKey(lambda x,y: x+y)'
        # print refined_satisfied_out
        query_string = 'training_data.' + spark_query.compile() + \
                       '.join(' + refined_satisfied_out + ').map(lambda s: s[1][0]).collect()'
        # print query_string
        data = [float(x) for x in (eval(query_string))]
        data.sort()
        print "Values at refinement level", refinement_level
        print data[:5]
        thresh = min(data)
        if thresh == 1:
            thresh += 1
        print thresh

        original_query_string = 'training_data.' + spark_query.compile() + '.map(lambda s: s[1]).collect()'
        data = [float(x) for x in (eval(original_query_string))]
        if len(data) > 0:
            print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data, 75), \
                "95 %", np.percentile(data, 95), "99 %", np.percentile(data, 99), "99.9 %", np.percentile(data, 99.9), \
                "99.99 %", np.percentile(data, 99.99), "99.999 %", np.percentile(data, 99.999)
        print "Thresh:", thresh, refinement_level

    return thresh


def apply_refinement_plan(sonata_query, refinement_key, refined_query_id, ref_level):
    # base refined query + headers
    refined_sonata_query = PacketStream(refined_query_id)
    refined_sonata_query.basic_headers = BASIC_HEADERS

    # Add refinement level, eg: 32, 24
    refined_sonata_query.map(map_keys=(refinement_key,), func=("mask", ref_level))

    # Copy operators to the new refined sonata query
    for operator in sonata_query.operators:
        copy_operators(refined_sonata_query, operator)

    return refined_sonata_query


class Refinement(object):
    refined_sonata_queries = {}
    filter_mappings = {}
    qid_2_refined_queries = {}

    def __init__(self, query, target):
        self.query = query
        self.target = target
        self.ref_levels = range(0, GRAN_MAX, GRAN)
        # self.ref_levels = [0,4,32]
        self.refinement_key = list(get_refinement_keys(self.query))[0]
        self.qid_2_query = get_qid_2_query(self.query)
        print self.qid_2_query

        # Add timestamp for each key
        self.add_timestamp_key()

        # Generate refined intermediate SONATA queries
        self.generate_refined_intermediate_sonata_queries()

    def get_refined_updated_query(self, qid, ref_level, prev_qid = 0, prev_ref_level = 0):
        # return query with updated threshold values and map operation---masking based on refinement level
        iter_qids = self.refined_sonata_queries[qid][ref_level].keys()
        iter_qids.sort()
        tmp_query = self.refined_sonata_queries[qid][ref_level][iter_qids[-1]]
        if prev_ref_level > 0:
            out_query = PacketStream(tmp_query.qid)
            out_query.basic_headers = BASIC_HEADERS
            refined_qid_src = 10000*prev_qid + prev_ref_level
            out_query.filter(append_type=1, src=refined_qid_src, filter_keys=(self.refinement_key,),
                                 func=('mask',prev_ref_level,))

            for operator in tmp_query.operators:
                copy_operators(out_query, operator)
        else:
            out_query = tmp_query

        return out_query

    def add_timestamp_key(self):
        def add_timestamp_to_query(q):
            # This function will be useful if we need to add ts in recursion
            for operator in q.operators:
                operator.keys = tuple(['ts'] + list(operator.keys))

        for qid in self.qid_2_query:
            query = self.qid_2_query[qid]
            add_timestamp_to_query(query)

    def generate_refined_intermediate_sonata_queries(self):
        qid_2_queries_refined = {}
        refined_sonata_queries = {}
        filter_mappings = {}

        # First update the Sonata queries for different levels
        for (qid, sonata_query) in self.qid_2_query.iteritems():
            if qid in self.qid_2_query:
                refined_sonata_queries[qid] = {}
                refinement_key = self.refinement_key
                ref_levels = self.ref_levels

                for ref_level in ref_levels[1:]:
                    refined_sonata_queries[qid][ref_level] = {}
                    refined_query_id = get_refined_query_id(sonata_query, ref_level)
                    refined_sonata_query = apply_refinement_plan(sonata_query, refinement_key, refined_query_id,
                                                                 ref_level)
                    qid_2_queries_refined[refined_query_id] = refined_sonata_query

                    # Create target-specific partition object for this refined query
                    partition_object = Partition(refined_sonata_query, self.target, ref_level)
                    # generate intermediate queries for learning
                    partition_object.generate_partitioned_queries_learning()
                    # update intermediate queries and filter mappings
                    sonata_intermediate_queries = partition_object.intermediate_learning_queries
                    filter_mappings_tmp = partition_object.filter_mappings
                    filter_mappings.update(filter_mappings_tmp)

                    # Update refined sonata queries
                    for part_qid in sonata_intermediate_queries:
                        refined_sonata_queries[qid][ref_level][part_qid] = sonata_intermediate_queries[part_qid]

        self.refined_sonata_queries = refined_sonata_queries
        self.filter_mappings = filter_mappings
        self.qid_2_refined_queries = qid_2_queries_refined

    def update_filter(self, training_data):
        spark_queries = {}
        reversed_ref_levels = self.ref_levels[1:]
        reversed_ref_levels.sort(reverse=True)
        level_32_sonata_query = None
        satisfied_spark_query = None

        for ref_level in reversed_ref_levels:
            for (prev_qid, curr_qid, ref_level_tmp) in self.filter_mappings:
                if ref_level == ref_level_tmp:
                    prev_parent_qid = prev_qid / 10000000
                    current_parent_qid = curr_qid / 10000000

                    refinement_key = self.refinement_key
                    qids_after_this_filter = filter(lambda x: x >= curr_qid,
                                                    self.refined_sonata_queries[current_parent_qid][ref_level].keys())

                    prev_sonata_query = self.refined_sonata_queries[prev_parent_qid][ref_level][prev_qid]
                    curr_sonata_query = self.refined_sonata_queries[current_parent_qid][ref_level][curr_qid]

                    if ref_level != self.ref_levels[-1]:
                        satisfied_sonata_query = PacketStream(level_32_sonata_query.qid)
                        satisfied_sonata_query.basic_headers = BASIC_HEADERS
                        for operator in level_32_sonata_query.operators:
                            copy_operators(satisfied_sonata_query, operator)
                        satisfied_sonata_query.map(map_keys=(refinement_key,), func=("mask", ref_level))

                        satisfied_spark_query = spark.PacketStream(prev_qid)
                        satisfied_spark_query.basic_headers = BASIC_HEADERS
                        for operator in satisfied_sonata_query.operators:
                            copy_sonata_operators_to_spark(satisfied_spark_query, operator)

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
                    # thresh = -1

                    thresh = get_thresh(training_data, prev_spark_query, spread, ref_level, satisfied_spark_query,
                                        self.ref_levels)

                    # Update all the following intermediate Sonata Queries
                    for tmp_qid in qids_after_this_filter:
                        filter_ctr = 1
                        son_query = self.refined_sonata_queries[current_parent_qid][ref_level][tmp_qid]
                        for operator in son_query.operators:
                            if operator.name == 'Filter':
                                if filter_ctr == filter_id:
                                    operator.func = ('geq', thresh)
                                    # print "Updated threshold for ", curr_qid, operator
                                    break
                                else:
                                    filter_ctr += 1
                    self.refined_sonata_queries[current_parent_qid][ref_level][curr_qid] = copy.deepcopy(curr_sonata_query)

                    if ref_level == self.ref_levels[-1]:
                        level_32_sonata_query = copy.deepcopy(curr_sonata_query)