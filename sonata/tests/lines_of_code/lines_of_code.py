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
    RESULTS_FOLDER = '/home/sonata/SONATA-DEV/sonata/tests/lines_of_code/q6/results/'
else:
    BASEPATH = '/home/vagrant/'
    SONATA = 'dev'
    DP_DRIVER_CONF = ('localhost', 6666)
    SPARK_ADDRESS = 'localhost'
    SNIFF_INTERFACE = 'm-veth-2'
    RESULTS_FOLDER = '/home/vagrant/dev/sonata/tests/lines_of_code/q6/results/'


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
    q0_1 = (PacketStream(1)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 50))
          .map(keys=('dIP',))
          )

    q0_2 = (PacketStream(2)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'payload'))
          )

    q0_3 = (q0_2.join(new_qid=3, query=q0_1)
          .map(keys=('dIP', 'payload'), map_values=('count',), func=('eq', 1))
          .reduce(keys=('dIP', 'payload'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', 1))
          .map(keys=('dIP',))
          .distinct(keys=('dIP',))
          )

    # Traffic anomaly detection (All UDP traffic)
    q1 = (PacketStream(1)
          .filter(filter_keys=('proto',), func=('eq', [17]))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('dIP',))
          )

    # heavy hitter detection
    # This works with training data since we need to
    # first know how much is 99 percentile and then
    # use that 99 percentile as threshold
    q2 = (PacketStream(2)
          .map(keys=('dIP', 'sIP'), values=('nBytes',))
          .reduce(keys=('dIP','sIP',), func=('sum',))
          .filter(filter_vals=('nBytes',), func=('geq', '99'))
          .map(keys=('dIP',))
          )

    # super spreader detection
    # One host makes too many connections to different

    q3 = (PacketStream(3)
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('sIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('sIP',))
          )

    # ssh brute forcing
    q4 = (PacketStream(4)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP', 'nBytes'))
          .distinct(keys=('dIP', 'sIP', 'nBytes'))
          .map(keys=('dIP','nBytes'), map_values=('count',), func=('set', 1,))
          .reduce(keys=('dIP','nBytes'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('dIP',))
          )
    # DNS TTL change detection
    q5 = (PacketStream(5)
          .filter(filter_keys=('sPort',), func=('eq', 53))
          .map(keys=('domain', 'ttl'), map_values=('count',), func=('set', 1,))
          .reduce(keys=('domain', 'ttl'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('domain',))
          )

    # port scan
    # One host is scanning lot of different ports
    # this potentially happens before an attack
    q6 = (PacketStream(6)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('sIP', 'dPort'))
          .distinct(keys=('sIP', 'dPort'))
          .map(keys=('sIP',), map_values=('count',), func=('set', 1,))
          .reduce(keys=('sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('sIP',))
          )

    queries = [q6]

    runtime = Runtime(conf, queries)





