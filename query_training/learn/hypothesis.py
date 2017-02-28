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

        self.query_out = None
        self.filter_mappings = {}
        self.qid_2_queries_refined = {}
        self.refined_sonata_queries = {}
        self.composed_refined_sonata_queries = {}

        self.query_training = query_training
        self.ref_levels = self.query_training.ref_levels
        self.query_generator = self.query_training.query_generator
        self.training_data = self.query_training.training_data
        self.sc = self.query_training.sc
        print self.query_training.qid_2_query

        self.generate_refined_queries()

        for qid in self.refined_spark_queries:
            print "Processing Refined Queries for cost...", qid
            self.get_query_output_less_memory(qid)

    def get_query_output_less_memory(self, qid):
        """
        Computes per query costs
        :return:
        """
        out0 = self.query_training.training_data.collect()
        query_costs = {}
        print "Out0", len(out0)
        # Iterate over each refined query and collect its output
        # for qid in self.refined_queries:

        query_costs[qid] = {}
        query_out = {}
        query_out[qid] = {}
        for ref_level in self.refined_spark_queries[qid]:
            query_out[qid][ref_level] = {}
            for iter_qid in self.refined_spark_queries[qid][ref_level]:
                if iter_qid > 0:
                    spark_query = self.refined_spark_queries[qid][ref_level][iter_qid]
                    if len(spark_query.compile()) > 0:
                        tmp_compile = spark_query.compile()
                        if spark_query.operators[-1].name == 'Distinct':
                            # Add the count mapping result to the output of intermediate query for distinct operation
                            # This makes it easier to perform the groupByKey operation
                            tmp_compile += '.map(lambda s: (s,1))'

                        query_string = 'self.training_data.' + tmp_compile + '.collect()'
                        query_string2 = "self.training_data." + tmp_compile + '.map(lambda s: (s[0][0], s[1])).groupByKey().map(lambda s: (s[0], list(s[1]))).collect()'
                        print("Processing Query", qid, "refinement level", ref_level, "iteration id", iter_qid)
                        # print query_string
                        out = eval(query_string)
                        out2 = eval(query_string2)
                        print out2[:5]
                    else:
                        print "No query to process for", qid, "refinement level", ref_level, "iteration id", iter_qid
                        out = []

                    query_out[qid][ref_level][iter_qid] = out
                    print len(query_out[qid][ref_level][iter_qid])

            query_out[qid][ref_level][0] = out0

        query_output_reformatted = {}
        query_costs_diff = {}

        print "Reformatting output of Refined Queries ...", qid
        # query_output_reformatted[qid] = self.get_reformatted_output_without_ts(qid, query_out[qid])

        print "Updating the Diff Entries ...", qid
        # query_costs_diff[qid] = self.get_query_diff_entries_without_ts(qid, query_output_reformatted)

    def get_query_diff_entries_without_ts(self, qid, query_output_reformatted):
        query_costs_diff = {}
        query = self.query_training.qid_2_query[qid]
        reduction_key = query.reduction_key
        ref_levels = self.ref_levels
        diff_counts = {}
        for ref_level_prev in ref_levels:
            for ref_level_curr in ref_levels:
                if ref_level_curr > ref_level_prev:
                    if ref_level_prev > 0:
                        transit = (ref_level_prev, ref_level_curr)
                        iter_qids_prev = query_output_reformatted[qid][ref_level_prev].keys()
                        iter_qids_curr = query_output_reformatted[qid][ref_level_curr].keys()
                        iter_qids_prev.sort()
                        iter_qids_curr.sort()

                        # print qid, transit, iter_qids_prev, iter_qids_curr
                        prev_out_final_query = query_output_reformatted[qid][ref_level_prev][iter_qids_prev[-1]]

                        if (ref_level_prev, ref_level_curr, 0) not in diff_counts:
                            out_zero_for_ctr_0 = query_output_reformatted[qid][ref_level_curr][0]
                            in_query = self.query_training.base_query
                            prev_bucket_count = self.get_diff_buckets(prev_out_final_query, out_zero_for_ctr_0,
                                                                      ref_level_prev, in_query, reduction_key)

                            diff_counts[(ref_level_prev, ref_level_curr, 0)] = prev_bucket_count
                            query_costs_diff[(transit, 0)] = diff_counts[(ref_level_prev, ref_level_curr, 0)]

                        for ctr in range(1, len(iter_qids_curr)):
                            # print qid, transit, iter_qids_prev, iter_qids_curr[ctr]

                            curr_out = query_output_reformatted[qid][ref_level_curr][iter_qids_curr[ctr]]
                            if (ref_level_prev, ref_level_curr, ctr) not in diff_counts:
                                curr_query = self.refined_spark_queries[qid][ref_level_curr][iter_qids_curr[ctr]]
                                diff_entries = self.get_diff_buckets(prev_out_final_query, curr_out, ref_level_prev,
                                                                     curr_query, reduction_key)
                                diff_counts[(ref_level_prev, ref_level_curr, ctr)] = diff_entries

                            query_costs_diff[(transit, iter_qids_curr[ctr])] = diff_counts[
                                (ref_level_prev, ref_level_curr, ctr)]
                            print qid, transit, iter_qids_prev, iter_qids_curr[ctr], query_costs_diff[
                                (transit, iter_qids_curr[ctr])]
                    else:
                        # No need to do any diff for this case
                        transit = (ref_level_prev, ref_level_curr)
                        iter_qids_prev = []
                        iter_qids_curr = query_output_reformatted[qid][ref_level_curr].keys()
                        iter_qids_prev.sort()
                        iter_qids_curr.sort()

                        # print qid, transit, iter_qids_prev, iter_qids_curr

                        for ctr in range(len(iter_qids_curr)):

                            curr_out = query_output_reformatted[qid][ref_level_curr][iter_qids_curr[ctr]]

                            if (ref_level_prev, ref_level_curr, ctr) not in diff_counts:
                                diff_entries = self.get_per_timestamp_counts(curr_out.keys())
                                diff_counts[(ref_level_prev, ref_level_curr, ctr)] = diff_entries
                            else:
                                print "This should not happen"

                            query_costs_diff[(transit, iter_qids_curr[ctr])] = diff_counts[
                                (ref_level_prev, ref_level_curr, ctr)]
                            print qid, transit, iter_qids_prev, iter_qids_curr[ctr], query_costs_diff[
                                (transit, iter_qids_curr[ctr])]
                            # print "Test", ctr, len(curr_out.keys()), transit, iter_qids_curr[ctr], diff_counts[(ref_level_prev, ref_level_curr, ctr)]
        return query_costs_diff

    def get_reformatted_output(self):
        query_output = self.query_out
        query_output_reformatted = {}
        for ts in self.query_training.timestamps:
            query_output_reformatted[ts] = {}
            for qid in query_output:
                query_output_reformatted[ts][qid] = {}
                for ref_level in query_output[qid]:
                    query_output_reformatted[ts][qid][ref_level] = {}
                    for iter_qid in query_output[qid][ref_level]:
                        query_output_reformatted[ts][qid][ref_level][iter_qid] = {}
                        out = query_output[qid][ref_level][iter_qid]
                        if len(out) > 0:
                            for entry in out:
                                # print entry
                                if type(entry[0]) == type(1):
                                    entry = (entry, 1)
                                ts_tmp = entry[0][0]
                                if ts_tmp == ts:
                                    k = tuple(entry[0][1:])
                                    v = entry[1]
                                    query_output_reformatted[ts][qid][ref_level][iter_qid][k] = v

                    print ts, qid, ref_level, query_output_reformatted[ts][qid][ref_level].keys()

        self.query_output_reformatted = query_output_reformatted

    def get_reformatted_output_without_ts(self, qid, query_out):
        query_output_reformatted = {}

        for ref_level in query_out:
            query_output_reformatted[ref_level] = {}
            for iter_qid in query_out[ref_level]:
                query_output_reformatted[ref_level][iter_qid] = {}
                out = query_out[ref_level][iter_qid]
                if len(out) > 0:
                    for entry in out:
                        if type(entry[0]) == type(1):
                            entry = (entry, 1)

                        k = tuple(entry[0][0:])
                        v = entry[1]
                        query_output_reformatted[ref_level][iter_qid][k] = v
                print qid, ref_level, iter_qid, len(query_output_reformatted[ref_level][iter_qid].keys())

            print qid, ref_level, query_output_reformatted[ref_level].keys()

        return query_output_reformatted

    def get_per_timestamp_counts(self, keys):
        """
        Given dict of type (ts, reduction_key) collect and compute per timestamp key counts
        :param keys:
        :return:
        """
        eval_string = "self.sc.parallelize(keys).map(lambda s: (s[0],1)).reduceByKey(lambda x,y: x+y).collect()"
        diff_entries = dict((x[0], x[1]) for x in eval(eval_string))

        return diff_entries

    def get_diff_buckets(self, prev_out, curr_out, ref_level_prev, curr_query, reduction_key):
        print "Get Diff Buckets called"
        if len(curr_query.operators) > 0:
            keys = curr_query.operators[-1].keys
        else:
            keys = BASIC_HEADERS

        prev_key_mapped = self.query_training.sc.parallelize(prev_out.keys()).map(lambda s: (s, 1))
        if len(keys) > 1:
            map_string = 'self.sc.parallelize(curr_out.keys()).map(lambda (' + ",".join(keys) + '): (ts,' + str(
                reduction_key) + ')).map(lambda (ts, dIP): ((ts, str(IPNetwork(str(dIP)+"/"+str(' + str(
                ref_level_prev) + ')).network)),1)).join(prev_key_mapped).map(lambda x: (x[0],x[1][0])).reduceByKey(lambda x,y: x+y).collect()'
        else:
            map_string = 'self.sc.parallelize(curr_out.keys()).map(lambda s: (s[0],s[1])).map(lambda (' + ",".join(
                keys) + '): (ts, ' + str(
                reduction_key) + ')).map(lambda (ts, dIP): ((ts, str(IPNetwork(str(dIP)+"/"+str(' + str(
                ref_level_prev) + ')).network)),1)).join(prev_key_mapped).map(lambda x: (x[0],x[1][0])).reduceByKey(lambda x,y: x+y).collect()'

        diff_entries = dict((x[0], x[1]) for x in eval(map_string))

        return diff_entries

    def generate_refined_queries(self, fname_rq_write=''):
        # Add timestamp for each key
        self.query_training.qid_2_query = add_timestamp_key(self.query_training.qid_2_query)

        # Generate refined intermediate SONATA queries
        self.generate_refined_intermediate_sonata_queries()

        # Update the threshold for the filters operators for these SONATA queries
        self.update_filter()

        # Generate Spark queries for the composed & refined SONATA queries
        self.generate_refined_spark_queries()

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
                print updated_query_tree

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

    def get_thresh(self, spark_query, spread, refinement_level, satisfied_sonata_spark_query):
        if refinement_level == self.query_training.ref_levels[-1]:
            query_string = 'self.query_training.training_data.' + spark_query.compile() + '.map(lambda s: s[1]).collect()'
            data = [float(x) for x in (eval(query_string))]
            thresh = 0.0
            if len(data) > 0:
                thresh = int(np.percentile(data, int(spread)))
                print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data, 75), \
                    "95 %", np.percentile(data, 95), "99 %", np.percentile(data, 99)
            print "Thresh:", thresh

        else:
            refined_satisfied_out = 'self.query_training.training_data.' + satisfied_sonata_spark_query.compile() + '.map(lambda s: (s, 1)).reduceByKey(lambda x,y: x+y)'
            # print refined_satisfied_out
            query_string = 'self.query_training.training_data.' + spark_query.compile() + '.join(' + refined_satisfied_out + ').map(lambda s: s[1][0]).collect()'
            # print query_string
            data = [float(x) for x in (eval(query_string))]
            thresh = min(data)
            # print data, thresh

            original_query_string = 'self.query_training.training_data.' + spark_query.compile() + '.map(lambda s: s[1]).collect()'
            data = [float(x) for x in (eval(original_query_string))]
            if len(data) > 0:
                print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data, 75), \
                    "95 %", np.percentile(data, 95), "99 %", np.percentile(data, 99)

        return thresh
