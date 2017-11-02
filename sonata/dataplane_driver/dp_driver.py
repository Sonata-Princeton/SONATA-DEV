#!/usr/bin/env python

import logging
import pickle
import time
from multiprocessing.connection import Listener

from query_cleaner import get_clean_application


class DataplaneDriver(object):
    def __init__(self, dpd_socket, internal_interfaces, metrics_file="test"):
        self.dpd_socket = dpd_socket

        self.targets = dict()
        self.metrics_log_file = metrics_file
        self.internal_interfaces = internal_interfaces

        # LOGGING
        log_level = logging.ERROR
        # add handler
        self.logger = logging.getLogger('DataplaneDriver')
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # initialize metrics logger
        # which is separate from debug logger

        self.initialize_metrics_logger()

    def initialize_metrics_logger(self):
        # create a logger for the object
        self.metrics = logging.getLogger(__name__)
        self.metrics.setLevel(logging.DEBUG)
        # create file handler which logs messages
        self.fh = logging.FileHandler(self.metrics_log_file + self.__class__.__name__)
        self.fh.setLevel(logging.DEBUG)
        self.metrics.addHandler(self.fh)

        # self.metrics.info('init')

    def start(self):
        self.logger.debug('starting the event listener')
        dpd_listener = Listener(tuple(self.dpd_socket))
        while True:
            conn = dpd_listener.accept()
            raw_data = conn.recv()
            message = pickle.loads(raw_data)
            for key in message.keys():
                if key == 'init':
                    start = "%.20f" % time.time()
                    self.logger.debug('received "init" message')
                    application = message[key][0]
                    target_id = message[key][1]
                    sonata_fields = message[key][2]
                    self.configure(application, target_id, sonata_fields)
                    # self.metrics.info("init" + ","+ str(len(application)) +"," + start +",%.20f" % time.time())
                elif key == 'delta':
                    # self.logger.debug('received "delta" message')
                    start = "%.20f" % time.time()
                    filter_update = message[key][0]
                    target_id = message[key][1]
                    # print "delta: dp_driver: ", filter_update
                    self.update_configuration(filter_update, target_id)
                    # self.metrics.info("delta" + ","+ str(len(filter_update)) +"," + start +",%.20f" % time.time())
                elif key == 'is_supported':
                    self.logger.debug('received "is_supported" message')
                    application = message[key][0]
                    target_id = message[key][1]
                    is_supported = self.is_supportable(application, target_id)
                    conn.send(is_supported)
                elif key == 'get_cost':
                    self.logger.debug('received "get_cost" message')
                    application = message[key][0]
                    target_id = message[key][1]
                    cost = self.get_cost(application, target_id)
                    conn.send(cost)
                else:
                    self.logger.error('Unsupported Key')
            conn.close()

    def add_target(self, target_type, tid, config):
        self.logger.info('adding new target of type %s with id %s' % (type, str(tid)))
        target = None
        if target_type == 'p4':
            from p4.p4_target import P4Target
            if 'em_conf' not in config or 'switch_conf' not in config:
                self.logger.error('missing configs')
                return
            em_config = config['em_conf']
            switch_config = config['switch_conf']
            target = P4Target(em_config, switch_config, self.internal_interfaces)
        elif target_type == 'p4_old':
            from p4_old.p4_target_old import P4Target
            if 'em_conf' not in config or 'switch_conf' not in config:
                self.logger.error('missing configs')
                return
            em_config = config['em_conf']
            switch_config = config['switch_conf']
            target = P4Target(em_config, switch_config)
        elif target_type == 'openflow':
            target = OFTarget()

        self.targets[tid] = target

    def is_supportable(self, application, target_id):
        target = self.get_target(target_id)

        supported_operators = target.get_supported_operators()
        self.logger.debug('target %s supports the following operators: %s' %
                          (str(target_id), ', '.join(supported_operators))
                          )

        for query_object in application.values():
            for operator in query_object.operators:
                self.logger.debug('trying to check if %s is supported.' % (operator.name,))
                if operator.name not in supported_operators:
                    return False
        return True

    def get_cost(self, application, target_id):
        target = self.get_target(target_id)

        return 999

    def configure(self, application, target_id, sonata_fields):
        # TODO integrate query cleaner
        clean_application = get_clean_application(application)
        # print "Cleaned: ", clean_application
        target = self.get_target(target_id)
        target.run(clean_application, sonata_fields)

    def update_configuration(self, filter_update, target_id):
        target = self.get_target(target_id)
        target.update(filter_update)

    def get_target(self, target_id):
        if target_id in self.targets:
            return self.targets[target_id]
        else:
            print "ERROR: Unknown Target"
        return None


def main():
    import json

    with open('/home/vagrant/dev/sonata/config.json') as json_data_file:
        data = json.load(json_data_file)
        # print(data)

    config = data["on_server"][data["is_on_server"]]["sonata"]


    BASEPATH = config["base_folder"]
    SONATA = 'SONATA-DEV'
    DP_DRIVER_CONF = config["fm_conf"]["fm_socket"]
    SPARK_ADDRESS = config["emitter_conf"]["spark_stream_address"]
    SNIFF_INTERFACE = config["emitter_conf"]["sniff_interface"]


    dpd = DataplaneDriver(DP_DRIVER_CONF, BASEPATH + SONATA + "/sonata/tests/macro_bench/results/dp_driver.log")
    p4_type = "p4"
    compiled_srcs = ''

    if p4_type == 'p4_old':
        compiled_srcs = 'recirculate'
    else:
        compiled_srcs = 'sequential'

    config = {
        'em_conf': {'spark_stream_address': SPARK_ADDRESS,
                    'spark_stream_port': 8989,
                    'sniff_interface': SNIFF_INTERFACE,
                    'log_file': BASEPATH + SONATA + "/sonata/tests/demos/reflection_dns/graph/emitter2.log"
                    },

        'switch_conf': {
            'compiled_srcs': BASEPATH + SONATA + '/sonata/tests/macro_bench/compiled_srcs/',
            'json_p4_compiled': 'compiled.json',
            'p4_compiled': 'compiled.p4',
            'p4c_bm_script': BASEPATH + 'p4c-bmv2/p4c_bm/__main__.py',
            'bmv2_path': BASEPATH + 'bmv2',
            'bmv2_switch_base': '/targets/simple_switch',
            'switch_path': '/simple_switch',
            'cli_path': '/sswitch_CLI',
            'thriftport': 22222,
            'p4_commands': 'commands.txt',
            'p4_delta_commands': 'delta_commands.txt'
        }
    }

    dpd.add_target(p4_type, 1, config)
    dpd.start()


if __name__ == '__main__':
    main()
