import sys
import math
import time
import os
import json
from multiprocessing.connection import Client
from pyspark import SparkContext
import shutil

# import interfaces
from vighata_platform.local_node.interfaces import *


class LocalDetection(object):
    def __init__(self, init_threshold_ip, location_id, sliding_interval, featuresPath,
                    redKeysPath, SDN_ADDRESS, SDN_PORT,
                    DSD_CENTRAL_PORT, DSD_CENTRAL_ADDRESS):

        # initialize spark context
        self.sc = SparkContext(appName="Vighata-localDetection")

        # initialize config params
        self.init_threshold_ip = init_threshold_ip
        self.location_id = location_id
        self.featuresPath = featuresPath
        self.redKeysPath = redKeysPath
        self.sliding_interval = sliding_interval

        # initialize SDX Interface
        self.sdx_interface = SDXInterface(SDN_ADDRESS, SDN_PORT)

        # initialize DSD central node Interface
        self.central_node_interface = CentralNodeInterface(self.location_id,
                                                            DSD_CENTRAL_PORT,
                                                            DSD_CENTRAL_ADDRESS)
        # initialize feature stream Interface
        self.feature_stream_interface = FeatureStreamInterface(self.sc,
                                                                featuresPath)
        # initialize reduction keys Interface
        self.reduction_keys_interface = ReductionKeysInterface(redKeysPath)

    def start(self):
        while True:
            features_rdd = self.feature_stream_interface.update_features()
            self.process_features_stream(features_rdd)
            time.sleep(self.sliding_interval)
            pass

    def process_features_stream(self, features_rdd):
        pass

if __name__ == "__main__":
    featuresPath = '/vagrant/vighata_platform/local_node/features/'
    redKeysPath = '/home/vagrant/dev/vighata_platform/feature_extraction/reduction_keys/'

    sliding_interval = 10
    topK = 10
    init_threshold_ip = 50

    # SDN Interface socket
    SDN_PORT = 4545
    SDN_ADDRESS = "localhost"

    # Cental Node Interface socket
    DSD_CENTRAL_PORT = 5454
    DSD_CENTRAL_ADDRESS = "localhost"
    location_id = 0
    local_node = LocalDetection(init_threshold_ip, location_id, sliding_interval, featuresPath,
                        redKeysPath, SDN_ADDRESS, SDN_PORT,
                        DSD_CENTRAL_PORT, DSD_CENTRAL_ADDRESS)
    local_node.start()
