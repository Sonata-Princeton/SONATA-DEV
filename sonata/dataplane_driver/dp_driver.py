#!/usr/bin/env python

import logging
import pickle

from multiprocessing.connection import Listener

from openflow.openflow import OFTarget
from p4.p4_target import P4Target


#TODO ADD LOGGING

class DataplaneDriver(object):
    def __init__(self, dpd_socket):
        self.dpd_socket = dpd_socket

        self.targets = dict()

        # LOGGING
        log_level = logging.DEBUG
        # add handler
        self.logger = logging.getLogger('DataplaneDriver')
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info('init')

    def start(self):
        self.logger.info('starting the event listener')
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
                    self.logger.debug('received "delta" message')
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

    def add_target(self, type, tid, config):
        self.logger.info('adding new target of type %s with id %s' % (type, str(tid)))
        target = None
        if type == 'p4':
            if 'em_conf' not in config or 'switch_conf' not in config:
                self.logger.error('missing configs')
                return
            em_config = config['em_conf']
            switch_config = config['switch_conf']
            target = P4Target(em_config, switch_config)
        elif type == 'openflow':
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
        target = self.get_target(target_id)
        target.run(application)

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
    pass


if __name__ == '__main__':
    main()
