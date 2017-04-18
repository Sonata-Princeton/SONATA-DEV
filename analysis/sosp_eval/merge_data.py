import pickle
import glob
#hypothesis_graph_6_min_8_2017-04-17 17:57:50.958863.pickle

def merge_files(qid):
    print "Merging qid:", qid
    intervals = range(60)
    files = glob.glob("data/hypothesis_graph_"+str(qid)+"_min_*.pickle")
    merged_data = {}
    for interval in intervals:
        fstring = 'hypothesis_graph_'+str(qid)+'_min_'+str(interval)
        tmp_fname =''
        for fname in files:
            if fstring in fname:
                tmp_fname = fname
                break
        with open(tmp_fname,'r') as f:
            G = pickle.load(f)
            print interval, len(G.keys()), G.keys()
            merged_data.update(G)
        print "Merged",  len(merged_data.keys())
    timestamps = merged_data.keys()
    timestamps.sort()
    # print timestamps
    out_fname = 'data/hypothesis_graph_'+str(qid)+'_merged_2017-04-17 17:57:50.958863.pickle'
    print out_fname
    with open(out_fname,'w') as f:
        pickle.dump(merged_data, f)


if __name__ == '__main__':
    qids = [1,6]
    for qid in qids:
        merge_files(qid)
