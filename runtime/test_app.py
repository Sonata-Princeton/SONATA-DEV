#!/usr/bin/python
# Initialize coloredlogs.
import logging
logging.getLogger("testApp")

import coloredlogs

coloredlogs.install(level='ERROR',)

#from runtime import *
from query_engine.sonata_queries import *

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000*window_length

featuresPath = ''
redKeysPath = ''

if __name__ == "__main__":

    spark_conf = {'batch_interval': batch_interval, 'window_length': window_length, 'sliding_interval': sliding_interval, 'featuresPath': featuresPath, 'redKeysPath': redKeysPath, 'sm_socket':('localhost',5555),
                  'op_handler_socket': ('localhost', 4949)}

    emitter_conf = {'spark_stream_address': 'localhost',
                    'spark_stream_port': 8989,
                    'sniff_interface': "out-veth-2"}

    conf = {'dp': 'p4', 'sp': 'spark',
            'sm_conf': spark_conf, 'emitter_conf': emitter_conf,
            'fm_socket': ('localhost', 6666)}

    q0 = PacketStream()

    q1 = (PacketStream()
                    .filter(keys = ("proto",), values = ('6',), comp = "eq")
                    .map(keys = ("dIP", "sIP"))
                    .distinct()
                    .map(keys = ("dIP",), values = ("1",))
                    .reduce(func = 'sum', values = ('count',))
                    .filter(keys = ("count",), values=("2",), comp = "geq")
                    .map(keys=('dIP',))
             )

    q2 = (PacketStream()
          .map(keys=('dIP',), values=tuple([x for x in q0.basic_headers]))
        )

    #print q2.expr, q2.keys, q2.values
    q3 = q1.join(query=q2)

    #print q0
    #print q1
    #print q2
    #print q3

    #runtime = Runtime(conf, queries)
    #runtime.send_to_sm()
