#!/usr/bin/env bash

cd ~
sudo apt-get update && sudo apt-get install -y graphviz autoconf automake bzip2 debhelper dh-autoreconf libssl-dev libtool openssl procps python-all python-qt4 python-twisted-conch python-zopeinterface

wget http://openvswitch.org/releases/openvswitch-2.5.1.tar.gz
tar xf openvswitch-2.5.1.tar.gz
pushd openvswitch-2.5.1
DEB_BUILD_OPTIONS='parallel=8 nocheck' fakeroot debian/rules binary
popd
sudo dpkg -i openvswitch-common*.deb openvswitch-datapath-dkms*.deb python-openvswitch*.deb openvswitch-pki*.deb openvswitch-switch*.deb
rm -rf *openvswitch*
cd ~
