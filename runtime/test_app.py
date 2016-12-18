#!/usr/bin/env python
# Initialize coloredlogs.
import logging

logging.getLogger("testApp")

import coloredlogs

coloredlogs.install(level='DEBUG',)

from runtime import *
from query_engine.sonata_queries import *

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000*window_length

featuresPath = ''
redKeysPath = ''

spark_conf = {'batch_interval': batch_interval, 'window_length': window_length, 'sliding_interval': sliding_interval, 'featuresPath': featuresPath, 'redKeysPath': redKeysPath, 'sm_socket':('localhost',5555)}

conf = {'dp': 'p4', 'sp': 'spark',
        'sm_conf': spark_conf,
        'fm_socket': ('localhost', 6666)}

query = (PacketStream()
                .filter(expr="proto == '17'")
                .map(keys=("dIP", "sIP"))
                .distinct()
                .map(keys=("dIP",), values = ("1",))
                .reduce(func='sum', values=('count',))
                .filter(expr='count > 2')
                .map(keys=('dIP',)))

queries = []
queries.append(query)
runtime = Runtime(conf, queries)
#runtime.send_to_sm()
