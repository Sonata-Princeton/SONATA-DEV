#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

import os

from sonata.query_engine.sonata_queries import *
from sonata.core.runtime import Runtime

batch_interval = 0.5
window_length = 1
sliding_interval = 1

RESULTS_FOLDER = '/home/vagrant/dev/sonata/tests/macro_bench/results/'

featuresPath = ''
redKeysPath = ''

if __name__ == '__main__':

    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    emitter_log_file = RESULTS_FOLDER + "emitter.log"
    fm_log_file = RESULTS_FOLDER + "dataplane_driver.log"
    rt_log_file = RESULTS_FOLDER + "runtime.log"

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

    q0 = PacketStream()

    # New Queries
    q1 = (PacketStream(1)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 990))
          .map(keys=('dIP',))
          )

    q2 = (PacketStream(2)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'payload'))
          )

    q3 = (q2.join(new_qid=3, query=q1)
          .map(keys=('dIP', 'payload'), map_values=('count',), func=('eq', 1))
          .reduce(keys=('dIP', 'payload'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 1))
          .map(keys=('dIP',))
          .distinct(keys=('dIP',))
          )

    queries = [q1]

    runtime = Runtime(conf, queries)


# def convert_queries_to_new_version(queries):
#     from sonata.query_engine.sonata_operators.map import *
#     from sonata.query_engine.sonata_operators.distinct import *
#     from sonata.query_engine.sonata_operators.filter import *
#     from sonata.query_engine.sonata_operators.join import *
#     from sonata.query_engine.sonata_operators.reduce import *
#
#
#     for query in queries.values():
#         new_qo = query_object.QueryObject(query.id)
#         new_qo.parse_payload = query.parse_payload
#         for operator in query.operators:
#             new_o = None
#             keys = filter(lambda x: x != 'ts', operator.keys)
#             if operator.name == 'Map':
#                 new_o = Map()
#                 if isinstance(operator.map_keys, tuple):
#                     new_o.map_keys = tuple(operator.map_keys[0])
#                 else:
#                     new_o.map_keys = operator.map_keys
#                 new_o.keys = keys
#                 new_o.map_values = operator.map_values
#                 new_o.values = operator.values
#                 new_o.prev_keys = operator.prev_keys
#                 new_o.prev_values = operator.prev_values
#                 new_o.func = operator.func
#             elif operator.name == 'Distinct':
#                 new_o = Distinct()
#                 new_o.keys = keys
#                 new_o.values = operator.values
#                 new_o.prev_keys = operator.prev_keys
#                 new_o.prev_values = operator.prev_values
#             elif operator.name == 'Filter':
#                 new_o = Filter()
#                 new_o.keys = keys
#                 new_o.values = operator.values
#                 new_o.prev_keys = operator.prev_keys
#                 new_o.prev_values = operator.prev_values
#                 new_o.filter_keys = operator.filter_keys
#                 new_o.filter_vals = operator.filter_vals
#                 new_o.func = operator.func
#                 new_o.src = operator.src
#             elif operator.name == 'Join':
#                 new_o = Join()
#                 new_o.query = operator.query
#             elif operator.name == 'Reduce':
#                 new_o = Reduce(func=('sum',))
#                 new_o.keys = keys
#                 new_o.values = operator.values
#                 new_o.prev_keys = operator.prev_keys
#                 new_o.prev_values = operator.prev_values
#                 new_o.func = operator.func
#             else:
#                 print "Found a unsupported operator: %s" % (operator.name, )
#
#             new_qo.operators.append(new_o)
#
#         cleaned_queries[new_qo.id] = new_qo
