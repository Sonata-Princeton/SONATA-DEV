#!/usr/bin/env bash

while [ "$1" != "" ]; do
    if [ $1 = "--no-mininet" ]; then
	NO_MININET=1
    fi
    shift
done

cd ~

# Install Quagga
sudo apt-get install -y quagga
sudo apt-get install -f -y
sudo apt-get install -y quagga

sudo pip install -r ~/dev/setup/pip-sdx-requires

# Install SDX
# use existing iSDX that is mounted by Vagrant
#git clone https://github.com/sdn-ixp/iSDX.git
cd iSDX
sudo chmod 755 xrs/client.py xrs/route_server.py
mkdir xrs/ribs
dos2unix launch.sh xrs/client.py pctrl/clean.sh
cd ~
