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

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential fakeroot debhelper autoconf \
automake libssl-dev graphviz python-all python-qt4 \
python-twisted-conch libtool git tmux vim python-pip python-paramiko \
python-sphinx mongodb dos2unix wireshark mysql-server

sudo -H pip install -U pip
sudo pip install --upgrade scipy
sudo -H pip install -r ~/dev/setup/pip-basic-requires

sudo apt-get install -y ssh git emacs sshfs graphviz feh Protobuf
sudo apt-get install -y libstring-crc32-perl xterm
sudo -H pip install mysql-connector==2.1.4

echo 'Defaults    env_keep += "PYTHONPATH"' | sudo tee --append /etc/sudoers
echo 'PATH=$PATH:~/iSDX/bin' >> ~/.profile
echo 'export PYTHONPATH=$PYTHONPATH:/home/vagrant/dev' >> ~/.profile
echo 'export PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet' >> ~/.profile
echo 'export SPARK_HOME=/home/vagrant/spark/' >> ~/.profile
sudo mysql -e "create database sonata;"
sudo mysql -e "use sonata; CREATE TABLE indexStore( id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, qid INT(6),  tuple VARCHAR(200), indexLoc INT(6) );"

mkdir ~/.vim

if [ -z "$NO_MININET" ]; then
    # set up some shortcuts
    mkdir ~/bin/
    echo "sudo mn -c; sudo mn --topo single,3 --mac --switch ovsk --controller remote" > ~/bin/mininet.sh
    chmod 755 ~/bin/mininet.sh
fi
