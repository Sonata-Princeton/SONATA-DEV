#!/usr/bin/env python

import logging
import pickle
import argparse

import query_object

import sys
sys.path.append("/home/vagrant/dev/sonata/query_engine/sonata_operators")

from sonata.query_engine.sonata_operators.map import *
from sonata.query_engine.sonata_operators.distinct import *
from sonata.query_engine.sonata_operators.filter import *
from sonata.query_engine.sonata_operators.join import *
from sonata.query_engine.sonata_operators.reduce import *


class CleanIt(object):
    def __init__(self, pickled_file):
        # LOGGING
        log_level = logging.DEBUG
        # add handler
        self.logger = logging.getLogger('DPDTest')
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info('init')

        qo = None
        i = 0
        with (open(pickled_file, "rb")) as openfile:
            while True:
                i += 1
                try:
                    qo = (pickle.load(openfile))
                except EOFError:
                    break
        if i > 1:
            self.logger.info('there was more than one message in the pickled file')

        cleaned_queries = dict()

        for query in qo.values():
            new_qo = query_object.QueryObject(query.id)
            new_qo.parse_payload = query.parse_payload
            for operator in query.operators:
                new_o = None
                keys = filter(lambda x: x != 'ts', operator.keys)
                if operator.name == 'Map':
                    new_o = Map()
                    if isinstance(operator.map_keys, tuple):
                        new_o.map_keys = tuple(operator.map_keys[0])
                    else:
                        new_o.map_keys = operator.map_keys
                    new_o.keys = keys
                    new_o.map_values = operator.map_values
                    new_o.values = operator.values
                    new_o.prev_keys = operator.prev_keys
                    new_o.prev_values = operator.prev_values
                    new_o.func = operator.func
                elif operator.name == 'Distinct':
                    new_o = Distinct()
                    new_o.keys = keys
                    new_o.values = operator.values
                    new_o.prev_keys = operator.prev_keys
                    new_o.prev_values = operator.prev_values
                elif operator.name == 'Filter':
                    new_o = Filter()
                    new_o.keys = keys
                    new_o.values = operator.values
                    new_o.prev_keys = operator.prev_keys
                    new_o.prev_values = operator.prev_values
                    new_o.filter_keys = operator.filter_keys
                    new_o.filter_vals = operator.filter_vals
                    new_o.func = operator.func
                    new_o.src = operator.src
                elif operator.name == 'Join':
                    new_o = Join()
                    new_o.query = operator.query
                elif operator.name == 'Reduce':
                    new_o = Reduce(func=('sum',))
                    new_o.keys = keys
                    new_o.values = operator.values
                    new_o.prev_keys = operator.prev_keys
                    new_o.prev_values = operator.prev_values
                    new_o.func = operator.func
                else:
                    print "Found a unsupported operator: %s" % (operator.name, )

                new_qo.operators.append(new_o)

            cleaned_queries[new_qo.id] = new_qo

        for key, value in cleaned_queries.iteritems():
            out = '%i: qid=%i, parse_payload=%s\n\t%s' % (key, value.id, str(value.parse_payload), value)
            # print out

        with open('dp_queries_clean.pickle', 'wb') as outfile:
            pickle.dump(cleaned_queries, outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pickled_file', help='path to pickled query object', type=str)
    parsed_args = parser.parse_args()

    tester = CleanIt(parsed_args.pickled_file)
