from __future__ import print_function

import sys
import math
import time

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from multiprocessing.connection import Client
from threading import Thread

spark_stream_address = 'localhost'
spark_stream_port = 8989

spark_agg_address = 'localhost'
spark_agg_port = 8990

batch_interval = 1
window_length = 10
sliding_interval = 10
T = 1000*window_length

#featuresPath = '/vagrant/platform/local_node/features/'
#redKeysPath = '/vagrant/platform/feature_extraction/reduction_keys/'



def processLogLine(flow):
    return tuple(flow.split(","))

class FeatureExtraction(object):
    def __init__(self, batch_interval, window_length, sliding_interval,
                    featuresPath, redKeysPath):

        # initialize config params
        self.batch_interval = batch_interval
        self.window_length = window_length
        self.sliding_interval = sliding_interval
        self.featuresPath = featuresPath
        self.redKeysPath = redKeysPath
        print("In FEM", self.redKeysPath, self.featuresPath)

        # intialize streaming context
        self.sc = SparkContext(appName="Vighata-Stream")
        self.ssc = StreamingContext(self.sc, self.batch_interval)


    def start(self):
        # start the module to update reduction keys
        self.reduction_key_updater = Thread(target=self.update_reduction_keys)
        self.reduction_key_updater.start()
        lines = self.ssc.socketTextStream(spark_stream_address, spark_stream_port)
        flows = (lines.map(lambda line: processLogLine(line)))
        self.process_flow_stream(flows)
        self.ssc.start()

    def process_flow_stream(self, flows):
        pass


    def update_reduction_keys(self):
        while True:
            for proto_vighata in self.reduction_keys:
                print("Updating reduction keys ...")
                for red_key in self.reduction_keys[proto_vighata]:
                    fname = self.redKeysPath+str(proto_vighata)+"_"+str(red_key)+".csv"
                    print("chutzpah fname ",fname)
                    with open(fname, 'r') as f:
                        dps = f.read().splitlines()
                    self.reduction_keys[proto_vighata][red_key] = self.sc.parallelize(dps).map(lambda s: (s, 1))
                    print("Update RED Key: proto_vighata ", proto_vighata, " red_key ", red_key)
                    # for dubuging only
                    print(self.reduction_keys[proto_vighata][red_key].collect())
                time.sleep(window_length)

if __name__ == "__main__":
    fem = FeatureExtraction(batch_interval, window_length, sliding_interval,
                        featuresPath, redKeysPath)
    fem.start()
