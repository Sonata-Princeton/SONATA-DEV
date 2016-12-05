## Kafka Integration

NOTE: This can all be done automatically using [this](https://github.com/agupta13/Sonata/blob/master/dev/setup/kafka-setup.sh) script which is executed during provisioning.

1. Install Kafka (I used [this](https://www.digitalocean.com/community/tutorials/how-to-install-apache-kafka-on-ubuntu-14-04) tutorial).
2. Clone and install my modified version of 'pycapa' (ported for compatibility with latest version of kafka-python) found [here](https://github.com/mleef/pycapa). 
3. Add some useful debugging/testing commands (below) to your ~/.bashrc file (assuming your kafka installation is at ~/kafka)
4. With running Zookeeper and Kafka instances, you can now run consume_packets.py.

# ~/.bashrc suggestions
```bash
# Kafka commands
# Make sure zookeeper instance is running before starting kafka server
alias start_kafka_server='nohup ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties > ~/Desktop/kafka.log 2>&1'

# Usage: produce [message] [topic]
# Example: produce "Hello world!" new-topic (topics are auto created if they don't exist yet)
produce_func() {
  echo $1 | ~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic $2 > /dev/null
}

# Usage: consume [topic]
# Example: consume new-topic
consume_func() {
  ~/kafka/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic $1
}

alias produce=produce_func
alias consume=consume_func

# Last argument should be a network interface on your machine
alias start_pycapa='sudo pycapa -z localhost:2181 -t packets -d -i enp0s3'
```