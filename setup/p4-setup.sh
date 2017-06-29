#!/usr/bin/env bash

cd ~

git clone https://github.com/p4lang/behavioral-model.git bmv2
git clone https://github.com/p4lang/p4c-bm.git p4c-bmv2


cd p4c-bmv2
sudo -H pip install -r requirements.txt

sudo apt-get -yf install

cd ~/bmv2/
sudo  ./install_deps.sh
./autogen.sh
./configure
make
sudo make install

cd ~
sudo apt-get install mininet
sudo -H pip install scapy thrift networkx
