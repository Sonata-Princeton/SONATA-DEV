from plotlib import *
import numpy as np
import pickle
import math

color_n=['r','b','k','g','m','k','w']
markers=['o','*','^','s','d','3','d','o','*','^','1','4']
linestyles=[ '-',':','--','-.','--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.']



def plot_cases():
    cases = [1,2,3,4]
    cases = [2]
    alpha = 0.5
    for case in cases:
        print "Case", case
        with open('case_'+str(case)+'_out_data.pickle','r') as f:
            data = pickle.load(f)
            if case == 1:
                def plot_line(xlab, data, err, XLabel, YLabel, fname):
                    my_locator = MaxNLocator(len(xlab))
                    fig = plt.figure()
                    ax = fig.add_subplot(1,1,1)

                    pl.errorbar(xlab, data, yerr=err, color=color_n[0],linestyle=linestyles[0], linewidth=2.0)

                    ax.yaxis.set_major_locator(my_locator)

                    pl.xlabel(XLabel)
                    pl.ylabel(YLabel)

                    if 'packets' in fname:
                        ax.set_ylim(ymax=1.1)
                    ax.set_ylim(ymin=0.0)
                    ax.grid(True)
                    plt.tight_layout()

                    plot_name = fname+'.eps'
                    pl.savefig(plot_name)

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
                        #print data[qid][alpha][ts]
                        if data[qid][alpha][ts][0][1] > 0:
                            d_n.append(float(data[qid][alpha][ts][0][0])/data[qid][alpha][ts][0][1])
                        if data[qid][alpha][ts][1][1] > 0:
                            d_b.append(float(data[qid][alpha][ts][1][0])/data[qid][alpha][ts][1][1])
                        #print data[qid][alpha][ts], d_n[-1], d_b[-1]

                    data_n.append(np.median(d_n))
                    err_n.append(np.std(d_n))

                    data_b.append(np.median(d_b))
                    err_b.append(np.std(d_b))

                print data_b, err_b
                print data_n, err_n
                plot_line(xlab, data_n, err_n, 'Number of Reduce Operators', 'Number of Packets (Normalized)', 'case1_packets')
                plot_line(xlab, data_b, err_b, 'Number of Reduce Operators', 'Number of Buckets (Normalized)', 'case1_buckets')


                print data.keys()

            elif case == 2:

                qid_2_nKeys = {0:1, 1:2, 2:2, 3:2, 4:2, 5:3, 6:3, 7:3, 8:3, 9:3, 10:3, 11:3, 12:3, 13:3, 14:3, 15:4}

                xlab = list(set(qid_2_nKeys.values()))[1:]
                xlab.sort()
                plot_data = {0:dict((x,[]) for x in xlab), 1:dict((x,[]) for x in xlab)}

                for qid in data:
                    n_keys = qid_2_nKeys[qid]
                    if n_keys in plot_data[0]:
                        for ts in data[qid][alpha]:
                            #print data[qid][alpha][ts]
                            if data[qid][alpha][ts][0][1] > 0:
                                tmp = float(data[qid][alpha][ts][0][0])/data[qid][alpha][ts][0][1]
                                plot_data[0][n_keys].append(tmp)
                            if data[qid][alpha][ts][1][1] > 0:
                                tmp = float(data[qid][alpha][ts][1][0])/data[qid][alpha][ts][1][1]
                                plot_data[1][n_keys].append(tmp)

                print plot_data[0].keys()

                plotCDF(plot_data[0], xlab, 'Number of Packets (Normalized)', 'CDF of Window Intervals', 'N/A', 'N/A', 'case2_packets', labels = None)
                plotCDF(plot_data[1], xlab, 'Number of Buckets (Normalized)', 'CDF of Window Intervals', 'N/A', 'N/A', 'case2_buckets', labels = None)



            elif case == 3:

                def plot_line(xlab, data, err, XLabel, YLabel, fname):
                    fig = plt.figure()
                    ax = fig.add_subplot(1,1,1)

                    pl.errorbar(xlab, data, yerr=err, color=color_n[0],linestyle=linestyles[0], linewidth=2.0)

                    ax.yaxis.set_major_locator(my_locator)

                    pl.xlabel(XLabel)
                    pl.ylabel(YLabel)

                    if 'packets' in fname:
                        ax.set_ylim(ymax=1.1)
                    ax.set_ylim(ymin=0.0)
                    ax.grid(True)
                    plt.tight_layout()

                    plot_name = fname+'.eps'
                    pl.savefig(plot_name)

                xlab = []
                data_n = []
                err_n = []
                data_b = []
                err_b = []
                ptile = [math.ceil(100.0*(1-x)) for x in [1, 0.8, 0.6, .4, .2, .01, 0.001]]
                xlab = ptile
                for qid in data:
                    d_n = []
                    d_b = []
                    for ts in data[qid][alpha]:
                        #print data[qid][alpha][ts]
                        if data[qid][alpha][ts][0][1] > 0:
                            d_n.append(float(data[qid][alpha][ts][0][0])/data[qid][alpha][ts][0][1])
                        if data[qid][alpha][ts][1][1] > 0:
                            d_b.append(float(data[qid][alpha][ts][1][0])/data[qid][alpha][ts][1][1])
                            #print data[qid][alpha][ts], d_n[-1], d_b[-1]

                    data_n.append(np.median(d_n))
                    err_n.append(np.std(d_n))

                    data_b.append(np.median(d_b))
                    err_b.append(np.std(d_b))
                #print xlab
                print xlab[:-1], data_n[:-1], err_n[:-1]
                print xlab[:-1], data_b[:-1], err_b[:-1]
                plot_line(xlab[:-1], data_n[:-1], err_n[:-1], 'Threshold (Percentile)', 'Number of Packets (Normalized)', 'case3_packets')
                plot_line(xlab[:-1], data_b[:-1], err_b[:-1], 'Threshold (Percentile)', 'Number of Buckets (Normalized)', 'case3_buckets')


                print data.keys()


def plot_case0():
    case = 0
    with open('case_'+str(case)+'_100_out_data.pickle','r') as f:
        output = pickle.load(f)
        # Get savings CDF
        plot_data = {0:{}, 1:{}}
        alphas = [0.001]
        #alphas = [0.0001, 0.001, 0.01, 0.1, 1.0]
        #alphas = [0, 0.01, 0.1, 0.25, 0.5, 0.75, 1.0]
        alphas = [0.1, 0.25, 0.5, 0.75]
        for qid in output:
            for alpha in alphas:
                if alpha not in plot_data[0]:
                    plot_data[0][alpha] = []
                    plot_data[1][alpha] = []
                for ts in output[qid][alpha]:
                    ((N,N_max), (B,B_max), _) = output[qid][alpha][ts]
                    plot_data[0][alpha].append(float(N)/N_max)
                    plot_data[1][alpha].append(float(B)/B_max)
        plotCDF(plot_data[0], alphas, 'Number of Packets (Normalized)', 'CDF of Queries',
                'N/A', 'N/A', 'case0_packets_cdf', labels = None, isLog = True)
        plotCDF(plot_data[1], alphas, 'Number of Buckets (Normalized)', 'CDF of Queries',
                'N/A', 'N/A', 'case0_buckets_cdf', labels = None, isLog = True)


def plot_static_case0():
    case = 0
    with open('case_'+str(case)+'_100_out_data.pickle','r') as f:
        output = pickle.load(f)
        with open('case_0_100_output_static_dp.pickle', 'r') as f:
            output_static_dp = pickle.load(f)
        with open('case_0_100_output_static_sp.pickle', 'r') as f:
            output_static_sp = pickle.load(f)
        # Get savings CDF
        plot_data = {0:{}, 1:{}, 2:{}}
        alphas = [0.001]
        #alphas = [0.0001, 0.001, 0.01, 0.1, 1.0]
        #alphas = [0, 0.01, 0.1, 0.25, 0.5, 0.75, 1.0]
        alphas = [0.1, 0.25, 0.5, 0.75]
        #alphas = [0.5]
        plot_data[0]['Static'] = []
        plot_data[1]['Static'] = []
        plot_data[2]['Static'] = []
        for qid in output:
            for alpha in alphas:
                if alpha not in plot_data[0]:
                    plot_data[0][alpha] = []
                    plot_data[1][alpha] = []
                    plot_data[2][alpha] = []
                for ts in output[qid][alpha]:
                    ((N,N_max), (B,B_max), delay) = output[qid][alpha][ts]
                    plot_data[0][alpha].append(float(N)/N_max)
                    plot_data[1][alpha].append(float(B)/B_max)
                    plot_data[2][alpha].append(delay)
        for ts in output_static_dp[qid][alpha]:
            ((N,N_max), (B,B_max), delay) = output_static_dp[qid][alpha][ts]
            plot_data[1]['Static'].append(float(B)/B_max)
            #plot_data[0]['Static'].append(float(N)/N_max)
            plot_data[2]['Static'].append(delay)

        for ts in output_static_sp[qid][alpha]:
            ((N,N_max), (B,B_max), delay) = output_static_sp[qid][alpha][ts]
            plot_data[0]['Static'].append(float(N)/N_max)

        plotCDF(plot_data[0], alphas+['Static'], 'Number of Packets (Normalized)',
                'CDF of Queries', 'N/A', 'N/A', 'case0_packets_static_cdf', labels = None, isLog = True)
        plotCDF(plot_data[1], alphas+['Static'], 'Number of Buckets (Normalized)',
                'CDF of Queries', 'N/A', 'N/A', 'case0_buckets_static_cdf', labels = None, isLog = True)
        plotCDF(plot_data[2], alphas+['Static'], 'Detection Delay (second)',
                'CDF of Queries', 'N/A', 'N/A', 'case0_delay_static_cdf', labels = None)

def plot_alpha_search():
    with open('case_0_learned_nfrac_2_alpha.pickle','r') as f:
        output = pickle.load(f)
        fracs = [0.001, 0.01, 0.1, 0.25, 0.5]
        plot_data = {}
        for qid in output:
            for ts in output[qid]:
                for f in fracs:
                    if f not in plot_data:
                        plot_data[f] = []
                    plot_data[f].append(output[qid][ts][f])
        plotCDF(plot_data, fracs, 'alpha',
                'CDF of Queries', 1, 0, 'case0_alpha_cdf', labels = None)




if __name__ == '__main__':
    #plot_cases()
    #plot_case0()
    #plot_static_case0()
    plot_alpha_search()