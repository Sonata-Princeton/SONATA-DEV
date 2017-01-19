from plotlib import *
import numpy as np
import pickle

def plot_line(xlab, data, err, XLabel, YLabel, fname):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)


    pl.errorbar(xlab, data, yerr=err)

    ax.yaxis.set_major_locator(my_locator)

    pl.xlabel(XLabel)
    pl.ylabel(YLabel)

    ax.grid(True)
    plt.tight_layout()

    plot_name = fname+'.eps'
    pl.savefig(plot_name)



def plot_cases():
    cases = [1,2,3,4]
    alpha = 0.05
    for case in cases:
        with open('case_'+str(case)+'_out_data.pickle','r') as f:
            data = pickle.load(f)
            if case == 1:
                xlab = []
                data_n = []
                err_n = []
                data_b = []
                err_b = []
                for qid in data:
                    print qid
                    n_reduce = qid+1
                    xlab.append(n_reduce)
                    d_n = []
                    d_b = []
                    for ts in data[qid][alpha]:
                        print data[qid][alpha][ts]
                        if data[qid][alpha][ts][0][1] > 0:
                            d_n.append(float(data[qid][alpha][ts][0][0])/data[qid][alpha][ts][0][1])
                        if data[qid][alpha][ts][1][1] > 0:
                            d_b.append(float(data[qid][alpha][ts][1][0])/data[qid][alpha][ts][1][1])
                        print data[qid][alpha][ts], d_n[-1], d_b[-1]

                    data_n.append(np.median(d_n))
                    err_n.append(np.std(d_n))

                    data_b.append(np.median(d_b))
                    err_b.append(np.std(d_b))

                print data_b, err_b
                print data_n, err_n
                plot_line(xlab, data_n, err_n, 'Number of Reduce Operators', 'Packets Savings', 'case1_packets')
                plot_line(xlab, data_b, err_b, 'Number of Reduce Operators', 'Buckets Savings', 'case1_buckets')


                print data.keys()



if __name__ == '__main__':
    plot_cases()