
# 1 second window length
T = 1
# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes", "proto", "sMac", "dMac"]
# training data path
TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv'
TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv/part-00496'
# refinement levels
REFINEMENT_LEVELS = range(0, 33, 8)
#REFINEMENT_LEVELS = range(0, 33, 16)
REFINEMENT_LEVELS = [0, 4,32]
QG_FNAME = '/home/vagrant/dev/training_data/dns_reflection/query_generator_object_reflection_1.pickle'
CM_FNAME = '/home/vagrant/dev/training_data/weights_udp.pickle'