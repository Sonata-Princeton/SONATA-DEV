CLI_PATH=/home/vagrant/bmv2/tools/runtime_CLI.py

if [ $# -lt 1 ]; then
    echo "Please specify register index"
    exit 1
fi
register=$1
index=$2


#echo "register_read $register $index" | $CLI_PATH dnr.json 22222
echo "register_read $register $index" | $CLI_PATH --thrift-port 22222
