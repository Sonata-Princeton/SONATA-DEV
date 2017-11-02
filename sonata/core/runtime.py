#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import logging
import pickle
import time
from multiprocessing.connection import Client, Listener
from threading import Thread

# from sonata.core.training.hypothesis.hypothesis import Hypothesis
from sonata.streaming_driver.streaming_driver import StreamingDriver

# # from sonata.core.training.weights.training_data import TrainingData
# from sonata.core.training.utils import get_spark_context_batch, create_spark_context

# from sonata.core.training.learn.learn import Learn
from sonata.core.refinement import get_refined_query_id, Refinement
from sonata.core.partition import get_dataplane_query, get_streaming_query

from sonata.core.integration import Target
from sonata.dataplane_driver.dp_driver import DataplaneDriver
from sonata.sonata_layers import *
from sonata.streaming_driver.query_object import PacketStream as SP_QO
from sonata.core.utils import copy_sonata_operators_to_sp_query, flatten_streaming_field_names
from sonata.core.utils import generated_source_path


class Runtime(object):
    dp_queries = {}
    sp_queries = {}
    query_plans = {}
    refinement_keys = {}
    query_in_mappings = {}
    query_out_mappings = {}
    query_out_final = {}
    op_handler_socket = None
    op_handler_listener = None

    def __init__(self, conf, queries, app_path):
        self.conf = conf
        self.refinement_keys = conf["refinement_keys"]
        self.GRAN_MAX = conf["GRAN_MAX"]
        self.GRAN = conf["GRAN"]
        self.queries = queries
        self.initialize_logging()
        self.target_id = 1
        self.app_path = generated_source_path(app_path, "/generated_src/")
        self.log_path = generated_source_path(app_path, "/logs/")

        self.sonata_fields = self.get_sonata_layers()

        use_pickled_queries = False
        if use_pickled_queries:
            with open('pickled_queries.pickle', 'r') as f:
                pickled_queries = pickle.load(f)
                self.dp_queries = pickled_queries[0]
                self.sp_queries = pickled_queries[1]
        else:
            # Learn the query plan
            for query in self.queries:
                target = Target()
                assert hasattr(target, 'costly_operators')
                refinement_object = Refinement(query, target, self.GRAN_MAX, self.GRAN, self.refinement_keys)

                print "*********************************************************************"
                print "*                   Generating Query Plan                           *"
                print "*********************************************************************\n\n"

                final_plan = conf["final_plan"]
                # Account for an additional map (masking) operation for iterative refinement
                final_plan = [(q, r, p + 1) for (q, r, p) in final_plan]

                prev_r = 0
                prev_qid = 0
                has_join, final_qid, sp_queries, join_queries = self.query_has_join_in_same_window(query,
                                                                                                   self.sonata_fields,
                                                                                                   final_plan)

                for (q, r, p) in final_plan:
                    qry = refinement_object.qid_2_query[q]
                    refined_query_id = get_refined_query_id(qry, r)

                    refined_sonata_query = refinement_object.get_refined_updated_query(qry.qid, r, prev_qid, prev_r,
                                                                                       has_join, final_qid)
                    # print "Refined Query: ", refined_sonata_query
                    if not has_join:
                        if prev_r > 0:
                            p += 1
                    else:
                        if prev_qid == qry.qid:
                            p += 1
                    dp_query = get_dataplane_query(refined_sonata_query, refined_query_id, self.sonata_fields, p)
                    self.dp_queries[refined_query_id] = dp_query

                    sp_query = get_streaming_query(refined_sonata_query, refined_query_id, self.sonata_fields, p)
                    self.sp_queries[refined_query_id] = sp_query
                    prev_r = r
                    prev_qid = q

                if not has_join:
                    self.update_query_mappings(refinement_object, final_plan, has_join)

            with open('pickled_queries.pickle', 'w') as f:
                pickle.dump({0: self.dp_queries, 1: self.sp_queries}, f)

        if has_join:
            for sp_query in sp_queries:
                self.sp_queries[sp_query.qid] = sp_query

        # print "Dataplane Queries:"
        # for (qid,query) in self.dp_queries.items():
        #     print "For", qid
        #     print query
        # print "\n\n"
        # print "Streaming Queries:"
        # for (qid,query) in self.sp_queries.items():
        #     print "For", qid
        #     print query

        # time.sleep(10)
        self.initialize_handlers()
        time.sleep(2)
        self.send_init_to_dp_driver('init', self.sonata_fields, self.dp_queries)
        print "*********************************************************************"
        print "*                   Updating data-plane driver                       *"
        print "*********************************************************************\n\n"

        # TODO:
        if self.sp_queries:
            self.send_to_sm(join_queries)

        # self.dp_driver_thread.join()
        self.streaming_driver_thread.join()
        self.op_handler_thread.join()

    def query_has_join_in_same_window(self, query, sonata_fields, final_plan):
        if query.left_child is not None and query.window == 'Same':
            right_query_operator = query.right_child.operators[-1]
            left_query_operator = query.left_child.operators[-1]

            ref_levels = list(
                set([r for (q, r, p) in final_plan if q == query.left_child.qid or q == query.right_child.qid]))

            join_values = [val + '_right' for val in right_query_operator.values] + [val + '_left' for val in
                                                                                     left_query_operator.values]
            query.operators[0].keys = right_query_operator.keys
            sp_queries = []
            join_queries = []

            ref_levels = sorted(ref_levels)

            final_query_id = None

            for (curr_ref_level, next_ref_level) in zip(ref_levels, ref_levels[1:]):
                sp_query_id = get_refined_query_id(query, curr_ref_level)
                sp_query = SP_QO(sp_query_id)
                sp_query.has_join = True
                sp_query.ref_level = curr_ref_level
                sp_query.join_same_window(keys=(flatten_streaming_field_names(right_query_operator.keys)),
                                          values=tuple(flatten_streaming_field_names(join_values)),
                                          left_qid=(query.right_child.qid * 10000 + curr_ref_level),
                                          right_qid=(query.left_child.qid * 10000 + curr_ref_level))

                for operator in query.operators:
                    copy_sonata_operators_to_sp_query(sp_query, operator, sonata_fields)

                if curr_ref_level < 32:
                    sp_query.map(keys=flatten_streaming_field_names(right_query_operator.keys)
                                 )

                sp_queries.append(sp_query)
                join_queries.append(query.right_child.qid * 10000 + curr_ref_level)
                join_queries.append(query.left_child.qid * 10000 + curr_ref_level)

                self.query_out_mappings[sp_query.qid] = [query.right_child.qid * 10000 + next_ref_level,
                                                         query.left_child.qid * 10000 + next_ref_level]
                final_query_id = query.qid

            curr_ref_level = ref_levels[-1]
            sp_query_id = get_refined_query_id(query, curr_ref_level)
            sp_query = SP_QO(sp_query_id)
            sp_query.has_join = True
            sp_query.ref_level = curr_ref_level
            sp_query.join_same_window(keys=(flatten_streaming_field_names(right_query_operator.keys)),
                                      values=tuple(flatten_streaming_field_names(join_values)),
                                      left_qid=(query.right_child.qid * 10000 + curr_ref_level),
                                      right_qid=(query.left_child.qid * 10000 + curr_ref_level))

            for operator in query.operators:
                copy_sonata_operators_to_sp_query(sp_query, operator, sonata_fields)

            if curr_ref_level < 32:
                sp_query.map(keys=flatten_streaming_field_names(right_query_operator.keys)
                             )

            sp_queries.append(sp_query)
            join_queries.append(query.right_child.qid * 10000 + curr_ref_level)
            join_queries.append(query.left_child.qid * 10000 + curr_ref_level)

            return True, final_query_id, sp_queries, join_queries
        else:
            return False, None, None, []

    def get_sonata_layers(self):

        INITIAL_LAYER = "ethernet"
        layer_2_target = {"ethernet": "bmv2",
                          "tcp": "bmv2",
                          "ipv4": "bmv2",
                          "udp": "bmv2",
                          "DNS": "scapy",
                          "payload": "scapy"}
        import json

        with open('sonata/fields_mapping.json') as json_data_file:
            data = json.load(json_data_file)

        field_that_determines_child = None
        if "field_that_determines_child" in data[INITIAL_LAYER][
            layer_2_target[INITIAL_LAYER]]: field_that_determines_child = \
        data[INITIAL_LAYER][layer_2_target[INITIAL_LAYER]]["field_that_determines_child"]
        layers = SonataLayer(INITIAL_LAYER,
                             data,
                             fields=data[INITIAL_LAYER][layer_2_target[INITIAL_LAYER]]["fields"],
                             offset=data[INITIAL_LAYER][layer_2_target[INITIAL_LAYER]],
                             parent_layer=None,
                             child_layers=data[INITIAL_LAYER][layer_2_target[INITIAL_LAYER]]["child_layers"],
                             field_that_determines_child=field_that_determines_child,
                             is_payload=data[INITIAL_LAYER][layer_2_target[INITIAL_LAYER]]["in_payload"],
                             layer_2_target=layer_2_target
                             )

        sonataFields = SonataRawFields(layers)

        return sonataFields

    def update_query_mappings(self, refinement_object, final_plan, has_join):
        if len(final_plan) > 1:
            query1 = refinement_object.qid_2_query[final_plan[0][0]]

            for ((q1, r1, p1), (q2, r2, p2)) in zip(final_plan, final_plan[1:]):
                query1 = refinement_object.qid_2_query[q1]
                query2 = refinement_object.qid_2_query[q2]

                qid1 = get_refined_query_id(query1, r1)
                qid2 = get_refined_query_id(query2, r2)
                if qid2 not in self.query_in_mappings:
                    self.query_in_mappings[qid2] = []
                self.query_in_mappings[qid2].append(qid1)

                if qid1 not in self.query_out_mappings:
                    self.query_out_mappings[qid1] = []
                self.query_out_mappings[qid1].append(qid2)

                # Update the queries whose o/p needs to be displayed to the network operators
            r = final_plan[-1][0]
            qid = get_refined_query_id(query1, r)
            self.query_out_final[qid] = 0
        else:
            print "No mapping update required"

    def start_op_handler(self):
        """
        At the end of each window interval, two things need to happen for each query (in order),
        (1) registers and filter tables need to be flushed, (2) Filter tables need to get updated.
        We tried to do (1) and (2) for each query independently, but struggled as there were no
        easy way to flush specific registers for a query. So what we ended up doing was to wait
        for o/p from all queries, use the reset command to flush all registers/tables at once,
        and then update them with the delta commands. I am sure there is a better way of solving
        this reset and update problem.
        """
        # Start the output handler
        # It receives output for each query in SP
        # It sends output of the coarser queries to the data-plane driver or
        # SM depending on where filter operation is applied (mostly DP)
        self.op_handler_socket = tuple(self.conf['sm_conf']['op_handler_socket'])
        self.op_handler_listener = Listener(self.op_handler_socket)

        start = "%.20f" % time.time()

        queries_received = {}
        updateDeltaConfig = False

        while True:
            conn = self.op_handler_listener.accept()
            op_data = conn.recv_bytes()
            op_data = op_data.strip('\n')
            received_data = op_data.split(",")
            src_qid = int(received_data[1])
            if received_data[2:] != ['']:
                table_match_entries = list(set(received_data[2:]))
                queries_received[src_qid] = table_match_entries
            else:
                queries_received[src_qid] = []

            if len(queries_received.keys()) >= len(self.query_out_mappings.keys()):
                updateDeltaConfig = True

            delta_config = {}
            # print queries_received, self.query_out_mappings
            if updateDeltaConfig:
                start = "%.20f" % time.time()
                for src_qid in queries_received:
                    if src_qid in self.query_out_mappings:
                        table_match_entries = queries_received[src_qid]
                        if len(table_match_entries) > 0:
                            out_queries = self.query_out_mappings[src_qid]
                            for out_qid in out_queries:
                                # find the queries that take the output of this query as input
                                delta_config[(out_qid, src_qid)] = table_match_entries
                                # reset these state variables
                    else:
                        if queries_received[src_qid]:
                            with open(self.log_path + "/final_output", 'w') as f:
                                f.write(str("\n".join(queries_received[src_qid])))

                        if len(queries_received[src_qid]) > 0:
                            print "Final Output for " + str(src_qid) + ": " + str(queries_received[src_qid])

                updateDeltaConfig = False
                if delta_config != {}: self.logger.info(
                    "runtime,create_delta_config," + str(start) + ",%.20f" % time.time())
                queries_received = {}

            # TODO: Update the send_to_dp_driver function logic
            # now send this delta config to data-plane driver and update the filter tables
            if delta_config != {}:
                IP = ""
                for qid_key in delta_config.keys():
                    IP = delta_config[qid_key]

                # print "*********************************************************************"
                # print "*                   IP " + IP[0] + " satisfies coarser query            *"
                # print "*                   Reconfiguring Data Plane                        *"
                # print "*********************************************************************\n\n"
                # print "Sending delta commands: ", delta_config
                self.send_to_dp_driver("delta", delta_config)
            # else:
            #     print "Sending empty delta commands: ", delta_config
            #     self.send_to_dp_driver("delta", delta_config)

        return 0

    def start_dataplane_driver(self):

        # Start the data-plane drivers local to each data plane element
        dpd = DataplaneDriver(self.conf['fm_conf']['fm_socket'], self.conf["internal_interfaces"],
                              self.conf['fm_conf']['log_file'])
        self.dpd_thread = Thread(name='dp_driver', target=dpd.start)
        self.dpd_thread.setDaemon(True)

        p4_type = 'p4'
        self.conf['emitter_conf']["log_path"] = self.log_path
        config = {
            'em_conf': self.conf['emitter_conf'],
            'switch_conf': {
                'compiled_srcs': self.app_path,
                'json_p4_compiled': 'compiled.json',
                'p4_compiled': 'compiled.p4',
                'p4c_bm_script': '/home/vagrant/p4c-bmv2/p4c_bm/__main__.py',
                'bmv2_path': '/home/vagrant/bmv2',
                'bmv2_switch_base': '/targets/simple_switch',
                'switch_path': '/simple_switch',
                'cli_path': '/sswitch_CLI',
                'thriftport': 22222,
                'p4_commands': 'commands.txt',
                'p4_delta_commands': 'delta_commands.txt'
            }
        }
        dpd.add_target(p4_type, self.target_id, config)
        self.dpd_thread.start()

    def start_streaming_driver(self):
        # Start streaming managers local to each stream processor
        # self.conf['sm_conf']['sc']=self.sc
        sm = StreamingDriver(self.conf['sm_conf'])
        sm.start()
        while True:
            time.sleep(5)
        return 0

    def compile(self):
        query_expressions = []
        for query in self.queries:
            query_expressions.append(query.compile_sp())
        return query_expressions

    def send_to_sm(self, join_queries):
        # Send compiled query expression to streaming manager
        start = "%.20f" % time.time()
        with open(self.app_path + 'spark.py', 'w') as f:
            f.write("spark_queries = {}\n\n")
            for qid in self.sp_queries:
                compiled_spark = str(self.sp_queries[qid])
                if 'join' not in compiled_spark:
                    f.write("spark_queries[" + str(qid) + "] = " + compiled_spark + "\n\n")
                else:
                    f.write(compiled_spark[4:] + "\n\n")

        serialized_queries = pickle.dumps({'queries': self.sp_queries, 'join_queries': join_queries})
        conn = Client(tuple(self.conf['sm_conf']['sm_socket']))
        conn.send(serialized_queries)
        self.logger.info("runtime,sm_init," + str(start) + "," + str(time.time()))
        print "*********************************************************************"
        print "*                   Updating Streaming Driver                       *"
        print "*********************************************************************\n\n"
        time.sleep(3)

    def send_init_to_dp_driver(self, message_type, sonata_fields, content):
        # Send compiled query expression to data-plane driver
        start = "%.20f" % time.time()

        with open('dns_reflection.pickle', 'w') as f:
            pickle.dump(content, f)

        message = {message_type: {0: content, 1: self.target_id, 2: sonata_fields}}
        serialized_queries = pickle.dumps(message)
        conn = Client(tuple(self.conf['fm_conf']['fm_socket']))
        conn.send(serialized_queries)
        self.logger.info("runtime,fm_" + message_type + "," + str(start) + ",%.20f" % time.time())
        time.sleep(1)
        conn.close()
        print "*********************************************************************"
        print "*                   Updating data-plane driver                       *"
        print "*********************************************************************\n\n"
        return ''

    def send_to_dp_driver(self, message_type, content):
        # Send compiled query expression to data-plane driver
        start = "%.20f" % time.time()

        # TODO: remove hardcoding
        with open('dns_reflection.pickle', 'w') as f:
            pickle.dump(content, f)

        message = {message_type: {0: content, 1: self.target_id}}
        serialized_queries = pickle.dumps(message)
        conn = Client(tuple(self.conf['fm_conf']['fm_socket']))
        conn.send(serialized_queries)
        # self.logger.info("runtime,fm_" + message_type + "," + str(start) + ",%.20f" % time.time())
        time.sleep(1)
        conn.close()
        # print "*********************************************************************"
        # print "*                   Updating data-plane driver                       *"
        # print "*********************************************************************\n\n"
        return ''

    def initialize_handlers(self):
        target = self.start_dataplane_driver()
        self.streaming_driver_thread = Thread(name='streaming_driver', target=self.start_streaming_driver)
        self.op_handler_thread = Thread(name='op_handler', target=self.start_op_handler)
        # self.fm_thread.setDaemon(True)
        self.streaming_driver_thread.start()
        self.op_handler_thread.start()
        time.sleep(1)

    def initialize_logging(self):
        # create a logger for the object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs messages
        self.fh = logging.FileHandler(self.conf['base_folder'] + self.__class__.__name__)
        self.fh.setLevel(logging.DEBUG)
        self.logger.addHandler(self.fh)
