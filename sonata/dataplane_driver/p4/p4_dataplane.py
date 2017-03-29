import logging

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink, Intf

import sys
sys.path.append("/home/vagrant/bmv2/mininet")

from p4_mininet import P4Switch, P4Host
from time import sleep

import subprocess

from interfaces import Interfaces
from utils import get_out, get_in


class P4DataPlane(object):
    def __init__(self, interfaces, switch_path, cli_path, thrift_port, bm_script):
        self.interfaces = interfaces
        self.switch_path = switch_path
        self.cli_path = cli_path
        self.thrift_port = thrift_port
        self.bm_script = bm_script

        # LOGGING
        log_level = logging.WARNING
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

        cmd = self.switch_path + " >/dev/null 2>&1"
        get_out(cmd)

        self.logger.info('start mininet topology')
        topo = P4Topo(self.switch_path,
                      p4_json_path,
                      self.thrift_port)

        net = Mininet(topo=topo,
                      host=P4Host,
                      switch=P4Switch,
                      controller=None)

        Intf("m-veth-1", net.get('s1'), 11)
        Intf("m-veth-2", net.get('s1'), 12)
        net.start()
        sleep(1)

        self.send_commands(p4_json_path, p4_commands_path)

        sleep(1)

    def create_interfaces(self):
        self.logger.info('create interfaces')
        for key in self.interfaces.keys():
            inter = Interfaces(self.interfaces[key][0], self.interfaces[key][1])
            inter.setup()

    def reset_switch_state(self):
        self.logger.info('reset switch state')
        cmd = "echo \'reset_state\' | " + self.cli_path + " --thrift-port "+str(self.thrift_port)
        # print "Running ##########:" + cmd
        get_out(cmd)

    def send_commands(self, p4_json_path, command_path):
        self.logger.info('send commands')
        cmd = [self.cli_path, p4_json_path, str(self.thrift_port)]
        with open(command_path, "r") as f:
            # print " ".join(cmd)
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


class P4Topo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1',
                                sw_path=sw_path,
                                json_path=json_path,
                                thrift_port=thrift_port,
                                pcap_dump=True)

