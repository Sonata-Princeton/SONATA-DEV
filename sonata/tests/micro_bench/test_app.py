#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

from sonata.dataplane_driver.p4_old.p4_dataplane import P4DataPlane

batch_interval = 0.5
window_length = 1
sliding_interval = 1

RESULTS_FOLDER = '/home/vagrant/dev/sonata/tests/micro_bench/recirculate/'

featuresPath = ''
redKeysPath = ''

if __name__ == '__main__':

    p4_type = 'sequential'

    target_conf = {
        'compiled_srcs': '/home/vagrant/dev/sonata/tests/micro_bench/'+p4_type+'/compiled_srcs/',
        'json_p4_compiled': 'compiled.json',
        'p4_compiled': 'compiled.p4',
        'p4c_bm_script': '/home/vagrant/p4c-bmv2/p4c_bm/__main__.py',
        'bmv2_path': '/home/vagrant/bmv2',
        'bmv2_switch_base': '/targets/simple_switch',
        'switch_path': '/simple_switch',
        'cli_path': '/sswitch_CLI',
        'thriftport': 22222,
        'p4_commands': 'commands.txt',
        'p4_delta_commands': 'delta_commands.txt'
    }
    
    # Code Compilation
    COMPILED_SRCS = target_conf['compiled_srcs']
    JSON_P4_COMPILED = COMPILED_SRCS + target_conf['json_p4_compiled']
    P4_COMPILED = COMPILED_SRCS + target_conf['p4_compiled']
    P4C_BM_SCRIPT = target_conf['p4c_bm_script']

    # Initialization of Switch
    BMV2_PATH = target_conf['bmv2_path']
    BMV2_SWITCH_BASE = BMV2_PATH + target_conf['bmv2_switch_base']

    SWITCH_PATH = BMV2_SWITCH_BASE + target_conf['switch_path']
    CLI_PATH = BMV2_SWITCH_BASE + target_conf['cli_path']
    THRIFTPORT = target_conf['thriftport']

    P4_COMMANDS = COMPILED_SRCS + target_conf['p4_commands']
    P4_DELTA_COMMANDS = COMPILED_SRCS + target_conf['p4_delta_commands']

    # interfaces
    interfaces = {
        'receiver': ['m-veth-1', 'out-veth-1'],
        'sender': ['m-veth-2', 'out-veth-2'],
        'original': ['m-veth-3', 'out-veth-3']
    }


    dataplane = P4DataPlane(interfaces, SWITCH_PATH, CLI_PATH, THRIFTPORT, P4C_BM_SCRIPT)
    dataplane.compile_p4(P4_COMPILED, JSON_P4_COMPILED)

    # initialize dataplane and run the configuration
    dataplane.initialize(JSON_P4_COMPILED, P4_COMMANDS)