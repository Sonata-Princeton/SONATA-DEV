#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine import *
import json, time
from multiprocessing.connection import Client
import pickle
from threading import Thread
from fabric_manager.fabric_manager import FabricManagerConfig
#from streaming_manager.streaming_manager import StreamingManager
import logging

logging.getLogger("runtime")


class Runtime(object):
    def __init__(self, conf, queries):
        self.conf = conf
        self.queries = queries
        self.dp_queries = []
        self.sp_queries = []

        self.fm_thread = Thread(name='fm_manager', target=self.start_fabric_managers)
        #self.sm_thread = Thread(name='sm_manager', target=self.start_streaming_managers)

        #self.fm_thread.setDaemon(True)
        self.fm_thread.start()
        #self.sm_thread.start()

        time.sleep(1)

        self.dp_qid = 1
        for query in self.queries:
            logging.debug("runtime: going thru queries")
            query.get_refinement_plan()
            for refined_query in query.refined_queries:
                logging.info("Refined Queries: ")
                logging.info(refined_query.eval())
                refined_query.get_partitioning_plan(4)
                refined_query.partition_plan_final = refined_query.partition_plans[0]
                refined_query.generate_dp_query(self.dp_qid)
                self.dp_qid += 1
                refined_query.generate_sp_query()
                self.dp_queries.append(refined_query.dp_query)
                self.sp_queries.append(refined_query.sp_query)

                for query in self.dp_queries:
                    logging.info("DP Query: " + query.expr + str(len(self.dp_queries)))

                for query in self.sp_queries:
                    logging.info("SP Query: " + query.expr)

        time.sleep(2)
        if self.dp_queries:
            self.send_to_fm("init", self.dp_queries)
            #self.send_to_sm()

        self.send_to_fm("delta", self.dp_queries)
        self.fm_thread.join()

    def start_fabric_managers(self):
        # Start the fabric managers local to each data plane element
        logging.debug("runtime: " + "creating fabric managers")
        fm = FabricManagerConfig(self.conf['fm_socket'])
        logging.debug("runtime: " + "starting fabric managers")
        fm.start()
        while True:
            logging.debug("Running...")
            time.sleep(5)
        return 0

    def start_streaming_managers(self):
        # Start streaming managers local to each stream processor
        logging.debug("runtime: " + "creating streaming managers")
        sm = StreamingManager(self.conf['sm_conf'])
        logging.debug("runtime: " + "starting streaming managers")
        sm.start()
        while True:
            logging.debug("Running...")
            time.sleep(5)
        return 0

    def apply_iterative_refinement(self):
        return 0

    def compile(self):
        query_expressions = []
        for query in self.queries:
            query_expressions.append(query.compile_sp())
        return query_expressions

    def send_config(self):
        self.send_to_sm()
        self.send_to_fm()

    def send_init_config(self):
        # send initial config to FMs and SMs
        return 0

    def send_update_config(self):
        # send delta config updates to SMs & FMs
        return 0

    def receive_query_output(self):
        # receive query output from stream processor
        return 0


    def send_to_sm(self):
        # Send compiled query expression to streaming manager
        logging.info(self.sp_queries)
        serialized_queries = pickle.dumps(self.sp_queries)
        conn = Client(self.conf['sm_conf']['sm_socket'])
        conn.send(serialized_queries)
        time.sleep(3)
        logging.debug("Config Sent to Streaming Manager ...")

    def send_to_fm(self, message_type, content):
        # Send compiled query expression to fabric manager
        message = {message_type: content}
        serialized_queries = pickle.dumps(message)
        conn = Client(self.conf['fm_socket'])
        conn.send(serialized_queries)
        time.sleep(3)
        logging.debug("Config Sent to Streaming Manager ...")
        return ''



#.reduceByKey("sum")
