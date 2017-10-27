import logging
import sys

from time import sleep

import subprocess

from interfaces import Interfaces
from sonata.dataplane_driver.utils import get_out, get_in
import threading,os

class Switch(threading.Thread):
    def __init__(self, p4_json_path, switch_path, internal_interfaces):
        threading.Thread.__init__(self)
        self.daemon = True
        self.switch_path = switch_path
        self.p4_json_path = p4_json_path
        self.internal_interfaces = internal_interfaces

    def run(self):
        compose_interfaces = ""
        for inter, port in self.internal_interfaces.iteritems():
            new_interface = " -i %s@%s " % (port, inter)
            compose_interfaces += new_interface

        COMMAND = "sudo %s %s %s --thrift-port 22222" % (self.switch_path, self.p4_json_path, compose_interfaces)
        os.system(COMMAND)


class P4DataPlane(object):
    def __init__(self, interfaces, switch_path, cli_path, thrift_port, bm_script, internal_interfaces):
        self.interfaces = interfaces
        self.switch_path = switch_path
        self.cli_path = cli_path
        self.thrift_port = thrift_port
        self.bm_script = bm_script
        self.internal_interfaces = internal_interfaces
        # LOGGING
        log_level = logging.DEBUG
        # add handler
        self.logger = logging.getLogger('P4DataPlane')
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info('init')

    def initialize(self, p4_json_path, p4_commands_path):
        self.logger.info('initialize')

        self.create_interfaces()

        get_out("sudo ps -ef | grep simple_switch | grep -v grep | awk '{print $2}' | sudo xargs kill -9")
        sleep(1)
        cmd = self.switch_path + " >/dev/null 2>&1"
        get_out(cmd)
        self.switch = Switch(p4_json_path, self.switch_path, self.internal_interfaces)
        self.switch.start()

        sleep(2)

        self.send_commands(p4_json_path, p4_commands_path)

        sleep(1)

    def create_interfaces(self):
        self.logger.info('create interfaces')
        for key in self.interfaces.keys():
            inter = Interfaces(self.interfaces[key][0], self.interfaces[key][1])
            inter.setup()

    def reset_switch_state(self):
        # self.logger.info('reset switch state')
        cmd = "echo \'reset_state\' | " + self.cli_path + " --thrift-port "+str(self.thrift_port)
        get_out(cmd)

    def send_commands(self, p4_json_path, command_path):
        # self.logger.info('send commands')
        cmd = [self.cli_path, p4_json_path, str(self.thrift_port)]

        with open(command_path, "r") as f:
            try:
                output = subprocess.check_output(cmd, stdin=f)
            except subprocess.CalledProcessError as e:
                print e
                print e.output

    def send_delta_commands(self, p4_json_path, commands):
        self.logger.info('send delta commands')
        cmd = [self.cli_path, p4_json_path, str(self.thrift_port)]
        get_in(cmd, commands)

    def compile_p4(self, p4_compiled, json_p4_compiled):
        self.logger.info('compile p4 to json')
        CMD = self.bm_script + " " + p4_compiled + " --json " + json_p4_compiled
        get_out(CMD)