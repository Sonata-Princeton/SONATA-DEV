CLI_PATH=/home/vagrant/bmv2/targets/simple_switch/sswitch_CLI

if [ $# -lt 1 ]; then
    echo "Please specify register index"
    exit 1
fi
register=$1
index=$2


echo "register_read $register $index" | $CLI_PATH dnr.json 22222
