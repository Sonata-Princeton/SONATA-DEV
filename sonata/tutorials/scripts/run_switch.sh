#!/bin/bash

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

#THIS_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

#source env.sh

BMV2_PATH=/home/vagrant/bmv2
# e.g. BMV2_PATH=$THIS_DIR/../bmv2
P4C_BM_PATH=/home/vagrant/p4c-bmv2
# e.g P4C_BM_PATH=$THIS_DIR/../p4c-bm
P4C_BM_SCRIPT=$P4C_BM_PATH/p4c_bm/__main__.py


SWITCH_PATH=$BMV2_PATH/targets/simple_switch/simple_switch

CLI_PATH=$BMV2_PATH/targets/simple_switch/sswitch_CLI

# create CPU port
intf0="m-veth-1"
intf1="out-veth-1"
if ! ip link show $intf0 &> /dev/null; then
    ip link add name $intf0 type veth peer name $intf1
    ip link set dev $intf0 up
    ip link set dev $intf1 up
    TOE_OPTIONS="rx tx sg tso ufo gso gro lro rxvlan txvlan rxhash"
    for TOE_OPTION in $TOE_OPTIONS; do
        /sbin/ethtool --offload $intf0 "$TOE_OPTION" off
        /sbin/ethtool --offload $intf1 "$TOE_OPTION" off
    done
fi
sysctl net.ipv6.conf.$intf0.disable_ipv6=1
sysctl net.ipv6.conf.$intf1.disable_ipv6=1

# create CPU port
intf2="m-veth-2"
intf3="out-veth-2"
if ! ip link show $intf2 &> /dev/null; then
    ip link add name $intf2 type veth peer name $intf3
    ip link set dev $intf2 up
    ip link set dev $intf3 up
    TOE_OPTIONS="rx tx sg tso ufo gso gro lro rxvlan txvlan rxhash"
    for TOE_OPTION in $TOE_OPTIONS; do
        /sbin/ethtool --offload $intf2 "$TOE_OPTION" off
        /sbin/ethtool --offload $intf3 "$TOE_OPTION" off
    done
fi
sysctl net.ipv6.conf.$intf2.disable_ipv6=1
sysctl net.ipv6.conf.$intf3.disable_ipv6=1


#$P4C_BM_SCRIPT p4src/distinct.p4 --json distinct.json
# This gives libtool the opportunity to "warm-up"
$SWITCH_PATH >/dev/null 2>&1
PYTHONPATH=$PYTHONPATH:$BMV2_PATH/mininet/ python scripts/create_topology.py \
    --p4-path $1 \
    --behavioral-exe $SWITCH_PATH \
    --json $1/plan.json \
    --cli $CLI_PATH \
    --thrift-port 22222


echo "Done"