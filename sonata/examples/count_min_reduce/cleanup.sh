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

if [[ $EUID -ne 0 ]]; then
    echo "This script should be run using sudo or as the root user"
    exit 1
fi

killall lt-simple_switch &> /dev/null
mn -c &> /dev/null
intf="cpu-veth-0"
if ip link show $intf &> /dev/null; then
  ip link delete $intf type veth
fi
