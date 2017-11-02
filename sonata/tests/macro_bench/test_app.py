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

SERVER = False
P4_TYPE = 'p4'

if SERVER:
    BASEPATH = '/home/sonata/'
    SONATA = 'SONATA-DEV'
    DP_DRIVER_CONF = ('172.17.0.101', 6666)
    SPARK_ADDRESS = '172.17.0.98'
    SNIFF_INTERFACE = 'ens1f1'
    RESULTS_FOLDER = '/home/sonata/SONATA-DEV/sonata/tests/demos/reflection_dns/graph/'
else:
    BASEPATH = '/home/vagrant/'
    SONATA = 'dev'
    DP_DRIVER_CONF = ('localhost', 6666)
    SPARK_ADDRESS = 'localhost'
    SNIFF_INTERFACE = 'm-veth-2'
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
                  'sm_socket': ('0.0.0.0', 5555),
                  'op_handler_socket': ('localhost', 4949)}

    # emitter_conf = {'spark_stream_address': SPARK_ADDRESS,
    #                 'spark_stream_port': 8989,
    #                 'sniff_interface': 'out-veth-2', 'log_file': emitter_log_file}

    conf = {'dp': 'p4', 'sp': 'spark',
            'sm_conf': spark_conf, 'emitter_conf': {}, 'log_file': rt_log_file,
            'fm_conf': {'fm_socket': DP_DRIVER_CONF, 'log_file': fm_log_file}}

    # New Queries
    q1 = (PacketStream(1)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 45))
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

    queries = [q3]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")
    runtime = Runtime(conf, queries)