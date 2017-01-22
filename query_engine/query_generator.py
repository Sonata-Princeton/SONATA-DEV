#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import random
import pickle
import copy

from query_engine.sonata_operators import *
from query_engine.sonata_queries import *
from query_engine.utils import *
#from runtime.runtime import *
import os
import itertools

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000 * window_length

featuresPath = ''
redKeysPath = ''

basic_headers = ["dIP", "sIP", "sPort", "dPort", "nBytes", "proto", "sMac", "dMac"]

def generate_composed_spark_queries(reduction_key, basic_headers, query_tree, qid_2_query, composed_queries = {}):
    #print query_tree
    root_qid = query_tree.keys()[0]
    #print "##", root_qid, query_tree.keys(), qid_2_query
    if root_qid in qid_2_query:
        root_query_sonata = qid_2_query[root_qid]
        root_query_spark = spark.PacketStream(root_qid)
        root_query_spark.basic_headers = basic_headers
    else:
        root_query_sonata = PacketStream(root_qid)
        root_query_spark = spark.PacketStream(root_qid)
        root_query_spark.basic_headers = basic_headers

    #print "%%", root_qid, root_query_sonata

    if query_tree[root_qid] != {}:
        children = query_tree[root_qid].keys()
        children.sort()
        left_qid = children[0]
        right_qid = children[1]
        left_query = generate_composed_spark_queries(reduction_key, basic_headers,
                                                     {left_qid:query_tree[root_qid][left_qid]},
                                                     qid_2_query, composed_queries)

        right_query = generate_composed_spark_queries(reduction_key, basic_headers,
                                                      {right_qid:query_tree[root_qid][right_qid]},
                                                      qid_2_query, composed_queries)

        #print "Left", left_qid, left_query

        #print "Right", right_qid, right_query
        for operator in root_query_sonata.operators:
            if operator.name == 'Map' and len(operator.func) > 0 and operator.func[0] == 'mask':
                copy_sonata_operators_to_spark(right_query, operator)

        composed_query = right_query.join(q=left_query, join_key = reduction_key, in_stream = 'In.')
        # This is important else the composed query will take the qid of the right child itself
        composed_query.qid = root_qid
        for operator in root_query_sonata.operators:
            if not (operator.name == 'Map' and len(operator.func) > 0 and operator.func[0] == 'mask'):
                copy_sonata_operators_to_spark(composed_query, operator)

        composed_queries[root_qid] = copy.deepcopy(composed_query)
    else:
        #print "Adding for", root_qid, root_query_sonata, root_query_sonata.qid
        for operator in root_query_sonata.operators:
            copy_sonata_operators_to_spark(root_query_spark, operator)

        #print "##Updating key", root_qid
        composed_queries[root_qid] = copy.deepcopy(root_query_spark)
        composed_query = root_query_spark

    #print "returning for ", root_qid, composed_queries

    return composed_query

def generate_composed_query(query_tree, qid_2_query):
    #print query_tree
    root_qid = query_tree.keys()[0]
    #print "##", root_qid, query_tree.keys(), qid_2_query
    if root_qid in qid_2_query:
        root_query = qid_2_query[root_qid]
    else:
        root_query = PacketStream(root_qid)

    #print "%%", root_qid, root_query

    if query_tree[root_qid] != {}:
        children = query_tree[root_qid].keys()
        children.sort()

        left_qid = children[0]
        right_qid = children[1]

        left_query = generate_composed_query({left_qid:query_tree[root_qid][left_qid]}, qid_2_query)
        right_query = generate_composed_query({right_qid:query_tree[root_qid][right_qid]}, qid_2_query)

        left_query_keys = left_query.keys
        #right_query = right_query.map(keys=left_query_keys, values=tuple(basic_headers))
        """
        print "Qid", root_qid
        print "Root Query", root_query
        print "Right Query", right_query
        print "Left Query", left_query
        """
        composed_query = right_query.join(new_qid=root_qid, query=left_query)
        for operator in root_query.operators:
            copy_operators(composed_query, operator)
    else:
        composed_query = root_query

    return composed_query



def generate_query_tree(ctr, all_queries, depth):
    """
    Generate Query Tree

    arguments:
    @depth: depth of the query tree to be generated
    @all_queries: list of all queries in the tree
    @qid: query id for the query
    """
    query_tree = {}
    if depth > 0:
        if ctr > len(all_queries)/2:
            return query_tree
        qid_l = all_queries[2*ctr-1]
        query_tree[qid_l] = generate_query_tree(ctr+1, all_queries,depth-1)

        qid_r =  all_queries[2*ctr]
        query_tree[qid_r] = {}
    return query_tree

def get_left_children(query_tree, out):
    """
    return all the left children for query_tree
    """
    qt = query_tree
    for parent in qt:
        #print parent, qt
        if len(qt[parent].keys()) > 0:
            children = qt[parent].keys()
            children.sort()
            #print "Sorted Children", children
            out.append(children[0])
            get_left_children({children[0]:qt[parent][children[0]]}, out)
        else:
            break


class QueryGenerator(object):
    # separated from basic headers -
    # refinement headers will be used in all queries to define refinement and zoom in
    refinement_headers = ["dIP", "sIP"]
    other_headers = ["proto", "sMac", "dMac"]

    def __init__(self, case, n_queries, max_reduce_operators, query_tree_depth, max_filter_frac):
        """
        Initialize QueryGenerator

        arguments:
        @n_queries: number of queries
        @max_reduce_operators: number of reduction operators
        @query_tree_depth: total depth of the query tree
        """
        self.n_queries = n_queries
        self.max_reduce_operators = max_reduce_operators
        self.max_query_tree_depth = query_tree_depth
        self.max_filter_sigma = max_filter_frac
        self.composed_queries = {}
        self.query_trees = {}
        self.qid_2_thresh = {}

        self.qid_2_query = {}

        self.case = case

        if self.case == 0:
            self.generate_queries_case0()
        elif self.case == 1:
            self.generate_queries_case1()
        elif self.case == 2:
            self.generate_queries_case2()
        elif self.case == 3:
            self.generate_queries_case3()
        elif self.case == 4:
            # Case where we vary the height of the query tree
            self.generate_queries_case4()

    def generate_single_query_case4(self, qid, reduction_key, other_headers, query_height, thresh, isLeft=True):

        thresh_random = random.choice(range(thresh, 100))
        if query_height > 1:
            query_height = 1

        q = PacketStream(qid)
        q.reduction_key = reduction_key
        reduction_fields = [reduction_key]+other_headers[:query_height]
        q.map(keys=tuple(reduction_fields), map_values = ('count',), func=('eq',1,))
        q.reduce(keys=tuple(reduction_fields), func=('sum',))
        q.filter(filter_vals=('count',), func=('geq', thresh_random))
        q.map(keys=tuple([reduction_key]))

        return q

    def generate_queries_case0(self):
        # Older set of operations to generate random queries given query tree depth
        thresholds = [90, 70, 50, 30, 10, 1]
        thresholds = [95, 95, 95, 95, 95, 95]
        other_headers = ["sPort", "dPort", "nBytes", "sMac", "dMac", "proto"]
        for n_query in range(self.n_queries):

            root_qid = int(math.pow(2, 1 + self.max_query_tree_depth) - 1) * n_query + 1
            query_depth = random.choice(range(1+self.max_query_tree_depth))
            all_queries = range(root_qid, root_qid + int(math.pow(2, 1 + query_depth) - 1))

            ctr = 1
            query_tree = {root_qid:generate_query_tree(ctr, all_queries, query_depth)}
            print "Query Tree", query_tree
            self.query_trees[n_query] = query_tree
            qid_2_query = {}
            reduction_key = random.choice(self.refinement_headers)

            out = []
            get_left_children(query_tree, out)
            #print "Left children", out
            single_queries = [root_qid]+out
            single_queries.sort(reverse=True)
            print "Single Queries", single_queries
            query_height = 0
            for qid in single_queries:
                random.shuffle(other_headers)
                qid_2_query[qid] = self.generate_single_query_case4(qid, reduction_key, other_headers,
                                                                    query_height, thresholds[query_height])
                query_height += 1

            composed_query = generate_composed_query(query_tree, qid_2_query)
            self.composed_queries[n_query]= composed_query
            self.qid_2_query.update(qid_2_query)

            composed_query = generate_composed_query(query_tree, qid_2_query)
            self.composed_queries[n_query]= composed_query
            #print n_query, self.query_trees[n_query]
            #print composed_query.qid, composed_query
            self.qid_2_query.update(qid_2_query)
            #tmp = composed_query.get_reduction_key()
            #print tmp
        fname = 'data/use_case_0_filtered_data/query_generator_object_case0_'+str(self.n_queries)+'.pickle'
        print fname
        with open(fname, 'w') as f:
            pickle.dump(self, f)


    def generate_queries_case4(self):
        # Case where we vary the height of the query tree
        other_headers = ["sPort", "dPort", "nBytes", "sMac", "dMac", "proto"]
        heights = range(len(other_headers)-1)
        self.n_queries = len(heights)

        reduction_key = 'dIP'
        thresh = 95
        thresholds = [90, 70, 50, 30, 10, 1]
        thresholds = [95, 95, 95, 95, 95, 1]
        for n_query in range(self.n_queries):
            print "Depth of Query Tree", n_query
            query_tree_depth = n_query
            root_qid = int(math.pow(2, 1+len(heights))-1)*n_query+1
            all_queries = range(root_qid, root_qid+int(math.pow(2, 1+query_tree_depth)-1))
            ctr = 1
            query_tree = {root_qid:generate_query_tree(ctr, all_queries, query_tree_depth)}
            print "Query Tree", query_tree

            self.query_trees[n_query] = query_tree

            qid_2_query = {}

            out = []
            get_left_children(query_tree, out)
            single_queries = [root_qid]+out
            single_queries.sort(reverse=True)
            print "Single Queries", single_queries
            query_height = 0
            for qid in single_queries:

                qid_2_query[qid] = self.generate_single_query_case4(qid, reduction_key, other_headers,
                                                              query_height, thresholds[query_height])
                query_height += 1

            composed_query = generate_composed_query(query_tree, qid_2_query)
            self.composed_queries[n_query]= composed_query
            self.qid_2_query.update(qid_2_query)
        print "Total queries generated", len(self.qid_2_query.keys())
        fname = 'query_engine/use_cases_aws/query_generator_object_case4_'+str(self.n_queries)+'.pickle'
        #with open(fname, 'w') as f:
        #    pickle.dump(self, f)


    def generate_queries_case3(self):
        # Case where we will vary the threshold
        fracs = [1, 0.8, 0.6, .4, .2, .01, 0.001]
        self.n_queries = len(fracs)
        reduction_key = 'dIP'
        qid_2_query = {}
        for n_query in range(self.n_queries):
            query_tree = {n_query:{}}
            self.query_trees[n_query] = query_tree

            thresh = 100.0*float(1-fracs[n_query])
            reduction_fields = [reduction_key]
            qid = n_query
            q = PacketStream(qid)
            q.reduction_key = reduction_key
            q.map(keys=tuple(reduction_fields), map_values = ('count',), func=('eq',1,))
            q.reduce(keys=tuple(reduction_fields), func=('sum',))
            q.filter(filter_vals=('count',), func=('geq', thresh))
            q.map(keys=tuple(reduction_fields))

            qid_2_query[qid] = q
            composed_query = generate_composed_query(query_tree, qid_2_query)
            self.composed_queries[n_query]= composed_query
            self.qid_2_query.update(qid_2_query)

        fname = 'query_engine/use_cases_aws/query_generator_object_case3_'+str(self.n_queries)+'.pickle'
        with open(fname, 'w') as f:
            pickle.dump(self, f)



    def generate_queries_case2(self):
        # Case where the impact of combination of of reduction keys is highlighted
        other_headers = ["sPort", "nBytes", "proto", "sMac"]
        candidate_reduction_keys = []

        stuff = other_headers
        for L in range(0, len(stuff)+1):
            for subset in itertools.combinations(stuff, L):
                candidate_reduction_keys.append(subset)
        print len(candidate_reduction_keys)
        self.n_queries = len(candidate_reduction_keys)
        reduction_key = 'dIP'
        thresh = 95
        qid_2_query = {}
        for n_query in range(self.n_queries):
            query_tree = {n_query:{}}
            self.query_trees[n_query] = query_tree
            qid = n_query

            reduction_fields = [reduction_key]+list(candidate_reduction_keys[n_query])
            q = PacketStream(qid)
            q.reduction_key = reduction_key
            q.map(keys=tuple(reduction_fields), map_values=('count',), func=('eq',1,))
            q.reduce(keys=tuple(reduction_fields), func=('sum',))
            q.filter(filter_vals=('count',), func=('geq', thresh))
            q.map(keys=tuple(reduction_fields))

            qid_2_query[qid] = q
            composed_query = generate_composed_query(query_tree, qid_2_query)
            self.composed_queries[n_query]= composed_query
            self.qid_2_query.update(qid_2_query)

        fname = 'query_engine/use_cases_aws/query_generator_object_case2.pickle'
        with open(fname, 'w') as f:
            pickle.dump(self, f)

    def generate_queries_case1(self):
        # Case where we vary the number of reduce operators
        other_headers = ["sPort", "dPort", "nBytes", "proto", "sMac", "dMac"]
        self.n_queries = 1+len(other_headers)
        reduction_key = 'dIP'
        thresholds = [90, 80, 70, 60, 50, 40]
        qid_2_query = {}
        other_headers = ["sPort", "dPort", "nBytes", "proto", "sMac", "dMac"]
        for n_query in range(self.n_queries)[:-2]:
            query_tree = {n_query:{}}
            self.query_trees[n_query] = query_tree
            n_reduce_operations = 1+n_query
            qid = n_query
            q = PacketStream(qid)
            q.reduction_key = reduction_key
            for n_opr in range(n_reduce_operations):
                reduction_fields = [reduction_key]+other_headers[n_opr:n_reduce_operations-1]
                #print n_reduce_operations, n_opr, reduction_fields
                q.map(keys=tuple(reduction_fields), map_values = ('count',), func=('eq',1,))
                q.reduce(keys=tuple(reduction_fields), func=('sum',))
                q.filter(filter_vals=('count',), func=('geq', thresholds[n_opr]))
            q.map(keys=tuple([reduction_key]))

            qid_2_query[qid] = q
            composed_query = generate_composed_query(query_tree, qid_2_query)
            self.composed_queries[n_query]= composed_query
            self.qid_2_query.update(qid_2_query)

        fname = 'query_engine/use_cases_aws/query_generator_object_case1_'+str(self.n_queries)+'.pickle'
        with open(fname, 'w') as f:
            pickle.dump(self, f)



    def generate_reduction_operators(self, q, qid, reduction_fields, operator):
        """
        Generate Map-Reduce-Filter Operators on input query `q`
        arguments:
        @q: query PacketStream to add Map-Reduce-Filter operators
        @qid: query id for the query
        @reduction_fields: fields to reduce query on
        """
        thresh = float(random.choice(range(95, int(self.max_filter_sigma))))

        if qid not in self.qid_2_thresh:
            self.qid_2_thresh[qid] = []
        self.qid_2_thresh[qid].append(thresh)
        if operator == 'Reduce':
            q.map(keys=tuple(reduction_fields), map_values = ('count',), func=('eq',1,))
            q.reduce(keys=tuple(reduction_fields), func=('sum',))
            q.filter(filter_vals=('count',), func=('geq', thresh))
        else:
            q.map(keys=tuple(reduction_fields))
            q.distinct(keys=tuple(reduction_fields))

    def generate_single_query(self, qid, reduction_key, isLeft=True):
        """
        Generate Single Query

        arguments:
        @qid: query id for the query
        @is_left: `True`  - removes payload from possible header options for left child
                  `False` - also consider payload for right child of a tree
        """
        q = PacketStream(qid)
        q.reduction_key = reduction_key

        #other_headers = self.other_headers + [x for x in self.refinement_headers if x != reduction_key]
        other_headers = self.other_headers
        if isLeft:
            other_headers = list(set(other_headers)-set(["payload"]))
        n_reduce_operators = random.choice(range(1, 1+self.max_reduce_operators))
        number_header_fields = random.sample(range(1,1+n_reduce_operators), n_reduce_operators-1)
        # Make sure the last keys for reduce operation are same as chosen reduction key
        number_header_fields.append(0)
        number_header_fields.sort(reverse=True)

        ctr = 0
        has_distinct = False
        for n_reduce in range(1, 1+n_reduce_operators):
            reduction_fields = random.sample(other_headers, number_header_fields[ctr])
            other_headers = reduction_fields
            ctr += 1
            operator = random.choice(['Distinct', 'Reduce'])
            # Make sure that we don't have more than one distinct operator
            if operator == 'Distinct':
                if not has_distinct:
                    has_distinct = True
                else:
                    operator = 'Reduce'

            self.generate_reduction_operators(q, qid, [reduction_key]+reduction_fields, operator)
        q.map(keys=tuple([reduction_key]+reduction_fields))

        return q


if __name__ == "__main__":
    """
    result_folder = '/home/vagrant/dev/results/result1/'
    emitter_log_file = result_folder + "emitter.log"
    fm_log_file = result_folder + "fabric_manager.log"
    rt_log_file = result_folder + "runtime.log"


    if not os.path.exists(result_folder):
            os.makedirs(result_folder)

    spark_conf = {'batch_interval': batch_interval, 'window_length': window_length,
                  'sliding_interval': sliding_interval, 'featuresPath': featuresPath, 'redKeysPath': redKeysPath,
                  'sm_socket': ('localhost', 5555),
                  'op_handler_socket': ('localhost', 4949)}

    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': 'out-veth-2', 'log_file': emitter_log_file}

    conf = {'dp': 'p4', 'sp': 'spark',
            'sm_conf': spark_conf, 'emitter_conf': emitter_conf, 'log_file': rt_log_file,
            'fm_conf': {'fm_socket': ('localhost', 6666), 'log_file': fm_log_file}}
    """


    n_queries = 10
    max_filter_frac = 100
    max_reduce_operators = 1
    query_tree_depth = 2
    # TODO: make sure the queries are unique
    query_generator = QueryGenerator(0, n_queries, max_reduce_operators, query_tree_depth, max_filter_frac)

    queries = query_generator.composed_queries.values()
    print query_generator.qid_2_query
    """
    runtime = Runtime(conf, queries)


    for n_query in query_generator.query_trees:
        composed_queries = {}
        query_tree = query_generator.query_trees[n_query]
        reduction_key = query_generator.qid_2_query[query_tree.keys()[0]].reduction_key
        generate_composed_spark_queries(reduction_key, query_tree, query_generator.qid_2_query, composed_queries)
        print composed_queries

        for qid in composed_queries:
            query_spark =  composed_queries[qid]
            query_spark.in_stream = 'Out.'
            query_spark.basic_headers = ['a','b']
            print query_spark.compile()

    """






