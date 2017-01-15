#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine.query_generator import *
from query_engine.sonata_queries import *
from utils import *
from pyspark import SparkContext, SparkConf
from netaddr import *
import os
import sys
import numpy as np
import pickle

# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes",
                 "proto", "sMac", "dMac"]

#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine.query_generator import *
from query_engine.sonata_queries import *

# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes",
                 "proto", "sMac", "dMac"]

def parse_log_line(logline):
    return tuple(logline.split(","))

def update_query_tree(root, qt, rl, out):
    #print root, qt
    out[10000*root+rl] = {}
    if len(qt[root]) > 0:
        children = qt[root].keys()
        children.sort()

        lc = children[0]
        #print lc, {lc:qt[root][lc]}
        update_query_tree(lc, {lc:qt[root][lc]}, rl, out[10000*root+rl])
        rc = children[1]
        #print rc, {rc:qt[root][rc]}
        update_query_tree(rc, {rc:qt[root][rc]}, rl, out[10000*root+rl])
    return out


def add_timestamp_key(qid_2_query):
    for qid in qid_2_query:
        query = qid_2_query[qid]
        for operator in query.operators:
            operator.keys = tuple(['ts'] + list(operator.keys))
    return qid_2_query


def get_intermediate_spark_queries(spark_query):
    reduce_operators = filter(lambda s: s in ['Distinct', 'Reduce'], [x.name for x in spark_query.operators])
    spark_intermediate_queries = {}
    prev_qid = 0
    filter_mappings = {}
    filter_mappings[spark_query.qid] = {}
    filters_marked = {}
    for max_reduce_operators in range(1,2+len(reduce_operators)):
        qid = 1000 * spark_query.qid + max_reduce_operators
        tmp_spark_query = (spark.PacketStream(spark_query.qid))
        tmp_spark_query.basic_headers = BASIC_HEADERS
        ctr = 0
        filter_ctr = 0
        for operator in spark_query.operators:
            if operator.name != 'Join':
                if ctr < max_reduce_operators:
                    copy_spark_operators_to_spark(tmp_spark_query, operator)
                else:
                    break
                if operator.name in ['Distinct', 'Reduce']:
                    ctr += 1
                if operator.name == 'Filter':
                    filter_ctr += 1
                    if (spark_query.qid, filter_ctr) not in filters_marked:
                        filters_marked[(spark_query.qid, filter_ctr)] = qid
                        filter_mappings[spark_query.qid][(prev_qid,qid)] = (spark_query.qid, filter_ctr, operator.func[1])
            else:
                copy_spark_operators_to_spark(tmp_spark_query, operator)



        spark_intermediate_queries[qid] = tmp_spark_query
        prev_qid = qid
    return spark_intermediate_queries, filter_mappings


def get_intermediate_queries(sonata_query):
    reduce_operators = filter(lambda s: s in ['Distinct', 'Reduce'], [x.name for x in sonata_query.operators])
    sonata_intermediate_queries = {}
    prev_qid = 0
    filter_mappings = {}
    filters_marked = {}
    for max_reduce_operators in range(1,2+len(reduce_operators)):
        qid = 1000 * sonata_query.qid + max_reduce_operators
        tmp_query = (spark.PacketStream(sonata_query.qid))
        tmp_query.basic_headers = BASIC_HEADERS
        ctr = 0
        filter_ctr = 0
        for operator in sonata_query.operators:
            if operator.name != 'Join':
                if ctr < max_reduce_operators:
                    copy_spark_operators_to_spark(tmp_query, operator)
                else:
                    break
                if operator.name in ['Distinct', 'Reduce']:
                    ctr += 1
                if operator.name == 'Filter':
                    filter_ctr += 1
                    if (sonata_query.qid, filter_ctr) not in filters_marked:
                        filters_marked[(sonata_query.qid, filter_ctr)] = qid
                        filter_mappings[(prev_qid, qid)] = (sonata_query.qid, filter_ctr, operator.func[1])
            else:
                copy_spark_operators_to_spark(tmp_query, operator)



        sonata_intermediate_queries[qid] = tmp_query
        prev_qid = qid
    return sonata_intermediate_queries, filter_mappings

# 10 second window length
T = 10*1000


class QueryTraining(object):

    conf = (SparkConf()
            .setMaster("local[*]")
            .setAppName("SONATA-Training")
            .set("spark.executor.memory","6g")
            .set("spark.driver.memory","20g")
            .set("spark.cores.max","16"))
    sc = SparkContext(conf=conf)
    # Load data
    #baseDir = os.path.join('/home/vagrant/dev/data/sample_data/')
    baseDir = os.path.join('/mnt/')
    #flows_File = os.path.join(baseDir, 'sample_data.csv')
    flows_File = os.path.join(baseDir, 'anon_all_flows_1min.csv')
    ref_levels = range(0, 33, 8)
    # 10 second window length
    window_length = 10*1000

    base_query = spark.PacketStream(0)
    base_query.basic_headers = BASIC_HEADERS

    base_sonata_query = spark.PacketStream(0)
    base_sonata_query.basic_headers = BASIC_HEADERS

    def __init__(self, refined_queries = None, fname_rq_read = '', fname_rq_write = '',
                 query_generator = None, fname_qg = ''):
        self.training_data = (self.sc.textFile(self.flows_File)
                              .map(parse_log_line)
                              # because the data provided has already applied 10 s windowing
                              .map(lambda s:tuple([int(math.ceil(int(s[0])))]+(list(s[2:]))))
                              .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto)=='17')
                              .filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(sPort) == '21')
                              )
        print "Collecting the training data for the first time ..."
        self.training_data = self.sc.parallelize(self.training_data.collect())
        print "Collecting timestamps for the experiment ..."
        self.timestamps = self.training_data.map(lambda s: s[0]).distinct().collect()
        print "Timestamps are: ", self.timestamps
        self.query_out = {}
        self.query_costs = {}
        self.composed_queries = {}
        self.qid_2_updated_filter = {}

        """
        if refined_queries is None:
            if fname_rq_read == '':
                self.process_refined_queries(fname_rq_write)
            else:
                with open(fname_rq_read, 'r') as f:
                    self.refined_queries = pickle.load(f)
        else:
            self.refined_queries = refined_queries

        """

        # Update the query Generator Object (either passed directly, or filename specified)
        if query_generator is None:
            if fname_qg == '':
                fname_qg = 'query_engine/query_dumps/query_generator_object_10.pickle'
            with open(fname_qg,'r') as f:
                query_generator = pickle.load(f)

        self.query_generator = query_generator
        self.max_reduce_operators = self.query_generator.max_reduce_operators
        self.qid_2_query = query_generator.qid_2_query

        print "Generating Refined Queries ..."
        self.process_refined_queries('refined_queries.pickle')

        """
        fname_rq_read = 'refined_queries_10.pickle'
        with open(fname_rq_read, 'r') as f:
            self.refined_queries = pickle.load(f)
        """

        print "Processing Refined Queries with test data..."
        self.get_query_output()

        print "Reformatting output of Refined Queries ..."
        self.get_reformatted_output()

        print "Updating the Cost Matrix ..."
        self.get_query_costs()

        with open('/mnt/query_cost.pickle','w') as f:
            print "Dumping query cost ..."
            pickle.dump(self.query_costs, f)

        print "Success ..."


    def process_refined_queries(self, fname_rq_write):
        # Add timestamp for each key
        self.add_timestamp_key()

        # Update the intermediate query mappings and filter mappings
        self.update_intermediate_queries()

        # Update filters for each SONATA Query
        #self.update_filter()
        #print self.qid_2_query

        # Update the input spark queries
        #self.get_composed_spark_queries()
        #self.update_composed_spark_queries()

        # Generate refined queries
        self.generate_refined_sonata_queries()
        #print self.refined_sonata_queries

        self.update_filter()
        print self.refined_sonata_queries

        self.generate_refined_spark_queries()
        print self.refined_queries

        # Dump refined queries
        self.dump_refined_queries(fname_rq_write)

    def update_composed_spark_queries(self):
        for (qid, spark_query) in self.composed_queries.iteritems():
            new_spark_query = spark.PacketStream(qid)
            new_spark_query.basic_headers = BASIC_HEADERS
            for operator in spark_query.operators:
                if operator.name == "Join":
                    operator.in_stream = 'self.training_data.'
                copy_spark_operators_to_spark(new_spark_query, operator)
            self.composed_queries[qid] = new_spark_query

    def get_composed_spark_queries(self):
        for n_query in self.query_generator.query_trees:
            composed_queries = {}
            query_tree = self.query_generator.query_trees[n_query]
            reduction_key = ['ts', self.query_generator.qid_2_query[query_tree.keys()[0]].reduction_key]
            generate_composed_spark_queries(reduction_key, query_tree,
                                            self.query_generator.qid_2_query,
                                            composed_queries)
            self.composed_queries.update(composed_queries)

    def generate_refined_sonata_queries(self):
        refined_sonata_queries = {}
        qid_2_queries_refined = {}
        # First update the Sonata queries for different levels
        for (qid, sonata_query) in self.qid_2_query.iteritems():
            if qid in self.qid_2_query:
                #print "Exploring Sonata Query", qid
                refined_sonata_queries[qid] = {}
                reduction_key = self.qid_2_query[qid].reduction_key
                #print "Reduction Key:", reduction_key

                for ref_level in self.ref_levels[1:]:

                    #print "Refinement Level", ref_level
                    refined_sonata_queries[qid][ref_level] = {}
                    refined_query_id = 10000*qid+ref_level
                    refined_sonata_query = PacketStream(refined_query_id)
                    refined_sonata_query.basic_headers = BASIC_HEADERS

                    refined_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))
                    for operator in sonata_query.operators:
                        if operator.name == 'Join':
                            operator.in_stream = 'self.training_data.'
                        copy_spark_operators_to_spark(refined_sonata_query, operator)

                    qid_2_queries_refined[refined_query_id] = refined_sonata_query

                    tmp1, _ = get_intermediate_queries(refined_sonata_query)

                    #refined_queries[qid][ref_level][0] = self.base_sonata_query
                    for iter_qid in tmp1:
                        #print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                        refined_sonata_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]
        self.qid_2_queries_refined = qid_2_queries_refined
        self.refined_sonata_queries = refined_sonata_queries

    def generate_refined_spark_queries(self):
        refined_spark_queries = {}
        qid_2_queries_refined = {}
        for qid in self.refined_sonata_queries:
            for ref_level in self.refined_sonata_queries[qid]:
                ref_qid = 10000*qid+ref_level
                tmp = self.refined_sonata_queries[qid][ref_level].keys()
                tmp.sort()
                final_iter_qid = tmp[-1]

                qid_2_queries_refined[ref_qid] = self.refined_sonata_queries[qid][ref_level][final_iter_qid]

        # Use the processed Sonata queries to generated refined+composed Spark queries
        for ref_level in self.ref_levels[1:]:
            for n_query in self.query_generator.query_trees:
                composed_queries = {}
                query_tree = self.query_generator.query_trees[n_query]
                updated_query_tree = {}
                update_query_tree(query_tree.keys()[0], query_tree, ref_level, updated_query_tree)
                #print updated_query_tree
                reduction_key = ['ts', self.query_generator.qid_2_query[query_tree.keys()[0]].reduction_key]

                generate_composed_spark_queries(reduction_key, BASIC_HEADERS, updated_query_tree,
                                                qid_2_queries_refined, composed_queries)
                for ref_qid in composed_queries:
                    #print ref_qid, composed_queries[ref_qid].qid
                    if len(composed_queries[ref_qid].operators) > 0:
                        tmp1, _ = get_intermediate_spark_queries(composed_queries[ref_qid])
                        qid = ref_qid/10000
                        if qid not in refined_spark_queries:
                            refined_spark_queries[qid] = {}
                        if ref_level not in refined_spark_queries[qid]:
                            refined_spark_queries[qid][ref_level] = {}
                        for iter_qid in tmp1:
                            #print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                            refined_spark_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]

                #print composed_queries
                self.composed_queries.update(composed_queries)
        #print refined_spark_queries
        self.refined_queries = refined_spark_queries

    def update_filter(self):
        sonata_queries = {}
        for ref_level in self.ref_levels[1:]:
            print "Refinement Level", ref_level
            for (prev_qid, curr_qid) in self.filter_mappings:
                prev_ref_qid = 1000*(10000*(prev_qid/1000)+ref_level)+(prev_qid%1000)
                curr_ref_qid = 1000*(10000*(curr_qid/1000)+ref_level)+(curr_qid%1000)
                curr_ref_qids = filter(lambda x: x >=curr_ref_qid,
                                       self.refined_sonata_queries[curr_qid/1000][ref_level].keys())
                print prev_qid, curr_qid, prev_ref_qid, curr_ref_qid, self.refined_sonata_queries.keys()
                prev_sonata_query = self.refined_sonata_queries[prev_qid/1000][ref_level][prev_ref_qid]
                curr_sonata_query = self.refined_sonata_queries[curr_qid/1000][ref_level][curr_ref_qid]

                # Get the Spark queries corresponding to the prev and curr sonata queries
                if prev_ref_qid not in sonata_queries:
                    prev_spark_query = spark.PacketStream(prev_ref_qid)
                    prev_spark_query.basic_headers = BASIC_HEADERS
                    for operator in prev_sonata_query.operators:
                        copy_sonata_operators_to_spark(prev_spark_query, operator)

                    sonata_queries[prev_ref_qid] = prev_spark_query
                else:
                    prev_spark_query = sonata_queries[prev_ref_qid]


                if curr_ref_qid not in sonata_queries:
                    curr_spark_query = spark.PacketStream(curr_ref_qid)
                    curr_spark_query.basic_headers = BASIC_HEADERS
                    for operator in curr_sonata_query.operators:
                        copy_sonata_operators_to_spark(curr_spark_query, operator)

                    sonata_queries[curr_ref_qid] = curr_spark_query
                else:
                    curr_spark_query = sonata_queries[curr_ref_qid]



                _, filter_id, spread = self.filter_mappings[(prev_qid, curr_qid)]
                #print "Update Computed for result of query", prev_sonata_query
                #thresh = -1
                thresh = self.get_thresh(prev_spark_query, spread)

                # Update the intermediate Spark Query
                filter_ctr = 1
                for operator in curr_spark_query.operators:
                    if operator.name == 'Filter':
                        if filter_ctr == filter_id:
                            #print "Before: ", curr_qid, operator
                            operator.func = ('geq',thresh)
                            print "Updated threshold for Intermediate Query", curr_qid, operator
                            break
                        else:
                            filter_ctr += 1
                sonata_queries[curr_ref_qid] = copy.deepcopy(curr_spark_query)

                # Update the Sonata Query
                for tmp_qid in curr_ref_qids:
                    filter_ctr = 1
                    son_query = self.refined_sonata_queries[curr_qid/1000][ref_level][tmp_qid]
                    for operator in son_query.operators:
                        if operator.name == 'Filter':
                            if filter_ctr == filter_id:
                                operator.func = ('geq',thresh)
                                print "Updated threshold for ", curr_ref_qid, operator
                                break
                            else:
                                filter_ctr += 1
                self.refined_sonata_queries[curr_qid/1000][ref_level][curr_ref_qid] = copy.deepcopy(curr_sonata_query)
                #print "##Curr SONATA", curr_sonata_query
                #print "$$Curr Spark", curr_spark_query

    def update_intermediate_queries(self):
        spark_intermediate_queries = {}
        filter_mappings = {}
        for (qid, sonata_query) in self.qid_2_query.iteritems():
            print qid, sonata_query
            # Initialize Spark Query
            tmp1, tmp2 = get_intermediate_queries(sonata_query)
            spark_intermediate_queries.update(tmp1)
            filter_mappings.update(tmp2)
            #break
        print spark_intermediate_queries.keys(), filter_mappings
        self.filter_mappings = filter_mappings
        self.spark_intermediate_queries = spark_intermediate_queries

    def add_timestamp_key(self):
        def add_timestamp_to_query(q):
            # This function will be useful if we need to add ts in recursion
            for operator in q.operators:
                operator.keys = tuple(['ts'] + list(operator.keys))

        for qid in self.qid_2_query:
            query = self.qid_2_query[qid]
            add_timestamp_to_query(query)


    def get_thresh(self, spark_query, spread):
        query_string = 'self.training_data.'+spark_query.compile()+'.map(lambda s: s[1]).collect()'
        #print query_string
        data = [float(x) for x in (eval(query_string))]
        thresh = 0.0
        if len(data) > 0:
            thresh = np.percentile(data, int(spread))
            print "Mean", np.mean(data), "Median", np.median(data), "75 %", np.percentile(data,75), \
                "95 %", np.percentile(data,95), "99 %", np.percentile(data,99)
        print "Thresh:", thresh
        return thresh

    def get_stdev(self, spark_query):
        query_string = 'self.training_data.'+spark_query.compile()+'.map(lambda s: s[1]).stdev()'
        print query_string
        stdev = eval(query_string)
        print "Stdev:", stdev
        return stdev

    def dump_refined_queries(self, fname_rq_write):
        with open(fname_rq_write,'w') as f:
            print "Dumping refined Queries ..."
            pickle.dump(self.refined_queries, f)

    def get_query_output(self):
        out0 = self.training_data.collect()
        print "Out0", len(out0)
        # Iterate over each refined query and collect its output
        query_out = {}
        for qid in self.refined_queries:
            query_out[qid] = {}
            for ref_level in self.refined_queries[qid]:
                query_out[qid][ref_level] = {}
                for iter_qid in self.refined_queries[qid][ref_level]:
                    if iter_qid > 0:
                        spark_query = self.refined_queries[qid][ref_level][iter_qid]
                        if len(spark_query.compile()) > 0:
                            query_string = 'self.training_data.'+spark_query.compile()+'.collect()'
                            print("Processing Query", qid, "refinement level", ref_level, "iteration id", iter_qid)
                            print query_string
                            out = eval(query_string)
                        else:
                            print "No query to process for", qid, "refinement level", ref_level, "iteration id", iter_qid
                            out = []

                        query_out[qid][ref_level][iter_qid] = out
                        print len(query_out[qid][ref_level][iter_qid])

                query_out[qid][ref_level][0] = out0

        self.query_out = query_out

    # noinspection PyShadowingNames
    def get_reformatted_output(self):
        query_output = self.query_out
        query_output_reformatted = {}
        for ts in self.timestamps:
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
                                #print entry
                                if type(entry[0]) == type(1):
                                    entry = (entry,1)
                                ts_tmp = entry[0][0]
                                if ts_tmp == ts:
                                    k = tuple(entry[0][1:])
                                    v = entry[1]
                                    query_output_reformatted[ts][qid][ref_level][iter_qid][k] = v

                    print ts, qid, ref_level, query_output_reformatted[ts][qid][ref_level].keys()

        self.query_output_reformatted = query_output_reformatted

    def get_diff_buckets(self, prev_out, curr_out, ref_level_prev, curr_query, reduction_key):
        if len(curr_query.operators) > 0:
            keys = curr_query.operators[-1].keys[1:]
        else:
            keys = BASIC_HEADERS[1:]

        #print "Curr Out: ", len(curr_out.keys()), curr_out.keys()[0]
        prev_key_mapped = self.sc.parallelize(prev_out.keys()).map(lambda s: (s[0],1))
        if len(keys) > 1:
            map_string = 'self.sc.parallelize(curr_out.keys()).map(lambda ('+",".join(keys)+'): '+str(reduction_key)+').map(lambda dIP: (str(IPNetwork(str(dIP)+"/"+str('+str(ref_level_prev)+')).network),1)).join(prev_key_mapped).map(lambda x: x[0]).collect()'
        else:
            map_string = 'self.sc.parallelize(curr_out.keys()).map(lambda s: s[0]).map(lambda ('+",".join(keys)+'): '+str(reduction_key)+').map(lambda dIP: (str(IPNetwork(str(dIP)+"/"+str('+str(ref_level_prev)+')).network),1)).join(prev_key_mapped).map(lambda x: x[0]).collect()'
        #print map_string
        diff_entries= dict((x,1) for x in eval(map_string))
        return diff_entries


    def get_query_costs(self):
        query_output_reformatted = self.query_output_reformatted
        query_costs = {}

        # Hierarchy
        # ts
        #   -> query
        #        -> partition_plan
        #

        for ts in query_output_reformatted:
            query_costs[ts] = {}
            for qid in query_output_reformatted[ts]:

                query_costs[ts][qid] = {}
                query = self.qid_2_query[qid]
                reduction_key = query.reduction_key

                partition_plans = query.get_partition_plans()
                #print partition_plans
                ref_levels = self.ref_levels
                diff_counts = {}
                for partition_plan in partition_plans[qid]:
                    #print partition_plan
                    for ref_level_prev in ref_levels:
                        for ref_level_curr in ref_levels:
                            if ref_level_curr > ref_level_prev:
                                if ref_level_prev > 0:
                                    transit = (ref_level_prev, ref_level_curr)
                                    iter_qids_prev = query_output_reformatted[ts][qid][ref_level_prev].keys()
                                    iter_qids_curr = query_output_reformatted[ts][qid][ref_level_curr].keys()
                                    iter_qids_prev.sort()
                                    iter_qids_curr.sort()

                                    print ts, qid, transit, iter_qids_prev, iter_qids_curr
                                    #break
                                    # output of the previous level helps us filter out crap from curr level
                                    prev_out = query_output_reformatted[ts][qid][ref_level_prev][iter_qids_prev[-1]]

                                    bucket_count = 0
                                    packet_count = 0
                                    # Maximum number of packets that we will send to stream processor if all
                                    # reduce operations are done at the stream processor. Note that we have implemented that
                                    # for such cases filtering will still be done in the data plane, that's why we only
                                    # count the difference (filtered packet tuples) and not the total
                                    if (ref_level_prev, ref_level_curr, 0) not in diff_counts:
                                        curr_in = query_output_reformatted[ts][qid][ref_level_curr][0]
                                        in_query = self.base_query
                                        prev_bucket_count = len(self.get_diff_buckets(prev_out, curr_in, ref_level_prev, in_query, reduction_key).keys())
                                        diff_counts[(ref_level_prev, ref_level_curr, 0)] = prev_bucket_count
                                    else:
                                        prev_bucket_count = diff_counts[(ref_level_prev, ref_level_curr, 0)]

                                    ctr = 1
                                    #print ts, qid, ref_level_curr, query_output_reformatted[ts][qid][ref_level_curr].keys()
                                    for elem in str(partition_plan):
                                        curr_out = query_output_reformatted[ts][qid][ref_level_curr][iter_qids_curr[ctr]]

                                        # To get the keys that we need to discard we need to know what entries are
                                        # common between the output of prev level and keys in the current bucket
                                        # For that we need to get a sense of position of reduction key
                                        if (ref_level_prev, ref_level_curr, ctr) not in diff_counts:
                                            curr_query = self.refined_queries[qid][ref_level_curr][iter_qids_curr[ctr]]
                                            print curr_query
                                            diff_entries = self.get_diff_buckets(prev_out, curr_out, ref_level_prev, curr_query, reduction_key)
                                            diff_entries_count = len(diff_entries.keys())
                                            diff_counts[(ref_level_prev, ref_level_curr, ctr)] = diff_entries_count
                                        else:
                                            diff_entries_count = diff_counts[(ref_level_prev, ref_level_curr, ctr)]


                                        if elem == '0':
                                            # This reduce operators is executed in the data plane, thus we need
                                            # to count the buckets required for this operator
                                            bucket_count += diff_entries_count
                                            prev_bucket_count = diff_entries_count
                                        else:
                                            # This one goes to the stream processor, so the bucket for the
                                            # previous operators is equal to the number of packets sent
                                            # to the stream processor
                                            packet_count = prev_bucket_count
                                            break

                                    if packet_count == 0:
                                        # Case when all reduce operators are executed in the data plane
                                        packet_count = len(query_output_reformatted[ts][qid][ref_level_curr][iter_qids_curr[-1]].keys())
                                    #print ts, qid, partition_plan, transit, bucket_count, packet_count
                                    query_costs[ts][qid][partition_plan, transit] = (bucket_count, packet_count)
                                else:
                                    # No need to do any diff for this case
                                    transit = (ref_level_prev, ref_level_curr)
                                    iter_qids_prev = []
                                    iter_qids_curr = query_output_reformatted[ts][qid][ref_level_curr].keys()
                                    iter_qids_prev.sort()
                                    iter_qids_curr.sort()

                                    print ts, qid, transit, iter_qids_prev, iter_qids_curr

                                    bucket_count = 0
                                    packet_count = 0

                                    if (ref_level_prev, ref_level_curr, 0) not in diff_counts:
                                        curr_in = query_output_reformatted[ts][qid][ref_level_curr][0]
                                        prev_bucket_count = len(curr_in.keys())
                                        # No diff required
                                        diff_counts[(ref_level_prev, ref_level_curr, 0)] = prev_bucket_count
                                    else:
                                        prev_bucket_count = diff_counts[(ref_level_prev, ref_level_curr, 0)]

                                    ctr = 1
                                    #print ts, qid, ref_level_curr, query_output_reformatted[ts][qid][ref_level_curr].keys()
                                    for elem in str(partition_plan):
                                        curr_out = query_output_reformatted[ts][qid][ref_level_curr][iter_qids_curr[ctr]]

                                        # To get the keys that we need to discard we need to know what entries are
                                        # common between the output of prev level and keys in the current bucket
                                        # For that we need to get a sense of position of reduction key
                                        if (ref_level_prev, ref_level_curr, ctr) not in diff_counts:
                                            curr_query = self.refined_queries[qid][ref_level_curr][iter_qids_curr[ctr]]
                                            #print curr_query
                                            diff_entries = curr_out
                                            diff_entries_count = len(diff_entries.keys())
                                            diff_counts[(ref_level_prev, ref_level_curr, ctr)] = diff_entries_count
                                        else:
                                            diff_entries_count = diff_counts[(ref_level_prev, ref_level_curr, ctr)]


                                        if elem == '0':
                                            # This reduce operators is executed in the data plane, thus we need
                                            # to count the buckets required for this operator
                                            bucket_count += diff_entries_count
                                            prev_bucket_count = diff_entries_count
                                        else:
                                            # This one goes to the stream processor, so the bucket for the
                                            # previous operators is equal to the number of packets sent
                                            # to the stream processor
                                            packet_count = prev_bucket_count
                                            break

                                    if packet_count == 0:
                                        # Case when all reduce operators are executed in the data plane
                                        packet_count = len(query_output_reformatted[ts][qid][ref_level_curr][iter_qids_curr[-1]].keys())
                                    #print ts, qid, partition_plan, transit, bucket_count, packet_count
                                    query_costs[ts][qid][partition_plan, transit] = (bucket_count, packet_count)

        self.query_costs = query_costs

    def test_spark_query(self):
        test = (self.training_data
                .map(lambda ((ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac)): ((ts,sIP,sPort,str(IPNetwork(str(str(dIP)+"/8")).network),dPort,nBytes,proto,sMac,dMac)))
                #.filter(lambda s: str(s[6])=='17')
                .map(lambda ((ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac)): (ts,dIP,dPort))
                #.reduceByKey(lambda x,y: x+y)
                #.filter(lambda s: s[1] > 2)
                #.map(lambda x: x[0])
                .distinct()
                )
        """
        distinct_ts = test.map(lambda s: s[0]).distinct().count()
        distinct_sIP = test.map(lambda s: s[1]).distinct().count()
        distinct_sport = test.map(lambda s: s[2]).distinct().count()
        distinct_dip = test.map(lambda s: s[3]).distinct().count()
        distinct_dport = test.map(lambda s: s[4]).distinct().count()
        distinct_nBytes = test.map(lambda s: s[5]).distinct().count()
        distinct_proto = test.map(lambda s: s[6]).distinct().count()
        distinct_sMac = test.map(lambda s: s[7]).distinct().count()
        distinct_dMac = test.map(lambda s: s[8]).distinct().count()
        print ("ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac")
        print (distinct_ts, distinct_sIP, distinct_sport, distinct_dip, distinct_dport,distinct_nBytes,distinct_proto,distinct_sMac,distinct_dMac)
        """



if __name__ == "__main__":

    #fname_rq_read = 'query_engine/query_dumps/refined_queries_1.pickle'
    qt = QueryTraining()
    #qt.test_spark_query()
    """

    with open('query_engine/query_dumps/query_generator_object_1.pickle', 'r') as f:
        qg = pickle.load(f)
        print qg.qid_2_query.keys()
        for n_query in qg.query_trees:
            print n_query, qg.query_trees[n_query]

    with open('refined_queries_10.pickle','r') as f:
        rq = pickle.load(f)
        #q = rq[22][8][220008001]
        #print q.compile()
        #print q.compile()
        #print rq.keys()



    fname_rq_read = 'query_engine/query_dumps/refined_queries_1.pickle'
    qt = QueryTraining(fname_rq_read=fname_rq_read)
    qt.get_reformatted_output()
    print qt.refined_queries
    #qt.get_query_output()



    with open('query_out.pickle','r') as f:
        qt.query_out = pickle.load(f)



    #query_output = qt.query_out
    qt.get_reformatted_output()
    #qt.get_query_costs()
    #print qt.query_costs

    #qt.get_query_output()
    #print qt.query_out
    """


    """
    print qt.refined_queries
    qt.get_query_output()
    qout = qt.query_out
    #qt.test_spark_query()


    with open('query_out.pickle','w') as f:
        print "Dumping query out ...", sys.getsizeof(qout)
        pickle.dump(qout, f)


    print "Loading Query Out ..."
    with open('query_out.pickle','r') as f:
        qt.query_out = pickle.load(f)

    #print qt.query_out
    qt.get_reformatted_output()
    qt.get_query_costs()

    with open('query_cost.pickle','w') as f:
        print "Dumping query cost ..."
        pickle.dump(qt.query_costs, f)
    """










