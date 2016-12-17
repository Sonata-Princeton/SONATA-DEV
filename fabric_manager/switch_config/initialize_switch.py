#!/usr/bin/python

# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

logging.getLogger(__name__)

from utils import *
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from p4_mininet import P4Switch, P4Host
from time import sleep


class MyTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        logging.debug("Topology created")
        switch = self.addSwitch('s1',
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port,
                                pcap_dump = True)


def initialize_switch(behavioral_exe, p4_json_path, thrift_port, cli_path, p4_commands):
    topo = MyTopo(behavioral_exe,
                  p4_json_path,
                  thrift_port)

    net = Mininet(topo=topo,
                  host=P4Host,
                  switch=P4Switch,
                  controller=None)

    Intf("m-veth-1", net.get('s1'), 11)
    Intf("m-veth-2", net.get('s1'), 12)
    net.start()
    sleep(1)

    send_commands_to_dp(cli_path, p4_json_path, thrift_port, p4_commands)

    logging.info(p4_commands)

    sleep(1)

    logging.debug("SWITCH Ready !")

    #CLI(net)
    #net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    initialize_switch(SWITCH_PATH, JSON_P4_COMPILED, THRIFTPORT, CLI_PATH)
