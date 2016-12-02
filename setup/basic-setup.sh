#!/usr/bin/env bash

while [ "$1" != "" ]; do
    if [ $1 = "--no-mininet" ]; then
	NO_MININET=1
    fi
    shift
done

# install packages
sudo apt-get -f -y install

sudo apt-get update

sudo apt-get install -y build-essential fakeroot debhelper autoconf \
automake libssl-dev graphviz python-all python-qt4 \
python-twisted-conch libtool git tmux vim python-pip python-paramiko \
python-sphinx mongodb dos2unix wireshark

sudo pip install -U pip

sudo pip install -r ~/dev/setup/pip-basic-requires

sudo apt-get install -y ssh git emacs sshfs graphviz feh
sudo apt-get install -y libstring-crc32-perl

echo 'PATH=$PATH:~/iSDX/bin' >> ~/.profile

if [ -z "$NO_MININET" ]; then
    # set up some shortcuts
    mkdir ~/bin/
    echo "sudo mn -c; sudo mn --topo single,3 --mac --switch ovsk --controller remote" > ~/bin/mininet.sh
    chmod 755 ~/bin/mininet.sh
fi
