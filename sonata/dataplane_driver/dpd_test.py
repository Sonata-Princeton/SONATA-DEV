#!/usr/bin/env python

import logging
import pickle
import argparse
import time

from threading import Thread

from multiprocessing.connection import Client

from dp_driver import DataplaneDriver

BASEPATH = '/home/vagrant/'
SONATA = 'dev'
DP_DRIVER_CONF = ('localhost', 6666)
SPARK_ADDRESS = 'localhost'
SNIFF_INTERFACE = 'm-veth-2'


class DPDTest(object):
    def __init__(self, pickled_file, socket_data):
        self.dpd_socket = socket_data
        self.target_id = 1

        # LOGGING
        log_level = logging.DEBUG
        # add handler
        self.logger = logging.getLogger('DPDTest')
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info('init')

        self.message = None
        j = 0
        with (open(pickled_file, "rb")) as openfile:
            while True:
                j += 1
                try:
                    tmp = (pickle.load(openfile))
                    # TODO: This should not be required with the right query dump
                    for qid in tmp:
                        for oprtor in tmp[qid].operators:
                            if oprtor.name == "Map":
                                if len(oprtor.map_keys) > 0:
                                    oprtor.map_keys = ["dIP"]

                    self.message = tmp
                except EOFError:
                    break
        if j > 1:
            self.logger.info('there was more than one message in the pickled file')

    def start_dpd(self):
        dpd = DataplaneDriver(self.dpd_socket)
        dpd_thread = Thread(name='dp_driver', target=dpd.start)
        dpd_thread.setDaemon(True)

        config = {
            'em_conf': {'spark_stream_address': SPARK_ADDRESS,
                        'spark_stream_port': 8989,
                        'sniff_interface': SNIFF_INTERFACE,
                        'log_file': BASEPATH + SONATA + "/sonata/tests/demos/reflection_dns/graph/emitter2.log"
                        },
            'switch_conf': {
                'compiled_srcs': BASEPATH + SONATA + '/sonata/dataplane_driver/p4/compiled_srcs/',
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
        dpd.add_target('p4', self.target_id, config)
        dpd_thread.start()

    def cost_test(self):
        msg_type = 'get_cost'
        content = (self.message, self.target_id)
        cost = self.send_message(msg_type, content, True)
        self.logger.info('received %i as cost' % (cost, ))

    def supported_test(self):
        msg_type = 'is_supported'
        content = (self.message, self.target_id)
        is_supported = self.send_message(msg_type, content, True)
        self.logger.info('target can support the query: %s' % (str(is_supported), ))

    def run_test(self):
        msg_type = 'init'
        content = (self.message, self.target_id)
        self.send_message(msg_type, content, False)

    def display_message(self):
        for key, value in self.message.iteritems():
            out = '%i: qid=%i, parse_payload=%s\n\t%s' % (key, value.id, str(value.parse_payload), value)
            print out

    def send_message(self, msg_type, content, receive):
        message = {msg_type: content}
        serialized_queries = pickle.dumps(message)
        conn = Client(self.dpd_socket)
        conn.send(serialized_queries)
        data = None
        if receive:
            data = conn.recv()
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pickled_file', help='path to pickled query object', type=str)
    parsed_args = parser.parse_args()

    dpd_socket = ('localhost', 6666)

    print '# Creating test instance'
    tester = DPDTest(parsed_args.pickled_file, dpd_socket)

    if True:
        print '# Displaying messages'
        tester.display_message()

    if True:
        print '# Trying to start the dataplane'
        tester.start_dpd()
        print '# Successfully started'

        if True:
            print '# Testing "is_supported"'
            tester.supported_test()

        if True:
            print '# Testing "get_cost"'
            tester.cost_test()

        if True:
            print '# Testing "run"'
            tester.run_test()

        for i in range(0, 12):
            print '\tSleep for 5 seconds'
            time.sleep(5)

    print '# Yay, done!!!'
