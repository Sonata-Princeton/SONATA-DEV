from subprocess import check_output, CalledProcessError
from tempfile import TemporaryFile

## Code Compilation
COMPILED_SRCS = "/home/arp/dev/fabric_manager/switch_config/compiled_srcs/"
JSON_P4_COMPILED = COMPILED_SRCS + "compiled.json"
P4_COMPILED = COMPILED_SRCS + "compiled.p4"
import subprocess

## Initialization of Switch
BMV2_PATH = "/home/arp/bmv2"
BMV2_SWITCH_BASE = BMV2_PATH + "/targets/simple_switch"

SWITCH_PATH = BMV2_SWITCH_BASE + "/simple_switch"
CLI_PATH = BMV2_SWITCH_BASE + "/sswitch_CLI"
THRIFTPORT = 22222

P4_COMMANDS = COMPILED_SRCS + "commands.txt"
P4_DELTA_COMMANDS = COMPILED_SRCS + "delta_commands.txt"


def reset_switch_state():
    cmd = "echo \'reset_state\' | " + CLI_PATH + " --thrift-port "+str(THRIFTPORT)
    print "Running ##########:" + cmd
    get_out(cmd)

def send_commands_to_dp(cli_path, p4_json_path, thrift_port, COMMAND_PATH):
    cmd = [cli_path, p4_json_path, str(thrift_port)]
    with open(COMMAND_PATH, "r") as f:
        print " ".join(cmd)
        try:
            output = subprocess.check_output(cmd, stdin = f)
            #print output
        except subprocess.CalledProcessError as e:
            print e
            print e.output
            #raise RuntimeError


def send_delta_commands_to_dp(cli_path, p4_json_path, thrift_port, commands):
    cmd = [cli_path, p4_json_path, str(thrift_port)]
    get_in(cmd, commands)

def get_out(args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t, shell=True)
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) +',' +t.read()
            #raise RuntimeError
            return False, t.read()


def write_to_file(path, content):
    with open(path, 'w') as fp:
        fp.write(content)


def get_in(args, input):
    with TemporaryFile() as t:
        try:
            t.write(input)
            out = check_output(args, stdin=t, shell=False)
            #print "SUCCESS: " + str(args) + ",0 ," + str(out)
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) +',' +t.read()
            #raise RuntimeError

            return False, t.read()
