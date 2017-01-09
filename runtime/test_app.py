#!/usr/bin/python
# Initialize coloredlogs.
import logging

logging.getLogger('testApp')

import coloredlogs

coloredlogs.install(level='ERROR', )

from runtime import *
from query_engine.sonata_queries import *


batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000 * window_length

featuresPath = ''
redKeysPath = ''

if __name__ == '__main__':
    spark_conf = {'batch_interval': batch_interval, 'window_length': window_length,
                  'sliding_interval': sliding_interval, 'featuresPath': featuresPath, 'redKeysPath': redKeysPath,
                  'sm_socket': ('localhost', 5555),
                  'op_handler_socket': ('localhost', 4949)}

    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': 'out-veth-2'}

    conf = {'dp': 'p4', 'sp': 'spark',
            'sm_conf': spark_conf, 'emitter_conf': emitter_conf,
            'fm_socket': ('localhost', 6666)}

    q0 = PacketStream()
    app_n = 1
    if app_n == 1:
        # New Queries
        q1 = (PacketStream(1)
              .filter(filter_keys=('proto',), func=('eq', 6))
              .map(keys=('dIP', 'sIP'))
              .distinct(keys=('dIP', 'sIP'))
              .map(keys=('dIP',), map_values = ('count',), func=('eq',1,))
              .reduce(keys=('dIP',), func=('sum',))
              .filter(filter_vals=('count',), func=('geq', '3'))
              .map(keys=('dIP',))
              )

        q2 = (PacketStream(2)
              .filter(filter_keys=('proto',), func=('eq', 6))
              .map(keys=('dIP','payload'))
              )

        q3 = (q2.join(new_qid=3, query=q1)
              .map(keys=('dIP', 'payload'), map_values=('count',), func=('eq', 1))
              .reduce(keys=('dIP','payload'),func=('sum',))
              .filter(filter_vals=('count',), func = ('geq', 1))
              .distinct(keys=('dIP',))
              .map(keys=('dIP',))
              )
        print q3
        queries = [q3]

    elif app_n == 2:
        q1 = (PacketStream(1).filter(keys = ('proto',),values = ('6',))
              .filter(keys = ('dIP',),values = ('112.7.186.25',))
              .map(keys=('dIP', 'sIP'))
              .distinct(keys=('dIP', 'sIP'))
            )

        q2 = (PacketStream(2)
              .map(keys=('dIP',), values=('1',))
              .reduce(keys=('dIP',), func='sum', values=('count',))
              )
        queries = [q1]

    runtime = Runtime(conf, queries)
