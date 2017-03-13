#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import logging
import pickle
import time
from multiprocessing.connection import Client, Listener
from threading import Thread

from sonata.core.training.hypothesis.hypothesis import Hypothesis
from sonata.dataplane_driver.dataplane_driver import DPDriverConfig
from sonata.streaming_manager.streaming_manager import StreamingManager

#from sonata.core.training.weights.training_data import TrainingData
from sonata.core.training.utils import get_spark_context_batch


class Runtime(object):
    def __init__(self, conf, queries):
        self.conf = conf
        self.queries = queries
        (self.sc, self.timestamps, self.training_data) = get_spark_context_batch()
        self.dp_queries = {}
        self.sp_queries = {}

        # TODO: create function for logging setup
        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(conf['log_file'])
        self.fh.setLevel(logging.INFO)
        self.logger.addHandler(self.fh)
        # ================

        self.dp_driver_thread = Thread(name='dp_driver', target=self.start_dataplane_driver)
        self.streaming_driver_thread = Thread(name='streaming_driver', target=self.start_streaming_driver)
        self.op_handler_thread = Thread(name='op_handler', target=self.start_op_handler)
        #self.fm_thread.setDaemon(True)

        self.dp_driver_thread.start()
        time.sleep(1)

        for query in self.queries:
            # Generate weights graph for each query
            hypothesis = Hypothesis(self, query)

            # Learn query plan
            # learn = Learn(weights)

            # Execute learned query plan


        #     # Apply learning algorithm to determine the final weights
        #     query.get_refinement_plan(ref_levels)
        #     self.logger.info("runtime,cost_refinement_plan,"+str(start)+","+str(time.time()))
        #
        #     # Generate dataplane and streaming abstract queries for refinement and partitioning
        #     print query.query_2_final_plan
        #     query.query_in_mapping = {}
        #     start = time.time()
        #     query.generate_query_in_mapping(finest_plan, query.query_2_final_plan, {}, [], False)
        #     self.logger.info("runtime,query_in_mapping,"+str(start)+","+str(time.time()))
        #
        #
        #     print "Q2In", query.query_in_mapping
        #     print "Q2Out", query.generate_query_out_mapping()
        #
        #     query.get_query_2_refinement_levels(finest_plan, query.query_2_final_plan, {})
        #     query.get_orig_refined_mapping()
        #
        #     start = time.time()
        #
        #
        #     query.generate_refined_queries(reduction_key)
        #     self.logger.info("runtime,generate_refined_queries,"+str(start)+","+str(time.time()))
        #
        #     start = time.time()
        #     query.generate_partitioned_queries()
        #     self.logger.info("runtime,generate_partitioned_queries,"+str(start)+","+str(time.time()))
        #     for qid in query.qid_2_dp_queries:
        #         print "Adding DP queries for query", qid
        #         self.dp_queries[qid] = query.qid_2_dp_queries[qid]
        #
        #     for qid in query.qid_2_sp_queries:
        #         print "Adding SP queries for query ", qid
        #         self.sp_queries[qid] = query.qid_2_sp_queries[qid]
        #
        #     print query.query_2_refinement_levels[query.qid].keys()
        #     print query.refined_2_orig
        #
        # time.sleep(2)
        # if self.dp_queries:
        #     self.send_to_dp_driver("init", self.dp_queries)
        #
        # # Start SM after everything is set in DP
        # self.streaming_driver_thread.start()
        #
        # if self.sp_queries:
        #     self.send_to_sm()
        #
        # self.op_handler_thread.start()
        #
        #
        # self.dp_driver_thread.join()
        # self.streaming_driver_thread.join()
        # self.op_handler_thread.join()

    def start_op_handler(self):
        """
        At the end of each window interval, two things need to happen for each query (in order),
        (1) registers and filter tables need to be flushed, (2) Filter tables need to get updated.
        We tried to do (1) and (2) for each query independently, but struggled as there were no
        easy way to flush specific registers for a query. So what we ended up doing was to wait
        for o/p from all queries, use the reset command to flush all registers/tables at once,
        and then update them with the delta commands. I am sure there is a better way of solving
        this reset and update problem.
        :return:
        """
        # Start the output handler
        # It receives output for each query in SP
        # It sends output of the coarser queries to the FM or
        # SM depending on where filter operation is applied (mostly DP)
        self.op_handler_socket = self.conf['sm_conf']['op_handler_socket']
        self.op_handler_listener = Listener(self.op_handler_socket)
        start = time.time()
        queries_received = {}
        updateDeltaConfig = False
        while True:
            print "Ready to receive data from SM ***************************"
            conn = self.op_handler_listener.accept()
            # Expected (qid,[])
            op_data = conn.recv_bytes()
            print "$$$$ OP Handler received:"+str(op_data)
            received_data = op_data.split(",")
            src_qid = int(received_data[1])
            table_match_entries = received_data[2:]
            queries_received[src_qid] = table_match_entries
            print "DP Queries: ", str(len(self.dp_queries.keys())), " Received keys:", str(len(queries_received.keys()))
            if len(queries_received.keys()) == len(self.dp_queries.keys()):
                updateDeltaConfig = True

            delta_config = {}
            print "## Received output for query", src_qid, "at time", time.time()-start
            if updateDeltaConfig:
                start = time.time()
                for src_qid in queries_received:
                    table_match_entries = queries_received[src_qid]
                    for query in self.queries:
                        print query.refined_2_orig
                        # find the queries that take the output of this query as input
                        original_qid, ref_level = query.refined_2_orig[src_qid]
                        if (original_qid, ref_level) in query.query_out_mapping:
                            target_queries = query.query_out_mapping[(original_qid, ref_level)]
                            for (dst_orig_qid,dst_ref_level) in target_queries:
                                dst_refined_qid = query.orig_2_refined[(dst_orig_qid,dst_ref_level)]
                                # get then name of the filter operator (and corresponding table)
                                # update the delta config dict
                                delta_config[(dst_refined_qid, src_qid)] = table_match_entries
                # reset these state variables
                updateDeltaConfig = False
                self.logger.info("runtime,create_delta_config,"+str(start)+","+str(time.time()))
                queries_received = {}

            # TODO: Update the send_to_dp_driver function logic
            # now send this delta config to fabric manager and update the filter tables
            if delta_config != {}:
                self.send_to_dp_driver("delta", delta_config)
        return 0

    def start_dataplane_driver(self):
        # Start the fabric managers local to each data plane element
        fm = DPDriverConfig(self.conf['fm_conf'], self.conf['emitter_conf'])
        fm.start()
        while True:
            time.sleep(5)
        return 0

    def start_streaming_driver(self):
        # Start streaming managers local to each stream processor
        sm = StreamingManager(self.conf['sm_conf'])
        sm.start()
        while True:
            time.sleep(5)
        return 0

    def compile(self):
        query_expressions = []
        for query in self.queries:
            query_expressions.append(query.compile_sp())
        return query_expressions

    def send_to_sm(self):
        # Send compiled query expression to streaming manager
        start = time.time()
        serialized_queries = pickle.dumps(self.sp_queries)
        conn = Client(self.conf['sm_conf']['sm_socket'])
        conn.send(serialized_queries)
        self.logger.info("runtime,sm_init,"+str(start)+","+str(time.time()))
        time.sleep(3)

    def send_to_dp_driver(self, message_type, content):
        # Send compiled query expression to fabric manager
        start = time.time()
        message = {message_type: content}
        serialized_queries = pickle.dumps(message)
        conn = Client(self.conf['fm_conf']['fm_socket'])
        conn.send(serialized_queries)
        self.logger.info("runtime,fm_"+message_type+","+str(start)+","+str(time.time()))
        time.sleep(1)
        return ''