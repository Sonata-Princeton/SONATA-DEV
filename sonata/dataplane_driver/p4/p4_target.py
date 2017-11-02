#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


from collections import namedtuple
from threading import Thread
import logging
from emitter.emitter import Emitter
from p4_application import P4Application
from p4_dataplane import P4DataPlane
from sonata.dataplane_driver.utils import get_logger
from sonata.dataplane_driver.utils import write_to_file


Operator = namedtuple('Operator', 'name keys')


class P4Target(object):
    def __init__(self, em_conf, target_conf, internal_interfaces):
        self.em_conf = em_conf

        # Code Compilation
        self.COMPILED_SRCS = target_conf['compiled_srcs']
        self.JSON_P4_COMPILED = self.COMPILED_SRCS + target_conf['json_p4_compiled']
        self.P4_COMPILED = self.COMPILED_SRCS + target_conf['p4_compiled']
        self.P4C_BM_SCRIPT = target_conf['p4c_bm_script']
        self.internal_interfaces = internal_interfaces
        # Initialization of Switch
        self.BMV2_PATH = target_conf['bmv2_path']
        self.BMV2_SWITCH_BASE = self.BMV2_PATH + target_conf['bmv2_switch_base']

        self.SWITCH_PATH = self.BMV2_SWITCH_BASE + target_conf['switch_path']
        self.CLI_PATH = self.BMV2_SWITCH_BASE + target_conf['cli_path']
        self.THRIFTPORT = target_conf['thriftport']

        self.P4_COMMANDS = self.COMPILED_SRCS + target_conf['p4_commands']
        self.P4_DELTA_COMMANDS = self.COMPILED_SRCS + target_conf['p4_delta_commands']

        # interfaces
        self.interfaces = {
            'receiver': ['m-veth-1', 'out-veth-1'],
            'sender': ['m-veth-2', 'out-veth-2'],
            'original': ['m-veth-3', 'out-veth-3']
        }

        self.supported_operations = ['Map', 'Filter', 'Reduce', 'Distinct']

        # LOGGING
        log_level = logging.DEBUG
        self.logger = get_logger('P4Target', 'DEBUG')
        self.logger.setLevel(log_level)
        self.logger.info('init')

        # init dataplane
        self.dataplane = P4DataPlane(self.interfaces,
                                     self.SWITCH_PATH,
                                     self.CLI_PATH,
                                     self.THRIFTPORT,
                                     self.P4C_BM_SCRIPT,
                                     self.internal_interfaces)

        # p4 app object
        self.app = None

    def get_supported_operators(self):
        return self.supported_operations

    def run(self, app, sonata_fields):
        self.logger.info('run')
        # compile app to p4
        self.logger.info('init P4 application object')
        self.app = P4Application(app, sonata_fields)

        self.logger.info('generate p4 code and commands')
        p4_src = self.app.get_p4_code()
        write_to_file(self.P4_COMPILED, p4_src)

        p4_commands = self.app.get_commands()
        commands_string = "\n".join(p4_commands)
        # self.logger.info("Commands: " + commands_string)
        write_to_file(self.P4_COMMANDS, commands_string)

        # compile p4 to json
        self.logger.info('compile p4 code to json')
        # TODO: uncomment this line
        self.dataplane.compile_p4(self.P4_COMPILED, self.JSON_P4_COMPILED)

        # initialize dataplane and run the configuration
        self.logger.info('initialize the dataplane with the json configuration')
        # TODO: uncomment this line
        self.dataplane.initialize(self.JSON_P4_COMPILED, self.P4_COMMANDS)

        # start the emitter
        if self.em_conf:
            self.logger.info('start the emitter')
            em = Emitter(self.em_conf, self.app.get_header_formats())
            em_thread = Thread(name='emitter', target=em.start)
            em_thread.setDaemon(True)
            em_thread.start()

    def update(self, filter_update):
        # self.logger.info('update')
        # Reset the data plane registers/tables before pushing the new delta config
        # print "reset dataplane"
        self.dataplane.reset_switch_state()
        self.dataplane.send_commands(self.JSON_P4_COMPILED, self.P4_COMMANDS)

        # Get the commands to add new filter flow rules
        if filter_update != {}:
            commands = self.app.get_update_commands(filter_update)
            commands_string = "\n".join(commands)
            print "Update Filter Tables: " + commands_string
            write_to_file(self.P4_DELTA_COMMANDS, commands_string)
            self.dataplane.send_commands(self.JSON_P4_COMPILED, self.P4_DELTA_COMMANDS)

