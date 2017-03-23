# Training related parameters
ALPHA = .93
BETA = 0.5
GRAN = 16
GRAN_MAX = 33

# Fold size for learning
FOLD_SIZE = 10

# 1 second window length
T = 1

# Error probability for approximate counts
DELTA = 0.01
# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes", "proto", "sMac", "dMac"]
# training data path
TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv'
TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv/part-00496'
# refinement levels
REFINEMENT_LEVELS = range(0, 33, 4)
#REFINEMENT_LEVELS = range(0, 33, 16)
#REFINEMENT_LEVELS = [0, 4,32]
QG_FNAME = '/home/vagrant/dev/training_data/dns_reflection/query_generator_object_reflection_1.pickle'
CM_FNAME = '/home/vagrant/dev/training_data/weights_udp.pickle'

TARGET_SP = 'SPARK'
TARGET_DP = 'P4'
TARGET_DP_ID = 1

DP_CONFIG = {
    'em_conf': None,
    'dpd_socket':('localhost', 6666),
    'switch_conf': {
        'compiled_srcs': '/home/vagrant/sonata/dataplane_driver/p4/compiled_srcs/',
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
}
