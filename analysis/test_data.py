import pickle
fname = 'data/data/hypothesis_graph_2_2017-04-09 14:51:55.766276.pickle'

with open(fname,'r') as f:
    data = pickle.load(f)
    print data