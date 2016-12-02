#!/usr/bin/env python
# Author: Arpit Gupta
# Parser that reads hashed IPFix
# data to generate tuples of incoming data stream

import os
import glob
import math, time
import pickle

from multiprocessing.connection import Listener

baseDir = os.path.join('/vagrant/data')
all_fnames = glob.glob(os.path.join(baseDir,
                        'hashed_dns_flows.csv/part*'))

T = 1000
spark_stream_address = 'localhost'
spark_stream_port = 8989
listener = Listener((spark_stream_address, spark_stream_port), backlog=10)

while True:
    print "Waiting for socket"
    spark_conn = listener.accept()
    print "Received request from Spark Stream"
    try:
        print "Sending data to Spark"
        current_time = 0
        for fname in all_fnames:
            print fname
            with open(fname, 'r') as f:
                for line in f:
                    time_start = math.ceil(int(line.split(",")[0])/T)
                    if current_time == 0:
                        current_time = time_start
                    if time_start > current_time:
                        print time_start, current_time
                        print "Sleeping for 1 second"
                        current_time = time_start
                        time.sleep(1)
                    else:
                        #print line
                        spark_conn.send(line)

    except:
        pass
    spark_conn.close()
