#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle

import numpy as np
from netaddr import *
from pyspark import SparkContext, SparkConf
from query_engine.query_generator import *

from sonata.query_engine.sonata_queries import *
from utils import *

#import tinys3



DURATION_TYPE = "1min"
N_QUERIES = "2"
BASE_PATH = "data/use_case_5/"
OUTPUT_COST_DIR = BASE_PATH +'query_cost_queries_case5_'+DURATION_TYPE+'_'+N_QUERIES+'_aws'
S3_ACCESS_KEY = "AKIAJZZYOKOOZNK2Z2GQ"
S3_SECRET_KEY = "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"
CASE_NUMBER = "_CASE5_"

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

# 1 second window length
T = 1

class QueryTraining(object):

    conf = (SparkConf()
            #.setMaster("local[*]")
            #.setMaster("")
            .setAppName("SONATA-Training"))
    #.set("spark.executor.memory","6g")
    #.set("spark.driver.memory","20g"))
    #.set("spark.cores.max","16"))

    sc = SparkContext(conf=conf)
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )
    # Load data
    #baseDir = os.path.join('/home/vagrant/dev/data/sample_data/')
    baseDir = os.path.join('/mnt/')
    #flows_File = os.path.join(baseDir, 'sample_data.csv')
    flows_File = os.path.join(baseDir, 'anon_all_flows_1min.csv')
    aws_File = "s3://sonatasdx/data/anon_all_flows_1min.csv/"
    ref_levels = range(0, 33, 4)
    # 10 second window length
    window_length = 1*1000

    base_query = spark.PacketStream(0)
    base_query.basic_headers = BASIC_HEADERS

    base_sonata_query = spark.PacketStream(0)
    base_sonata_query.basic_headers = BASIC_HEADERS

    def __init__(self, refined_queries = None, fname_rq_read = '', fname_rq_write = '',
                 query_generator = None, fname_qg = ''):

        self.training_data = (self.sc.textFile(self.flows_File)
                              .map(parse_log_line)
                              # because the data provided has already applied 10 s windowing
                              .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[1:]))))
                              #.filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(proto)=='17')
                              #.filter(lambda (ts,sIP,sPort,dIP,dPort,nBytes,proto,sMac,dMac): str(sPort) == '53')
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
        self.query_costs_diff = {}
        self.worst_case_queries = {}
        self.has_write_to_s3 = False

        # Update the query Generator Object (either passed directly, or filename specified)
        if query_generator is None:
            if fname_qg == '':
                fname_qg = BASE_PATH + 'query_generator_object_case5_'+N_QUERIES+'.pickle'
                self.write_to_s3(fname_qg)
            with open(fname_qg,'r') as f:
                query_generator = pickle.load(f)

        self.query_generator = query_generator
        self.max_reduce_operators = self.query_generator.max_reduce_operators
        self.qid_2_query = query_generator.qid_2_query

        REFINED_QUERY_PATH = BASE_PATH+'refined_queries_queries_case5_'+DURATION_TYPE+'_'+N_QUERIES+'_1min_aws.pickle'
        print "Generating Refined Queries ..."
        self.process_refined_queries(REFINED_QUERY_PATH)
        print self.refined_queries

        self.write_to_s3(REFINED_QUERY_PATH)

        """

        fname_rq_read = 'data/refined_queries_queries_case5_100_1min_aws.pickle'
        with open(fname_rq_read, 'r') as f:
            self.refined_queries = pickle.load(f)
        """

        for qid in self.refined_queries:
            print "Processing Refined Queries for cost...", qid
            self.get_query_output_less_memory(qid)

        print "Success ..."


    def process_refined_queries(self, fname_rq_write):
        # Add timestamp for each key
        self.add_timestamp_key()

        # Update the intermediate query mappings and filter mappings
        self.update_intermediate_queries()

        # Generate refined queries
        self.generate_refined_sonata_queries()

        print self.refined_sonata_queries

        self.update_filter()

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
            print "Refinement Level", ref_level, self.filter_mappings
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

    def get_query_output_for_worst_case(self):
        worst_cost = {}

        for qid in self.worst_case_queries:
            sonata_query = self.worst_case_queries[qid]
            spark_query = spark.PacketStream(qid)
            spark_query.basic_headers = BASIC_HEADERS

            for operator in sonata_query.operators:
                copy_sonata_operators_to_spark(spark_query, operator)
            query_string = 'self.training_data.'+spark_query.compile()+'.map(lambda s: (s[0][0],1)).reduceByKey(lambda x,y: x+y).collect()'
            out = eval(query_string)
            worst_cost[qid] = out
            print "qid", qid, out

        worst_case_output = OUTPUT_COST_DIR + "/q_worst_cost" + CASE_NUMBER + DURATION_TYPE +".pickle"
        with open(worst_case_output,'w') as f:
            print "Dumping refined Queries ..."
            pickle.dump(worst_cost, f)

        self.write_to_s3(worst_case_output)

    def get_query_output_less_memory(self, qid):
        """
        Computes per query costs
        :return:
        """
        out0 = self.training_data.collect()
        query_costs = {}
        print "Out0", len(out0)
        # Iterate over each refined query and collect its output
        #for qid in self.refined_queries:

        query_costs[qid] = {}
        query_out = {}
        query_out[qid] = {}
        for ref_level in self.refined_queries[qid]:
            query_out[qid][ref_level] = {}
            for iter_qid in self.refined_queries[qid][ref_level]:
                if iter_qid > 0:
                    spark_query = self.refined_queries[qid][ref_level][iter_qid]
                    if len(spark_query.compile()) > 0:
                        query_string = 'self.training_data.'+spark_query.compile()+'.collect()'
                        print("Processing Query", qid, "refinement level", ref_level, "iteration id", iter_qid)
                        #print query_string
                        out = eval(query_string)
                    else:
                        print "No query to process for", qid, "refinement level", ref_level, "iteration id", iter_qid
                        out = []

                    query_out[qid][ref_level][iter_qid] = out
                    print len(query_out[qid][ref_level][iter_qid])

            query_out[qid][ref_level][0] = out0

        query_output_reformatted = {}
        query_costs_diff = {}

        print "Reformatting output of Refined Queries ...", qid
        query_output_reformatted[qid] = self.get_reformatted_output_without_ts(qid, query_out[qid])

        print "Updating the Diff Entries ...", qid
        query_costs_diff[qid] = self.get_query_diff_entries_without_ts(qid, query_output_reformatted)

        qid_diff_output = OUTPUT_COST_DIR + '/q_diff_' + str(DURATION_TYPE) + '_' + str(qid) + '.pickle'
        with open(qid_diff_output,'w') as f:
            print "Dumping query cost ..." + qid_diff_output
            pickle.dump(query_costs_diff[qid], f)

        self.write_to_s3(qid_diff_output)


        print "Updating the Cost Metrics ...", qid
        query_costs[qid] = self.get_query_cost_only(qid, query_output_reformatted, query_costs_diff)

        qid_cost_output = OUTPUT_COST_DIR + '/q_cost_' + str(DURATION_TYPE) + '_' + str(qid) + '.pickle'
        with open(qid_cost_output,'w') as f:
            print "Dumping query cost ..." + qid_cost_output
            pickle.dump(query_costs[qid], f)

        self.write_to_s3(qid_cost_output)

        query_output_reformatted = {}
        query_costs_diff = {}

    def write_to_s3(self, path):
        # write to S3 bucket
        if self.has_write_to_s3:
            conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,tls=True)
            f = open(path,'r')
            conn.upload(path,f,'sonataresultsnew')
            f.close()

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
                            entry = (entry,1)

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
        diff_entries= dict((x[0],x[1]) for x in eval(eval_string))

        return diff_entries

    def get_diff_buckets(self, prev_out, curr_out, ref_level_prev, curr_query, reduction_key):
        if len(curr_query.operators) > 0:
            keys = curr_query.operators[-1].keys
        else:
            keys = BASIC_HEADERS

        prev_key_mapped = self.sc.parallelize(prev_out.keys()).map(lambda s: (s,1))
        if len(keys) > 1:
            map_string = 'self.sc.parallelize(curr_out.keys()).map(lambda ('+",".join(keys)+'): (ts,'+str(reduction_key)+')).map(lambda (ts, dIP): ((ts, str(IPNetwork(str(dIP)+"/"+str('+str(ref_level_prev)+')).network)),1)).join(prev_key_mapped).map(lambda x: (x[0][0],1)).reduceByKey(lambda x,y: x+y).collect()'
        else:
            map_string = 'self.sc.parallelize(curr_out.keys()).map(lambda s: (s[0],s[1])).map(lambda ('+",".join(keys)+'): (ts, '+str(reduction_key)+')).map(lambda (ts, dIP): ((ts, str(IPNetwork(str(dIP)+"/"+str('+str(ref_level_prev)+')).network)),1)).join(prev_key_mapped).map(lambda x: (x[0][0],1)).reduceByKey(lambda x,y: x+y).collect()'

        diff_entries= dict((x[0],x[1]) for x in eval(map_string))

        return diff_entries

    def get_query_cost_only(self, qid, query_output_reformatted, query_costs_diff):

        query_costs = {}
        query = self.qid_2_query[qid]
        ref_levels = self.ref_levels
        partition_plans = query.get_partition_plans()

        for partition_plan in partition_plans[qid]:
            for ref_level_prev in ref_levels:
                for ref_level_curr in ref_levels:
                    if ref_level_curr > ref_level_prev:
                        transit = (ref_level_prev, ref_level_curr)
                        time_stamps = query_costs_diff[qid][((0,32), 0)].keys()
                        iter_qids_curr = query_output_reformatted[qid][ref_level_curr].keys()
                        iter_qids_curr.sort()

                        assert query_costs_diff[qid][((0,32), 0)] == query_costs_diff[qid][((0,8), 0)]

                        query_costs[partition_plan, transit] = {}

                        for ts in time_stamps:
                            query_costs[partition_plan, transit][ts] = (0,0)

                            if ts in query_costs_diff[qid][(transit, 0)]:

                                bucket_count = 0
                                packet_count = 0
                                ctr = 0
                                # Number of packets coming in for this query
                                prev_bucket_count = query_costs_diff[qid][(transit, iter_qids_curr[ctr])][ts]

                                ctr = 1
                                for elem in str(partition_plan):
                                    if ts in query_costs_diff[qid][(transit, iter_qids_curr[ctr])]:
                                        diff_entries_count = query_costs_diff[qid][(transit, iter_qids_curr[ctr])][ts]
                                        if elem == '0':
                                            # This reduce operators is executed in the data plane, thus we need
                                            # to count the buckets required for this operator
                                            bucket_count += diff_entries_count
                                            # Number of packets input to next set of reduce operations
                                            prev_bucket_count = diff_entries_count
                                        else:
                                            # This one goes to the stream processor, so the bucket for the
                                            # previous operators is equal to the number of packets sent
                                            # to the stream processor
                                            packet_count = prev_bucket_count
                                            break

                                        if packet_count == 0:
                                            # Case when all reduce operators are executed in the data plane
                                            if ts not in query_costs_diff[qid][(transit,iter_qids_curr[-1])]:
                                                print qid, (transit,iter_qids_curr[-1]), query_costs_diff[qid][(transit,iter_qids_curr[-1])]
                                                packet_count = 0
                                            else:
                                                packet_count = query_costs_diff[qid][(transit,iter_qids_curr[-1])][ts]
                                        ctr += 1

                                #print ts, "Part Plan", partition_plan, " transit", transit, "bucket cost", \
                                #    bucket_count, "Packet cost", packet_count
                                query_costs[partition_plan, transit][ts] = (bucket_count, packet_count)
        return query_costs

    def get_query_diff_entries_without_ts(self, qid, query_output_reformatted):

        query_costs_diff = {}
        query = self.qid_2_query[qid]
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

                        print qid, transit, iter_qids_prev, iter_qids_curr
                        prev_out_final_query = query_output_reformatted[qid][ref_level_prev][iter_qids_prev[-1]]

                        if (ref_level_prev, ref_level_curr, 0) not in diff_counts:
                            out_zero_for_ctr_0 = query_output_reformatted[qid][ref_level_curr][0]
                            in_query = self.base_query
                            prev_bucket_count = self.get_diff_buckets(prev_out_final_query, out_zero_for_ctr_0, ref_level_prev, in_query, reduction_key)
                            diff_counts[(ref_level_prev, ref_level_curr, 0)] = prev_bucket_count
                            query_costs_diff[(transit,0)] = diff_counts[(ref_level_prev, ref_level_curr, 0)]

                        for ctr in range(1, len(iter_qids_curr)):
                            print qid, transit, iter_qids_prev, iter_qids_curr[ctr]

                            curr_out = query_output_reformatted[qid][ref_level_curr][iter_qids_curr[ctr]]
                            if (ref_level_prev, ref_level_curr, ctr) not in diff_counts:

                                curr_query = self.refined_queries[qid][ref_level_curr][iter_qids_curr[ctr]]
                                diff_entries = self.get_diff_buckets(prev_out_final_query, curr_out, ref_level_prev, curr_query, reduction_key)
                                diff_counts[(ref_level_prev, ref_level_curr, ctr)] = diff_entries

                            query_costs_diff[(transit,iter_qids_curr[ctr])] = diff_counts[(ref_level_prev, ref_level_curr, ctr)]
                            #print qid, transit, iter_qids_prev, iter_qids_curr[ctr], query_costs_diff[(transit,iter_qids_curr[ctr])].values()[0]
                    else:
                        # No need to do any diff for this case
                        transit = (ref_level_prev, ref_level_curr)
                        iter_qids_prev = []
                        iter_qids_curr = query_output_reformatted[qid][ref_level_curr].keys()
                        iter_qids_prev.sort()
                        iter_qids_curr.sort()

                        print qid, transit, iter_qids_prev, iter_qids_curr

                        for ctr in range(len(iter_qids_curr)):

                            curr_out = query_output_reformatted[qid][ref_level_curr][iter_qids_curr[ctr]]

                            if (ref_level_prev, ref_level_curr, ctr) not in diff_counts:
                                diff_entries = self.get_per_timestamp_counts(curr_out.keys())
                                diff_counts[(ref_level_prev, ref_level_curr, ctr)] = diff_entries
                            else:
                                print "This should not happen"

                            query_costs_diff[(transit,iter_qids_curr[ctr])] = diff_counts[(ref_level_prev, ref_level_curr, ctr)]
                            #print qid, transit, iter_qids_prev, iter_qids_curr[ctr], query_costs_diff[(transit,iter_qids_curr[ctr])].values()[0]
                            #print "Test", ctr, len(curr_out.keys()), transit, iter_qids_curr[ctr], diff_counts[(ref_level_prev, ref_level_curr, ctr)]
        return query_costs_diff




if __name__ == "__main__":

    #qid = sys.argv[1]

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










