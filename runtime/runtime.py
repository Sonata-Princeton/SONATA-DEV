#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

from query_engine import *
import json, time
from multiprocessing.connection import Client, Listener
import pickle
from threading import Thread
from fabric_manager.fabric_manager import FabricManagerConfig
from streaming_manager.streaming_manager import StreamingManager
import logging

logging.getLogger("runtime")


class Runtime(object):
    def __init__(self, conf, queries):
        self.conf = conf
        self.queries = queries
        self.dp_queries = {}
        self.sp_queries = {}

        self.fm_thread = Thread(name='fm_manager', target=self.start_fabric_managers)

        self.sm_thread = Thread(name='sm_manager', target=self.start_streaming_managers)
        self.op_handler_thread = Thread(name='op_handler', target=self.start_op_handler)
        #self.fm_thread.setDaemon(True)

        self.fm_thread.start()


        time.sleep(1)

        for query in self.queries:
            logging.info("runtime: going thru queries")

            query.get_query_tree()
            query.get_all_queries()
            query.get_partition_plans()

            # TODO: get rid of this hardcoding
            reduction_key = 'dIP'
            ref_levels = range(0, 33, 8)
            finest_plan = ref_levels[-1]

            query.get_cost(ref_levels)
            query.get_refinement_plan(ref_levels)
            print query.query_2_final_plan
            query.generate_query_in_mapping(finest_plan, query.query_2_final_plan)
            print query.query_in_mapping
            print query.generate_query_out_mapping()
            print query.get_query_2_refinement_levels(finest_plan, query.query_2_final_plan)
            query.get_orig_refined_mapping()
            query.generate_refined_queries(reduction_key)
            query.generate_partitioned_queries()
            for qid in query.qid_2_dp_queries:
                print "Adding DP queries", qid, query.qid_2_dp_queries[qid]
                self.dp_queries[qid] = query.qid_2_dp_queries[qid]

            for qid in query.qid_2_sp_queries:
                print "Adding SP queries", qid, query.qid_2_sp_queries[qid]
                self.sp_queries[qid] = query.qid_2_sp_queries[qid]

        time.sleep(2)
        if self.dp_queries:
            self.send_to_fm("init", self.dp_queries)

        # Start SM after everything is set in DP
        self.sm_thread.start()

        if self.sp_queries:
            self.send_to_sm()

        self.op_handler_thread.start()

        #self.send_to_fm("delta", self.dp_queries)
        self.fm_thread.join()

        self.sm_thread.join()
        self.op_handler_thread.join()

    def start_op_handler(self):
        # Start the output handler
        # It receives output for each query in SP
        # It sends output of the coarser queries to the FM or
        # SM depending on where filter operation is applied (mostly DP)
        logging.debug("runtime: " + "starting output handler")
        self.op_handler_socket = self.conf['sm_conf']['op_handler_socket']
        self.op_handler_listener = Listener(self.op_handler_socket)
        logging.debug("OP Handler Running...")
        while True:
            print "Ready to receive data from SM ***************************"
            conn = self.op_handler_listener.accept()
            # Expected (qid,[])
            op_data = conn.recv_bytes()
            print "$$$$ OP Handler received:"+str(op_data)
            received_data = op_data.split(",")
            src_qid = int(received_data[1])
            table_match_entries = received_data[2:]
            delta_config = {}
            print "## Received output for query", src_qid

            for query in self.queries:
                # find the queries that take the output of this query as input
                print "Exploring ", query.qid, " with out-mappings:", query.query_out_mapping
                original_qid, ref_level = query.refined_2_orig[src_qid]
                if (original_qid, ref_level) in query.query_out_mapping:

                    target_queries = query.query_out_mapping[(original_qid, ref_level)]
                    print "Target Queries", target_queries
                    for (dst_orig_qid,dst_ref_level) in target_queries:
                        print "Found query", dst_orig_qid, " that requires o/p of", original_qid, "as i/p"
                        dst_refined_qid = query.orig_2_refined[(dst_orig_qid,dst_ref_level)]

                        print "We need to update the filter table for query", dst_refined_qid

                        dp_query = query.qid_2_dp_queries[dst_refined_qid]
                        print "Query is", dp_query.expr
                        # get then name of the filter operator (and corresponding table)
                        print "For this query filter tables are:", dp_query.src_2_filter_operator
                        filter_operator = dp_query.src_2_filter_operator[src_qid]
                        # update the delta config dict
                        delta_config[(dst_refined_qid, src_qid)] = table_match_entries

            # TODO: Update the send_to_fm function logic
            # now send this delta config to fabric manager and update the filter tables
            if delta_config != {}:
                self.send_to_fm("delta", delta_config)
        return 0

    def start_fabric_managers(self):
        # Start the fabric managers local to each data plane element
        logging.debug("runtime: " + "creating fabric managers")
        fm = FabricManagerConfig(self.conf['fm_socket'], self.conf['emitter_conf'])
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

    def compile(self):
        query_expressions = []
        for query in self.queries:
            query_expressions.append(query.compile_sp())
        return query_expressions

    def send_config(self):
        self.send_to_sm()
        self.send_to_fm()

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
        time.sleep(1)
        logging.debug("Config Sent to Streaming Manager ...")
        return ''