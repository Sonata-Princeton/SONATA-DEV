#!/usr/bin/python

from query_engine.sonata_queries import *
import random

def generate_query_tree(depth, all_queries, qid):
    query_tree = {}
    if depth > 0:
        qid_l = 2 * qid
        all_queries.append(qid_l)
        query_tree[qid_l] = generate_query_tree(depth-1, all_queries, qid_l)

        qid_r = 2 * qid + 1
        all_queries.append(qid_r)
        query_tree[qid_r] = generate_query_tree(depth-1, all_queries, qid_r)

    return query_tree


class QueryGenerator(object):
    refinement_headers = ["dIP", "sIP"]
    other_headers = ["sPort", "dPort", "nBytes", "proto", "sMac", "dMac", "payload"]

    def __init__(self, n_queries, max_reduce_operators, query_tree_depth):
        self.n_queries = n_queries
        self.max_reduce_operators = max_reduce_operators
        self.query_tree_depth = query_tree_depth
        self.qid_2_thresh = {}
        self.all_queries = [1]
        self.query_tree = {1:generate_query_tree(self.query_tree_depth, self.all_queries, 1)}
        self.single_queries = [1]+self.get_left_children()
        self.qid_2_query = {}
        for qid in self.single_queries:
            if qid == 1:
                self.qid_2_query[qid] = self.generate_single_query(qid, isLeft=False)
            else:
                self.qid_2_query[qid] = self.generate_single_query(qid)

    def get_left_children(self):
        out = []
        qt = self.query_tree
        for parent in qt:
            if len(qt[parent].keys()) > 0:
                out.append(qt[parent].keys()[0])
                qt = qt[parent]
            else:
                break
        return out

    def generate_reduction_operators(self, q, qid, reduction_fields):
        q.map(keys=tuple(reduction_fields), values=("1",))
        q.reduce(keys=tuple(reduction_fields), func='sum', values=('count',))
        q.filter(keys=tuple(reduction_fields), values=(self.qid_2_thresh[qid],), comp="geq")

    def generate_single_query(self, qid, isLeft=True):
        q = PacketStream(qid)
        # TODO: get rid of this hardcoding
        self.qid_2_thresh[qid] = 2

        reduction_key = random.choice(self.refinement_headers)
        other_headers = self.other_headers + [x for x in self.refinement_headers if x != reduction_key]
        if isLeft:
            other_headers = list(set(other_headers)-set(["payload"]))
        n_reduce_operators = random.choice(range(1, 1+self.max_reduce_operators))
        number_header_fields = random.sample(range(1,1+len(other_headers)), n_reduce_operators)
        number_header_fields.sort(reverse=True)

        ctr = 0
        for n_reduce in range(1, 1+n_reduce_operators):
            reduction_fields = random.sample(other_headers, number_header_fields[ctr])
            other_headers = reduction_fields
            ctr += 1
            self.generate_reduction_operators(q, qid, [reduction_key]+reduction_fields)

        print qid, q
        return 0

if __name__ == "__main__":
    n_queries = 1
    max_reduce_operators = 2
    query_tree_depth = 1
    query_generator = QueryGenerator(n_queries, max_reduce_operators, query_tree_depth)