
# 1 second window length
T = 1
# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "sIP", "sPort", "dIP", "dPort", "nBytes",
                 "proto", "sMac", "dMac"]
# training data path
TD_PATH = '/home/vagrant/dev/data/anon_all_flows_1min.csv/part-00496'
# refinement levels
REFINEMENT_LEVELS = range(0, 33, 16)
QG_FNAME = '/home/vagrant/dev/query_training/dns_reflection/query_generator_object_reflection_1.pickle'