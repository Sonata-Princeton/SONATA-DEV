#!/usr/bin/env python

import logging
import pickle

from multiprocessing.connection import Listener

from query_cleaner import get_clean_application

from openflow.openflow import OFTarget
# from p4.p4_target import P4Target


BASEPATH = '/home/vagrant/'
SONATA = 'dev'
DP_DRIVER_CONF = ('localhost', 6666)

class DataplaneDriver(object):
    def __init__(self, dpd_socket, metrics_file):
        self.dpd_socket = dpd_socket

        self.targets = dict()
        self.metrics_log_file = metrics_file

        # LOGGING
        log_level = logging.DEBUG
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
        self.metrics.setLevel(logging.INFO)
        # create file handler which logs messages
        self.fh = logging.FileHandler(self.metrics_log_file)
        self.fh.setLevel(logging.INFO)
        self.metrics.addHandler(self.fh)

        self.metrics.info('init')

    def start(self):
        self.logger.debug('starting the event listener')
        dpd_listener = Listener(self.dpd_socket)
        while True:
            conn = dpd_listener.accept()
            raw_data = conn.recv()
            message = pickle.loads(raw_data)
            for key in message.keys():
                if key == 'init':
                    self.logger.debug('received "init" message')
                    application = message[key][0]
                    target_id = message[key][1]
                    print "application", application
                    self.configure(application, target_id)
                elif key == 'delta':
                    # self.logger.debug('received "delta" message')
                    filter_update = message[key][0]
                    target_id = message[key][1]
                    self.update_configuration(filter_update, target_id)
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
            target = P4Target(em_config, switch_config)
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
                self.logger.debug('trying to check if %s is supported.' % (operator.name, ))
                if operator.name not in supported_operators:
                    return False
        return True

    def get_cost(self, application, target_id):
        target = self.get_target(target_id)

        return 999

    def configure(self, application, target_id):
        print application
        # TODO integrate query cleaner
        clean_application = get_clean_application(application)
        print "Cleaned: ", clean_application
        target = self.get_target(target_id)
        target.run(clean_application)

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

    dpd = DataplaneDriver(DP_DRIVER_CONF, BASEPATH + SONATA +"/sonata/tests/micro_seq_recirculate/results/dp_driver.log")
    p4_type = 'p4_old'
    compiled_srcs = ''

    if p4_type == 'p4_old': compiled_srcs = 'recirculate'
    else: compiled_srcs = 'sequential'

    config = {
        'em_conf': {},
        'switch_conf': {
            'compiled_srcs': BASEPATH + SONATA +'/sonata/tests/micro_seq_recirculate/'+compiled_srcs+'/compiled_srcs/',
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
