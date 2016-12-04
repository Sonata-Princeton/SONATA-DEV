
# Initialize coloredlogs.
import logging

logging.getLogger("testApp")

import coloredlogs

coloredlogs.install(level='DEBUG',)
                    #format='%(asctime)s %(hostname)s %(name)s(%(threadName)-10s) %(levelname)s %(message)s')

from runtime import *
from query_engine.sonata_queries import *

conf = {'dp':'p4', 'sp':'spark', 'sm_socket':('localhost', 7777),
        'fm_socket':('localhost', 6666)}

query = (PacketStream()
        .filter(expr = "proto == '17'")
        .map(keys = ("dIP", "sIP"))
        .distinct()
        .map(keys =("dIP",), values = ("1",))
        .reduce(func='sum', values=('count',))
        .filter(expr='count > 20')
        .map(keys=('dIP',))
        )
queries = []
queries.append(query)
runtime = Runtime(conf, queries)
#runtime.send_to_sm()
