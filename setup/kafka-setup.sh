#!/usr/bin/env bash

# Install and configure 'pycapa'
git clone https://github.com/mleef/pycapa.git;
cd pycapa;
sudo -H pip install -r requirements.txt;
sudo python setup.py install;
cd ../;
rm -rf pycapa;

# Kafka dependencies
sudo apt-get install -y default-jre
sudo apt-get install -y zookeeperd

# Kafka itself
wget http://mirror.olnevhost.net/pub/apache/kafka/0.10.1.0/kafka_2.10-0.10.1.0.tgz -P ~/Downloads

# Unpack Kafka
mkdir -p ~/kafka && cd ~/kafka
tar -xvzf ~/Downloads/kafka_2.10-0.10.1.0.tgz --strip 1

# Add config option to delete topics
echo "delete.topic.enable = true" >> ~/kafka/config/server.properties

# Add kafka logging output file
mkdir ~/Desktop
touch ~/Desktop/kafka.log

# Add shortcuts to ~/.bashrc
sudo bash -c "echo '' >> ~/.bashrc"
sudo bash -c "echo 'alias start_kafka_server=\"nohup ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties > ~/Desktop/kafka.log 2>&1\"' >> ~/.bashrc"
sudo bash -c "echo 'produce_func() {' >> ~/.bashrc"
sudo bash -c "echo '  echo \$1 | ~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic \$2 > /dev/null' >> ~/.bashrc"
sudo bash -c "echo '}' >> ~/.bashrc"
sudo bash -c "echo 'consume_func() {' >> ~/.bashrc"
sudo bash -c "echo '  ~/kafka/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic \$1' >> ~/.bashrc"
sudo bash -c "echo '}' >> ~/.bashrc"
sudo bash -c "echo 'alias produce=\"produce_func\"' >> ~/.bashrc"
sudo bash -c "echo 'alias consume=\"consume_func\"' >> ~/.bashrc"
sudo bash -c "echo 'alias start_pycapa=\"sudo pycapa -z localhost:2181 -t packets -d -i eth0\"' >> ~/.bashrc"