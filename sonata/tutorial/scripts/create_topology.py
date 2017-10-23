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

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink, Intf

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep
import os
import subprocess

parser = argparse.ArgumentParser(description='Sonata demo')
parser.add_argument('--p4-path', help='Path to P4-code',
                    type=str, action="store", required=True)
parser.add_argument('--behavioral-exe', help='QueryPlan to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--json', help='QueryPlan to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--cli', help='QueryPlan to BM CLI',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", required=True)

args = parser.parse_args()

class MyTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        switch = self.addSwitch('s1',
                                sw_path=sw_path,
                                json_path=json_path,
                                thrift_port=thrift_port,
                                pcap_dump=False)


def main():
    topo = MyTopo(args.behavioral_exe,
                  args.json,
                  args.thrift_port)

    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)

    cpu_intf1 = Intf("m-veth-1", net.get('s1'), 11)
    cpu_intf2 = Intf("m-veth-2", net.get('s1'), 12)

    net.start()

    sleep(1)

    cmd = [args.cli, args.json, str(args.thrift_port)]
    with open(args.p4_path + "/commands.txt", "r") as f:
        print " ".join(cmd)
        try:
            output = subprocess.check_output(cmd, stdin = f)
            print output
        except subprocess.CalledProcessError as e:
            print e
            print e.output

    sleep(1)

    print "Ready !"

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()