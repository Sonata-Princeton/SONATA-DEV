CLI_PATH=/home/vagrant/bmv2/targets/simple_switch/sswitch_CLI

if [ $# -lt 1 ]; then
    echo "Please specify thrift port"
    exit 1
fi
tport=$1

$CLI_PATH --thrift-port $1
