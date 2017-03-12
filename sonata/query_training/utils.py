#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine.query_generator import *

from sonata.query_engine.sonata_queries import *

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
