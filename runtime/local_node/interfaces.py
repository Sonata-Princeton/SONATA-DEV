import sys
import math
import time
import os
import json
from multiprocessing.connection import Client
from pyspark import SparkContext
import shutil

featuresPath = '/vagrant/platform/local_node/features/'
redKeysPath = '/vagrant/platform/feature_extraction/reduction_keys/'

sliding_interval = 10
topK = 10

def processLogLine(flow):
    return tuple(str(x) for x in flow.split(","))


class FeatureStreamInterface(object):
    def __init__(self, sc, featuresPath):
        self.sc = sc
        # DSD features
        self.features = {"DNS":{"mac1": {"1":None},
                                "mac2": {"1":None},
                                "ip1": {"1":None}}
                        }
        self.featuresPath = featuresPath

    def update_features(self):
        features_rdd = {}
        for proto in self.features:
            features_rdd[proto] = {}
            for red_key in self.features[proto]:
                features_rdd[proto][red_key] = {}
                for feature_id in self.features[proto][red_key]:
                    fname = self.featuresPath+str(proto)+"_"+str(red_key)+"_"+str(feature_id)+".csv"
                    if os.path.isfile(fname):
                        tmp = (self.sc.textFile(fname)
                                .map(lambda line: processLogLine(line))
                                .collect()
                                )
                        features_rdd[proto][red_key][feature_id] = self.sc.parallelize(tmp)
        return features_rdd


class ReductionKeysInterface(object):
    def __init__(self, redKeysPath):
        self.redKeysPath = redKeysPath
        self.reduction_keys = {"DNS":{"mac1": None,
                                "mac2": None,
                                "ip2": None}}

    def send_reduction_keys(self):
        for proto in self.reduction_keys:
            for red_key in self.reduction_keys[proto]:
                to_send = self.reduction_keys[proto][red_key]
                if to_send != None:
                    txt = "\n".join(str(a) for a in to_send)
                    fname = self.redKeysPath+str(proto)+"_"+str(red_key)+".csv"
                    #print(fname, to_send)
                    with open(fname, 'w') as f:
                        f.write(txt + "\n")


class SDXInterface(object):
    def __init__(self, SDN_ADDRESS, SDN_PORT):
        self.socket = (SDN_ADDRESS, SDN_PORT)

    def create_message(match = {}, action = {}):
        # match = {"tcp_dst" = 53}, action= {"samp_rate" = 1000 or "off"="" or "mitigate"=""}
        msg = {}
        msg["match"] = match
        msg["action"] = action
        msg["id"]  = ",".join(match.values())
        return msg

    def send_message(self, msg):
        conn = Client((self.socket))
        conn.send(json.dump(msg))
        conn.close()


class CentralNodeInterface(object):
    def __init__(self, location_id, DSD_CENTRAL_PORT, DSD_CENTRAL_ADDRESS):
        self.socket = (DSD_CENTRAL_ADDRESS, DSD_CENTRAL_PORT)
        self.location_id = location_id
        self.potential_victims_local = {}
        self.potential_victims_remote = {}
        self.confirmed_victims_remote = {}

    def send_potential_victims_local(self):
        #print self.socket
        conn = Client((self.socket))
        conn.send(json.dump(self.potential_vicitms))
        conn.close()

    def receive_victims_from_central(self, type):
        conn = Client((self.socket))
        if type == "potential":
            conn.send(json.dump({"req":"potential_victims"}))
        else:
            conn.send(json.dump({"req":"confirmed_victims"}))
        tmp= conn.recv()
        if type == "potential":
            self.potential_victims_remote = json.loads(tmp)
        else:
            self.confirmed_victims_remote = json.loads(tmp)
        conn.close()
