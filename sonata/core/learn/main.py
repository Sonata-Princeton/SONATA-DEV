#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

# System imports
from netaddr import *
from pyspark import SparkContext, SparkConf

from cost_model import *
from hypothesis import Hypothesis


class QueryTraining(object):

    conf = (SparkConf()
            .setMaster("local[*]")
            .setAppName("SONATA-Training")
            .set("spark.executor.memory","6g")
            .set("spark.driver.memory","20g")
            .set("spark.cores.max","16"))

    sc = SparkContext(conf=conf)
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

    # Load training data
    training_data_path = TD_PATH
    ref_levels = REFINEMENT_LEVELS

    # 10 second window length
    window_length = 1*1000

    base_query = spark.PacketStream(0)
    base_query.basic_headers = BASIC_HEADERS

    base_sonata_query = spark.PacketStream(0)
    base_sonata_query.basic_headers = BASIC_HEADERS

    def __init__(self, query_generator_fname = QG_FNAME):
        # Get the query generator
        with open(query_generator_fname,'r') as f:
            self.query_generator = pickle.load(f)
        self.max_reduce_operators = self.query_generator.max_reduce_operators
        self.qid_2_query = self.query_generator.qid_2_query

        self.hypothesis = Hypothesis(self)
        """
        with open('hypothesis.pickle','wb') as f:
            pickle.dump(self.hypothesis, f)
        """
        self.cost_model = CostModel(self.hypothesis)

        with open(CM_FNAME,'w') as f:
            pickle.dump(self.cost_model.weights, f)



if __name__ == "__main__":
    qt = QueryTraining()