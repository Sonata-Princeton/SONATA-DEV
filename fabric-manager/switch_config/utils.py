from subprocess import check_output, CalledProcessError

from tempfile import TemporaryFile

## Code Compilation
COMPILED_SRCS = "/home/vagrant/dev/fabric-manager/switch_config/compiled_srcs/"
JSON_P4_COMPILED = COMPILED_SRCS + "compiled.json"
P4_COMPILED = COMPILED_SRCS + "compiled.p4"

## Initialization of Switch
BMV2_PATH = "/home/vagrant/bmv2"
BMV2_SWITCH_BASE = BMV2_PATH + "/targets/simple_switch"

SWITCH_PATH = BMV2_SWITCH_BASE + "/simple_switch"
CLI_PATH = BMV2_SWITCH_BASE + "/sswitch_CLI"
THRIFTPORT = 22222

P4_COMMANDS = COMPILED_SRCS + "commands.txt"

def get_out(args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t, shell=True)
            #print "SUCCESS: " + args + ",0 ," + out + "\n"
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) + t.read()
            return False, t.read()
