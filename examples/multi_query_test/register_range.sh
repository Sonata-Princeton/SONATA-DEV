CLI_PATH=/home/vagrant/bmv2/tools/runtime_CLI.py

if [ $# -lt 3 ]; then
    echo "USAGE: register_range NAME STARTINDEX ENDINDEX"
    exit 1
fi
register=$1
sindex=$2
eindex=$3

echo "register_range $register $sindex $eindex" | $CLI_PATH --thrift-port 22222
