"""
This module translates each shard of size W into
hypothesis graph
"""

import numpy as np

from sonata.core.training.utils import *
from sonata.core.utils import *


class Counts(object):
    """
    Compute counts (number of packets, bytes) for each edge in the hypothesis graph.
    1. Computes threshold (moved to refinement class)
    2. Generates refined queries (moved to refinement class)
    3. Executes generated refined queries (uses Spark batch processing) to compute the
       counts for each window interval in the data set.
    """

    query_tree = {}

    def __init__(self, query, sc, training_data, timestamps, refinement_object, target):

        self.query = query
        self.sc = sc
        self.training_data = training_data
        self.timestamps = timestamps
        self.target = target

        # load refinement object
        self.refinement_object = refinement_object
        self.refinement_key = refinement_object.refinement_key
        self.ref_levels = refinement_object.ref_levels
        self.filter_mappings = self.refinement_object.filter_mappings
        self.qid_2_refined_queries = self.refinement_object.qid_2_refined_queries
        self.qid_2_query = self.refinement_object.qid_2_query
        self.refined_sonata_queries = self.refinement_object.refined_sonata_queries

        self.query_tree[query.qid] = get_query_tree(query)
        self.query_out = None

        # print self.qid_2_query, self.query_tree

        # Generate Spark queries for the composed & refined SONATA queries
        self.generate_refined_spark_queries()

        for qid in self.refined_spark_queries:
            print "Processing Refined Queries for cost...", qid
            self.query_cost_transit_fname = 'query_cost_transit_'+str(qid)+'.pickle'
            self.get_transit_query_output(qid)
            dump_data(self.query_out_transit, self.query_cost_transit_fname)
            with open(self.query_cost_transit_fname, 'r') as f:
                self.query_out_transit = pickle.load(f)


    def get_transit_query_output(self, qid):
        """
        Computes per query costs
        :return:
        """
        out0 = self.training_data.collect()
        query_cost_transit = {}
        print "Out0", out0[:2]
        # Iterate over each refined query and collect its output
        # for qid in self.refined_queries:

        query_cost_transit[qid] = {}

        query = self.qid_2_query[qid]
        refinement_key = self.refinement_key
        ref_levels = self.ref_levels

        # Get the query output for each refined intermediate queries
        query_out_refinement_level = self.get_query_output(qid, out0)

        # Get the query cost for each refinement transit, i.e. edge in the refinement graph
        # First get the cost for transit (0,ref_level)
        for ref_level in ref_levels[1:]:
            transit = (0, ref_level)
            query_cost_transit[qid][transit] = {}
            for iter_qid in self.refined_spark_queries[qid][ref_level].keys():
                spark_query = self.refined_spark_queries[qid][ref_level][iter_qid]
                out = query_out_refinement_level[qid][ref_level][iter_qid]
                transit_query_string = 'self.sc.parallelize(out)'
                transit_query_string = generate_query_to_collect_transit_cost(transit_query_string, spark_query)
                query_cost_transit[qid][transit][iter_qid] = eval(transit_query_string)
                #print transit, iter_qid, query_cost_transit[qid][transit][iter_qid][:2]
                #break

        # Then get the cost for transit (ref_level_prev, ref_level_current)
        for ref_level_prev in ref_levels[1:]:
            for ref_level_curr in ref_levels:
                if ref_level_curr > ref_level_prev:
                    transit = (ref_level_prev, ref_level_curr)
                    query_cost_transit[qid][transit] = {}
                    prev_level_out_mapped_string, prev_level_out = generate_query_string_prev_level_out_mapped(qid,
                                                                                           ref_level_prev,
                                                                                           query_out_refinement_level,
                                                                                           self.refined_spark_queries,
                                                                                           out0,
                                                                                           refinement_key)
                    print prev_level_out_mapped_string
                    prev_level_out_mapped = eval(prev_level_out_mapped_string)
                    #print prev_level_out_mapped.collect()[:2]
                    # For each intermediate query for `ref_level_curr` in transit (ref_level_prev, ref_level_current),
                    # we filter out entries that do not satisfy the query at level `ref_level_prev`
                    for iter_qid_curr in self.refined_spark_queries[qid][ref_level_curr].keys():
                        #if iter_qid_curr > 0:
                        curr_level_out = query_out_refinement_level[qid][ref_level_curr][iter_qid_curr]
                        curr_query = self.refined_spark_queries[qid][ref_level_curr][iter_qid_curr]
                        transit_query_string = generate_transit_query(curr_query, curr_level_out,
                                                                      prev_level_out_mapped, ref_level_prev)
                        query_cost_transit[qid][transit][iter_qid_curr] = eval(transit_query_string)
                        #print transit, iter_qid_curr, query_cost_transit[qid][transit][iter_qid_curr][:2]

        self.query_out_transit = query_cost_transit

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
            for n_query in self.query_tree:
                composed_spark_queries = {}
                query_tree = self.query_tree[n_query]
                updated_query_tree = {}
                update_query_tree(query_tree.keys()[0], query_tree, ref_level, updated_query_tree)
                print updated_query_tree

                refinement_key = [self.refinement_key]
                # refinement_key = ['ts', self.refinement_key]

                generate_composed_spark_queries(refinement_key, BASIC_HEADERS, updated_query_tree,
                                                refined_sonata_queries, composed_spark_queries)
                for ref_qid in composed_spark_queries:
                    # print ref_qid, composed_queries[ref_qid].qid
                    if len(composed_spark_queries[ref_qid].operators) > 0:
                        tmp1, _ = generate_intermediate_spark_queries(composed_spark_queries[ref_qid], ref_level, self.target)
                        qid = ref_qid / 10000
                        if qid not in refined_spark_queries:
                            refined_spark_queries[qid] = {}
                        if ref_level not in refined_spark_queries[qid]:
                            refined_spark_queries[qid][ref_level] = {}
                        tmp_query = (spark.PacketStream(qid))
                        tmp_query.basic_headers = BASIC_HEADERS

                        refined_spark_queries[qid][ref_level][0] = tmp_query
                        for iter_qid in tmp1:
                            # print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                            refined_spark_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]

        # print refined_spark_queries
        self.refined_spark_queries = refined_spark_queries

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

        self.query_out_refinement_level = query_out_refinement_level

        return query_out_refinement_level