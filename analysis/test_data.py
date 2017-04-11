import pickle
fname = 'data/hypothesis_graph_2_2017-04-11 02:32:08.513236.pickle'
fname = 'data/hypothesis_graph_6_2017-04-11 02:55:06.032332.pickle'

with open(fname,'r') as f:
    data = pickle.load(f)
    v,e = data[data.keys()[0]]
    print e[((0, 0, 0), (4, 0, 1))], e[((0, 0, 0), (4, 4, 1))], e[((4, 0, 1), (32, 0, 2))]

# fname = 'data/counts_2_2017-04-11 02:28:02.230536.pickle'
# with open(fname,'r') as f:
#     data = pickle.load(f)
#     print data[2][(0,4)]