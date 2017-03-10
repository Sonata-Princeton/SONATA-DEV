#!/usr/bin/python
# Initialize coloredlogs.
#import coloredlogs

#coloredlogs.install(level='ERROR', )

from runtime import *
from query_engine.sonata_queries import *
import os

batch_interval = 1
window_length = 1
sliding_interval = 1

result_folder = '/home/arp/SONATA-DEV/results/result1/'
emitter_log_file = result_folder + "emitter.log"
fm_log_file = result_folder + "fabric_manager.log"
rt_log_file = result_folder + "runtime.log"

featuresPath = ''
redKeysPath = ''

if __name__ == '__main__':
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

    q0 = PacketStream()

    # New Queries
    q1 = (PacketStream(1)
          #.filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values = ('count',), func=('eq',1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '500'))
          .map(keys=('dIP',))
          )

    q2 = (PacketStream(2)
          #.filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP','payload'))
          )

    q3 = (q2.join(new_qid=3, query=q1)
          .map(keys=('dIP', 'payload'), map_values=('count',), func=('eq', 1))
          .reduce(keys=('dIP','payload'),func=('sum',))
          .filter(filter_vals=('count',), func = ('geq', 1))
          .map(keys=('dIP',))
          .distinct(keys=('dIP',))
          )

    queries = [q3]



    runtime = Runtime(conf, queries)