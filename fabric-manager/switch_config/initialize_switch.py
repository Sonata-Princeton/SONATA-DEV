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

from utils import *
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from p4_mininet import P4Switch, P4Host
from time import sleep
import subprocess


class MyTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        switch = self.addSwitch('s1',
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port,
                                pcap_dump = True)


def main(behavioral_exe, p4_json_path, thrift_port, cli_path):
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

    cmd = [cli_path, p4_json_path, str(thrift_port)]
    with open(P4_COMMANDS, "r") as f:
        print " ".join(cmd)
        try:
            output = subprocess.check_output(cmd, stdin = f, shell=False)
            print output
        except subprocess.CalledProcessError as e:
            print e
            print e.output

    sleep(1)

    print "Ready !"

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main(SWITCH_PATH, JSON_P4_COMPILED, THRIFTPORT, CLI_PATH)
