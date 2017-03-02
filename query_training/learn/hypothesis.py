"""
This module translates each shard of size W into
hypothesis graph
"""

from utils import *
from query_engine.sonata_queries import *
from config import *
import copy
import numpy as np
import pickle


class Hypothesis(object):
    def __init__(self, query_training):

        self.query_out = None
        self.filter_mappings = {}
        self.qid_2_queries_refined = {}
        self.refined_sonata_queries = {}
        self.composed_refined_sonata_queries = {}

        self.query_training = query_training
        self.ref_levels = self.query_training.ref_levels
        self.query_generator = self.query_training.query_generator
        self.sc = self.query_training.sc
        self.timestamps, self.training_data = shard_training_data(self.sc, self.query_training.training_data_path, T)
        print self.query_training.qid_2_query

        self.generate_refined_queries()

        for qid in self.refined_spark_queries:
            print "Processing Refined Queries for cost...", qid
            #self.get_transit_query_output(qid)
            self.query_cost_transit_fname = 'query_cost_transit_'+str(qid)+'.pickle'
            #dump_data(self.query_out_transit, self.query_cost_transit_fname)
            with open(self.query_cost_transit_fname, 'r') as f:
                self.query_out_transit = pickle.load(f)


    def generate_refined_queries(self, fname_rq_write=''):
        # Add timestamp for each key
        self.query_training.qid_2_query = add_timestamp_key(self.query_training.qid_2_query)

        # Generate refined intermediate SONATA queries
        self.generate_refined_intermediate_sonata_queries()

        # Update the threshold for the filters operators for these SONATA queries
        self.update_filter()

        # Generate Spark queries for the composed & refined SONATA queries
        self.generate_refined_spark_queries()

    def get_transit_query_output(self, qid):
        """
        Computes per query costs
        :return:
        """
        out0 = self.training_data.collect()
        query_cost_transit = {}
        print "Out0", len(out0)
        # Iterate over each refined query and collect its output
        # for qid in self.refined_queries:

        query_cost_transit[qid] = {}


        query = self.query_training.qid_2_query[qid]
        reduction_key = query.reduction_key
        ref_levels = self.ref_levels

        # Get the query output for each refined intermediate queries
        query_out_refinement_level = self.get_query_output(qid, out0)

        # Get the query cost for each refinement transit, i.e. edge in the refinement graph
        # First get the cost for transit (0,ref_level)
        for ref_level in ref_levels[1:]:
            transit = (0,ref_level)
            query_cost_transit[qid][transit] = {}
            for iter_qid in self.refined_spark_queries[qid][ref_level]:
                spark_query = self.refined_spark_queries[qid][ref_level][iter_qid]
                out = query_out_refinement_level[qid][ref_level][iter_qid]
                transit_query_string = 'self.sc.parallelize(out)'
                transit_query_string = generate_query_to_collect_transit_cost(transit_query_string, spark_query.operators[-1].name)
                query_cost_transit[qid][transit][iter_qid] = eval(transit_query_string)
                print transit, iter_qid, spark_query.operators[-1].name, query_cost_transit[qid][transit][iter_qid][:2]
                #break

        # Then get the cost for transit (ref_level_prev, ref_level_current)
        for ref_level_prev in ref_levels[1:]:
            for ref_level_curr in ref_levels:
                if ref_level_curr > ref_level_prev:
                    transit = (ref_level_prev, ref_level_curr)
                    query_cost_transit[qid][transit] = {}
                    prev_level_out_mapped_string, prev_level_out = generate_query_string_prev_level_out_mapped(qid, ref_level_prev,
                                                                                                               query_out_refinement_level, self.refined_spark_queries, out0,
                                                                                                               reduction_key)
                    prev_level_out_mapped = eval(prev_level_out_mapped_string)
                    print prev_level_out_mapped.collect()[:2]
                    # For each intermediate query for `ref_level_curr` in transit (ref_level_prev, ref_level_current),
                    # we filter out entries that do not satisfy the query at level `ref_level_prev`
                    for iter_qid_curr in self.refined_spark_queries[qid][ref_level_curr]:
                        if iter_qid_curr > 0:
                            curr_level_out = query_out_refinement_level[qid][ref_level_curr][iter_qid_curr]
                            curr_query = self.refined_spark_queries[qid][ref_level_curr][iter_qid_curr]
                            transit_query_string = generate_transit_query(curr_query, curr_level_out,
                                                                          prev_level_out_mapped, ref_level_prev)
                            query_cost_transit[qid][transit][iter_qid_curr] = eval(transit_query_string)
                            print transit, iter_qid_curr, query_cost_transit[qid][transit][iter_qid_curr][:2]

        self.query_out_transit = query_cost_transit

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
                    refined_query_id = 10000 * qid + ref_level

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
                    sonata_intermediate_queries, filter_mappings_tmp = generate_intermediate_sonata_queries(
                        refined_sonata_query, ref_level)
                    self.filter_mappings.update(filter_mappings_tmp)

                    for iter_qid in sonata_intermediate_queries:
                        refined_sonata_queries[qid][ref_level][iter_qid] = sonata_intermediate_queries[iter_qid]

        self.qid_2_queries_refined = qid_2_queries_refined
        self.refined_sonata_queries = refined_sonata_queries
        # print self.refined_sonata_queries

    def update_filter(self):
        spark_queries = {}
        reversed_ref_levels = self.query_training.ref_levels[1:]
        reversed_ref_levels.sort(reverse=True)
        level_32_sonata_query = None
        satisfied_spark_query = None

        for ref_level in reversed_ref_levels:
            for (prev_qid, curr_qid, ref_level_tmp) in self.filter_mappings:
                if ref_level == ref_level_tmp:
                    prev_parent_qid = prev_qid / 10000000
                    current_parent_qid = curr_qid / 10000000

                    reduction_key = self.query_training.qid_2_query[current_parent_qid].reduction_key
                    qids_after_this_filter = filter(lambda x: x >= curr_qid,
                                                    self.refined_sonata_queries[current_parent_qid][ref_level].keys())

                    prev_sonata_query = self.refined_sonata_queries[prev_parent_qid][ref_level][prev_qid]
                    curr_sonata_query = self.refined_sonata_queries[current_parent_qid][ref_level][curr_qid]

                    if ref_level != self.query_training.ref_levels[-1]:
                        satisfied_sonata_query = PacketStream(level_32_sonata_query.qid)
                        satisfied_sonata_query.basic_headers = BASIC_HEADERS
                        for operator in level_32_sonata_query.operators:
                            copy_operators(satisfied_sonata_query, operator)
                        satisfied_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))

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

                    thresh = self.get_thresh(prev_spark_query, spread, ref_level, satisfied_spark_query)

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
                    self.refined_sonata_queries[current_parent_qid][ref_level][curr_qid] = copy.deepcopy(
                        curr_sonata_query)

                    if ref_level == self.query_training.ref_levels[-1]:
                        level_32_sonata_query = copy.deepcopy(curr_sonata_query)

    def generate_refined_spark_queries(self):
        # Compose the updated SONATA queries for different refinement levels
        refined_sonata_queries = {}
        for parent_qid in self.refined_sonata_queries:
            for ref_level in self.refined_sonata_queries[parent_qid]:
                ref_qid = 10000 * parent_qid + ref_level
                tmp = self.refined_sonata_queries[parent_qid][ref_level].keys()
                tmp.sort()
                final_iter_qid = tmp[-1]
                refined_sonata_queries[ref_qid] = self.refined_sonata_queries[parent_qid][ref_level][final_iter_qid]

        # Use the processed Sonata queries to generated refined+composed Spark queries
        refined_spark_queries = {}
        for ref_level in self.ref_levels[1:]:
            for n_query in self.query_generator.query_trees:
                composed_spark_queries = {}
                query_tree = self.query_generator.query_trees[n_query]
                updated_query_tree = {}
                update_query_tree(query_tree.keys()[0], query_tree, ref_level, updated_query_tree)
                #print updated_query_tree

                reduction_key = ['ts', self.query_generator.qid_2_query[query_tree.keys()[0]].reduction_key]

                generate_composed_spark_queries(reduction_key, BASIC_HEADERS, updated_query_tree,
                                                refined_sonata_queries, composed_spark_queries)
                for ref_qid in composed_spark_queries:
                    # print ref_qid, composed_queries[ref_qid].qid
                    if len(composed_spark_queries[ref_qid].operators) > 0:
                        tmp1, _ = generate_intermediate_spark_queries(composed_spark_queries[ref_qid], ref_level)
                        qid = ref_qid / 10000
                        if qid not in refined_spark_queries:
                            refined_spark_queries[qid] = {}
                        if ref_level not in refined_spark_queries[qid]:
                            refined_spark_queries[qid][ref_level] = {}
                        for iter_qid in tmp1:
                            # print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                            refined_spark_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]

        # print refined_spark_queries
        self.refined_spark_queries = refined_spark_queries

    def get_thresh(self, spark_query, spread, refinement_level, satisfied_sonata_spark_query):
        if refinement_level == self.query_training.ref_levels[-1]:
            query_string = 'self.training_data.' + spark_query.compile() + '.map(lambda s: s[1]).collect()'
            data = [float(x) for x in (eval(query_string))]
            thresh = 0.0
            if len(data) > 0:
                thresh = int(np.percentile(data, int(spread)))
                print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data, 75), \
                    "95 %", np.percentile(data, 95), "99 %", np.percentile(data, 99)
            if thresh == 1:
                thresh += 1
            print "Thresh:", thresh, refinement_level

        else:
            refined_satisfied_out = 'self.training_data.' + satisfied_sonata_spark_query.compile() + \
                                    '.map(lambda s: (s, 1)).reduceByKey(lambda x,y: x+y)'
            # print refined_satisfied_out
            query_string = 'self.training_data.' + spark_query.compile() + \
                           '.join(' + refined_satisfied_out + ').map(lambda s: s[1][0]).collect()'
            # print query_string
            data = [float(x) for x in (eval(query_string))]
            data.sort()
            print "Values at refinement level", refinement_level
            print data
            thresh = min(data)
            if thresh == 1:
                thresh += 1
            # print data, thresh

            original_query_string = 'self.training_data.' + spark_query.compile() + '.map(lambda s: s[1]).collect()'
            data = [float(x) for x in (eval(original_query_string))]
            if len(data) > 0:
                print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data, 75), \
                    "95 %", np.percentile(data, 95), "99 %", np.percentile(data, 99)
            print "Thresh:", thresh, refinement_level

        return thresh

    def get_query_output(self, qid, out0):
        # Get the query output for each refined intermediate queries
        query_out_refinement_level = {}
        query_out_refinement_level[qid] = {}
        for ref_level in self.refined_spark_queries[qid]:
            query_out_refinement_level[qid][ref_level] = {}
            for iter_qid in self.refined_spark_queries[qid][ref_level]:
                if iter_qid > 0:
                    spark_query = self.refined_spark_queries[qid][ref_level][iter_qid]
                    if len(spark_query.compile()) > 0:
                        tmp_compile = spark_query.compile()
                        query_string = 'self.training_data.' + tmp_compile + '.collect()'
                        #print("Processing Query", qid, "refinement level", ref_level, "iteration id", iter_qid)
                        out = eval(query_string)
                    else:
                        print "No query to process for", qid, "refinement level", ref_level, "iteration id", iter_qid
                        out = []
                    query_out_refinement_level[qid][ref_level][iter_qid] = out
                    #print len(query_out_refinement_level[qid][ref_level][iter_qid])

            query_out_refinement_level[qid][ref_level][0] = out0

        return query_out_refinement_level