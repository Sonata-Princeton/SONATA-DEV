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
from mininet.log import setLogLevel
from mininet.cli import CLI

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep
import os
import subprocess

## Initialization of Switch
BMV2_PATH = "/home/vagrant/bmv2"
BMV2_SWITCH_BASE = BMV2_PATH + "/targets/simple_switch"

SWITCH_PATH = BMV2_SWITCH_BASE + "/simple_switch"
CLI_PATH = BMV2_SWITCH_BASE + "/sswitch_CLI"
THRIFTPORT = 22222

_THIS_DIR = os.path.dirname(os.path.realpath(__file__))
_THRIFT_BASE_PORT = 22222

BASE_PATH = "training_data/micro/"

class MyTopo(Topo):
    def __init__(self, sw_path, json_path, nb_hosts, nb_switches, links, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        for i in xrange(nb_switches):
           self.addSwitch('s%d' % (i + 1),
                            sw_path = sw_path,
                            json_path = json_path,
                            thrift_port = _THRIFT_BASE_PORT + i,
                            pcap_dump = True,
                            device_id = i)

        for h in xrange(nb_hosts):
            self.addHost('h%d' % (h + 1), ip="10.0.0.%d" % (h + 1),
                    mac="00:00:00:00:00:0%d" % (h+1))

        for a, b in links:
            self.addLink(a, b)


def read_topo():
    nb_hosts = 0
    nb_switches = 0
    links = []
    with open(BASE_PATH + "topo.txt", "r") as f:
        line = f.readline()[:-1]
        w, nb_switches = line.split()
        assert(w == "switches")
        line = f.readline()[:-1]
        w, nb_hosts = line.split()
        assert(w == "hosts")
        for line in f:
            if not f: break
            a, b = line.split()
            links.append( (a, b) )
    return int(nb_hosts), int(nb_switches), links


def initialize_switch(p4_json_path=BASE_PATH + "join.json", behavioral_exe=SWITCH_PATH, thrift_port=THRIFTPORT, cli_path=CLI_PATH):
    nb_hosts, nb_switches, links = read_topo()

    topo = MyTopo(behavioral_exe,
                  p4_json_path,
                  nb_hosts, nb_switches, links)

    net = Mininet(topo=topo,
                  host=P4Host,
                  switch=P4Switch,
                  controller=None)
    net.start()

    for n in xrange(nb_hosts):
        h = net.get('h%d' % (n + 1))
        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload eth0 %s off" % off
            print cmd
            h.cmd(cmd)
        print "disable ipv6"
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv4.tcp_congestion_control=reno")
        h.cmd("iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP")

    sleep(2)

    for i in xrange(nb_switches):
        cmd = [cli_path, p4_json_path, str(thrift_port)]
        with open(BASE_PATH + "commands.txt", "r") as f:
            print " ".join(cmd)
            try:
                output = subprocess.check_output(cmd, stdin=f)
                print output
            except subprocess.CalledProcessError as e:
                print e
                print e.output

    sleep(1)

    print "Ready !"

    #CLI( net )
    #net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    initialize_switch()
