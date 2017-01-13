#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine.query_generator import *
from query_engine.sonata_queries import *
from utils import *
from pyspark import SparkContext
from netaddr import *
import os
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


def add_timestamp_key(qid_2_query):
    for qid in qid_2_query:
        query = qid_2_query[qid]
        print qid
        print "Before:", query
        for operator in query.operators:
            operator.keys = tuple(['ts'] + list(operator.keys))
        print "After:", query
    return qid_2_query


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


# noinspection PyShadowingNames







T = 10000
class QueryTraining(object):
    sc = SparkContext(appName="SONATA-Training")
    # Load data
    baseDir = os.path.join('/home/vagrant/dev/data/sample_data/')
    flows_File = os.path.join(baseDir, 'sample_data.csv')
    ref_levels = range(0, 33, 16)
    # 10 second window length
    window_length = 10*1000

    base_query = PacketStream(0)
    base_query.basic_headers = BASIC_HEADERS

    def __init__(self, refined_queries = None, fname_rq_read = '', fname_rq_write = '',
                 query_generator = None, fname_qg = ''):
        self.training_data = (self.sc.textFile(self.flows_File)
                              .map(parse_log_line)
                              .map(lambda s:tuple([int(math.ceil(int(s[0])/T))]+(list(s[2:]))))
                              .cache())
        self.query_out = {}
        self.query_costs = {}

        if refined_queries is None:
            if fname_rq_read == '':
                self.process_refined_queries(query_generator, fname_qg, fname_rq_write)
            else:
                with open(fname_rq_read, 'r') as f:
                    self.refined_queries = pickle.load(f)
        else:
            self.refined_queries = refined_queries

        # Update the query Generator Object (either passed directly, or filename specified)
        if query_generator is None:
            if fname_qg == '':
                fname_qg = 'query_engine/query_dumps/query_generator_object_1.pickle'
            with open(fname_qg,'r') as f:
                query_generator = pickle.load(f)

        self.query_generator = query_generator
        self.max_reduce_operators = self.query_generator.max_reduce_operators
        self.qid_2_sonata_query = query_generator.qid_2_query

    def get_query_output(self):
        out0 = self.training_data.collect()
        # Iterate over each refined query and collect its output
        query_out = {}
        for qid in self.refined_queries:
            query_out[qid] = {}
            for ref_level in self.refined_queries[qid]:
                query_out[qid][ref_level] = {}
                for iter_qid in self.refined_queries[qid][ref_level]:
                    if iter_qid > 0:
                        spark_query = self.refined_queries[qid][ref_level][iter_qid]
                        query_string = 'self.training_data.'+spark_query.compile()+'.collect()'
                        print("Processing Query", qid, "refinement level", ref_level, "iteration id", iter_qid)
                        query_out[qid][ref_level][iter_qid] = eval(query_string)

                query_out[qid][ref_level][0] = out0

        self.query_out = query_out

    def process_refined_queries(self, query_generator, fname_qg, fname_rq_write):
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
                refined_queries[qid][ref_level] = []
                refined_query_id = 10000*qid+ref_level
                refined_sonata_query = PacketStream(refined_query_id)
                refined_sonata_query.basic_headers = BASIC_HEADERS
                refined_sonata_query.map(map_keys=(reduction_key,), func=("mask", ref_level))
                for operator in sonata_query.operators:
                    copy_sonata_operators_to_spark(refined_sonata_query, operator)

                tmp1, _ = get_intermediate_spark_queries(self.max_reduce_operators, refined_sonata_query)

                refined_queries[qid][ref_level][0] = self.base_query
                for iter_qid in tmp1:
                    print "Adding intermediate Query:", iter_qid, type(tmp1[iter_qid])
                    refined_queries[qid][ref_level][iter_qid] = tmp1[iter_qid]

        self.refined_queries = refined_queries

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

    # noinspection PyShadowingNames
    def get_reformatted_output(self):
        query_output = self.query_out
        query_output_reformatted = {}
        for qid in query_output:
            for ref_level in query_output[qid]:
                for iter_qid in query_output[qid][ref_level]:
                    out = query_output[qid][ref_level][iter_qid]

                    for entry in out:
                        #print entry
                        if type(entry[0]) == type(1):
                            entry = (entry,1)
                        ts = entry[0][0]
                        if ts not in query_output_reformatted:
                            query_output_reformatted[ts] = {}
                        if qid not in query_output_reformatted[ts]:
                            query_output_reformatted[ts][qid] = {}
                        if ref_level not in query_output_reformatted[ts][qid]:
                            query_output_reformatted[ts][qid][ref_level] = {}
                        if iter_qid not in query_output_reformatted[ts][qid][ref_level]:
                            query_output_reformatted[ts][qid][ref_level][iter_qid] = {}
                        k = tuple(entry[0][1:])
                        v = entry[1]
                        query_output_reformatted[ts][qid][ref_level][iter_qid][k] = v
                    print qid, ref_level, iter_qid, query_output_reformatted[ts][qid][ref_level].keys()

        self.query_output_reformatted = query_output_reformatted

    def get_diff_buckets(self, prev_out, curr_out, ref_level_prev):
        diff_entries = {}
        print "Curr", len(curr_out.keys()), "prev", len(prev_out.keys())
        for curr_out_entry in curr_out.keys():
            filtered_keys = filter(lambda x: len(str(x).split('.')) == 4, curr_out_entry)
            filtered_keys = [str(IPNetwork(str(x)+"/"+str(ref_level_prev)).network) for x in filtered_keys]
            for prev_out_entry in prev_out.keys():
                print prev_out_entry, filtered_keys
                break
                if str(prev_out_entry) in filtered_keys:
                    diff_entries[curr_out_entry] = curr_out[curr_out_entry]
                    break
            break
        print "Diff", len(diff_entries.keys())
        return diff_entries

    def get_query_costs(self):
        query_output_reformatted = self.query_output_reformatted
        query_costs = {}
        for ts in query_output_reformatted:
            query_costs[ts] = {}
            for qid in query_output_reformatted[ts]:
                query_costs[ts][qid] = {}
                query = qt.qid_2_sonata_query[qid]
                partition_plans = query.get_partition_plans()
                print partition_plans
                ref_levels = qt.refined_queries[qid].keys()
                for partition_plan in partition_plans[qid]:
                    print partition_plan
                    for ref_level_prev in ref_levels:
                        for ref_level_curr in ref_levels:
                            if ref_level_curr > ref_level_prev:
                                transit = (ref_level_prev, ref_level_curr)
                                iter_qids_prev = query_output_reformatted[ts][qid][ref_level_prev].keys()
                                iter_qids_curr = query_output_reformatted[ts][qid][ref_level_curr].keys()
                                iter_qids_prev.sort()
                                iter_qids_curr.sort()
                                print ts, qid, transit, iter_qids_prev, iter_qids_curr
                                # output of the previous level helps us filter out crap from curr level
                                prev_out = query_output_reformatted[ts][qid][ref_level_prev][iter_qids_prev[-1]]


                                bucket_count = 0
                                packet_count = 0
                                # Maximum number of packets that we will send to stream processor if all
                                # reduce operations are done at the stream processor. Note that we have implemented that
                                # for such cases filtering will still be done in the data plane, that's why we only
                                # count the difference (filtered packet tuples) and not the total
                                curr_in = query_output_reformatted[ts][qid][ref_level_curr][0]
                                in_query = self.base_query
                                prev_bucket_count = self.get_diff_buckets(prev_out, curr_in, ref_level_prev)
                                ctr = 1
                                for elem in str(partition_plan):
                                    curr_out = query_output_reformatted[ts][qid][ref_level_curr][iter_qids_curr[ctr]]

                                    # To get the keys that we need to discard we need to know what entries are
                                    # common between the output of prev level and keys in the current bucket
                                    # For that we need to get a sense of position of reduction key
                                    curr_query = self.refined_queries[qid][ref_level_curr][iter_qids_curr[ctr]]
                                    diff_entries = self.get_diff_buckets(prev_out, curr_out, ref_level_prev)
                                    diff_entries_count = len(diff_entries.keys())

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

                                query_costs[ts][qid][partition_plan, transit] = (bucket_count, packet_count)
        self.query_costs = query_costs


if __name__ == "__main__":
    fname_rq_read = 'query_engine/query_dumps/refined_queries_1.pickle'
    qt = QueryTraining(fname_rq_read=fname_rq_read)
    qt.get_reformatted_output()
    print qt.refined_queries
    #qt.get_query_output()

    with open('query_out.pickle','r') as f:
        qt.query_out = pickle.load(f)

    #query_output = qt.query_out
    qt.get_reformatted_output()
    qt.get_query_costs()
    print qt.query_costs

    #qt.get_query_output()
    #print qt.query_out




