#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
import pickle

from analysis.plotlib import plotLine, plotCDF

import matplotlib
matplotlib.rc('text')
matplotlib.use('Agg')
from matplotlib import rc_file
rc_file('analysis/matplotlibrc')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
my_locator = MaxNLocator(6)

def heatmap_plot(X, Y, data, xlabel, ylabel, plot_name):
    # here's our data to plot, all normal Python lists
    # x = [math.log(e, 10) for e in X]
    # y = [math.log(e, 10) for e in Y]
    x = [float(t) / 1000 for t in X]
    y = [float(t) / 1000 for t in Y]
    intensity = data

    # setup the 2D grid with Numpy
    x, y = np.meshgrid(x, y)

    # convert intensity (list of lists) to a numpy array for plotting
    intensity = np.array(intensity)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax.locator_params(nbins=6)
    plt.tight_layout()

    # now just plug the data into pcolormesh, it's that easy!
    plt.pcolormesh(x, y, intensity, cmap='gnuplot')
    plt.axis([x.min(), x.max(), y.min(), y.max()])
    plt.colorbar()  # need a colorbar to show the intensity scale
    plt.savefig(plot_name)


def get_alpha_intensity(Ns, Bs, operational_alphas):
    intensity = []
    ctr = 0
    for b in Bs:

        intensity.append([])
        for n in Ns:
            if n < 3000 and operational_alphas[(n, b)] > 0:
                print n,b, operational_alphas[(n, b)]
            intensity[ctr].append(operational_alphas[(n, b)])
        ctr += 1

    return intensity


def get_plans_intensity(Ns, Bs, unique_plans, operational_alphas):
    intensity = []
    ctr = 0
    for b in Bs:
        intensity.append([])
        for n in Ns:
            x = -1
            for plan in unique_plans:
                if (n, b) in unique_plans[plan]:
                    if operational_alphas[(n,b)] > 0:
                        x = 1 * (1 + unique_plans.keys().index(plan))
                    else:
                        x = 0
                    # print n, b, plan, x
                    break
            intensity[ctr].append(x)
        ctr += 1

    return intensity


def plot_heatmaps():
    # fname = 'data/alpha_tuning_dump_2017-03-29 20:07:13.376800.pickle'
    fname = 'data/alpha_tuning_dump_2017-03-30 11:33:50.334231.pickle'
    fname = 'data/alpha_tuning_dump_2017-03-30 17:17:07.283793.pickle'
    fname = 'data/alpha_tuning_dump_6_2017-04-09 15:55:47.505726.pickle'
    fname = 'data/alpha_tuning_dump_6_2017-04-12 15:54:52.662756.pickle'
    fname = 'data/alpha_tuning_dump_6_2017-04-12 21:19:28.906466.pickle'

    # Query 1 on caida 5mins and 10 seconds spark intervals
    fname = 'data/alpha_tuning_dump_1_2017-04-15 20:04:56.331188.pickle'
    with open(fname, 'r') as f:
        data_dump = pickle.load(f)
        for mode in data_dump:
            if mode in [2,3,4,5]:
                (Ns, Bs, operational_alphas, unique_plans) = data_dump[mode]
                print mode, unique_plans.keys()
                intensity_alpha = get_alpha_intensity(Ns, Bs[:-1], operational_alphas)
                print intensity_alpha
                intensity_plans = get_plans_intensity(Ns, Bs[:-1], unique_plans, operational_alphas)
                plot_fname1 = fname.split('.pickle')[0]+'_heatmap_alpha_'+str(mode)+'.pdf'
                plot_fname2 = fname.split('.pickle')[0]+'_heatmap_plans_'+str(mode)+'.pdf'
                print plot_fname1
                heatmap_plot(Ns, Bs[:-1], intensity_alpha, 'Nmax (Kpps)', 'Bmax (Kb)', plot_fname1)
                heatmap_plot(Ns, Bs, intensity_plans, 'Nmax (Kpps)', 'Bmax (Kb)', plot_fname2)


def plot_learning_curve():
    # fname = 'data/bias_var_analysis_2017-03-31 02:18:06.331508.pickle'
    fname = 'data/bias_var_analysis_2017-04-05 16:18:30.958175.pickle'
    with open(fname,'r') as f:
        data_dump = pickle.load(f)
        for mode in data_dump:
            for (n_max, b_max) in data_dump[mode]:
                iter_data = data_dump[mode][(n_max, b_max)]
                x = iter_data.keys()
                x.sort()
                x = x[:-1]
                y1 = [iter_data[elem][0] for elem in x]
                y2 = [iter_data[elem][1] for elem in x]
                data = {}
                data['Training Error'] = (x, y1)
                data['Test Error'] = (x, y2)
                print data
                order = ['Training Error', 'Test Error']
                plot_fname = 'data/lcurve_'+"_".join([str(x) for x in [mode,n_max,b_max]])+'.pdf'
                print plot_fname, data
                plotLine(data, order, 'Training Data Size (seconds)', 'RMSE (Cost)', 'N/A', 'N/A', plot_fname)


def plot_performance_graphs():
    fname = 'data/performance_gains_2017-04-05 23:14:51.499819.pickle'

    fname = 'data/performance_gains_2017-04-11 21:13:09.275776.pickle'
    fname = 'data/hypothesis_graph_6_2017-04-12 15:30:31.466226_performance_gains.pickle'

    fname = 'data/hypothesis_graph_1_2017-04-15 17:28:01.037231_performance_gains.pickle'
    with open(fname,'r') as f:
        data_dump = pickle.load(f)
        plot_ncost = {}
        plot_bcost = {}
        for mode in data_dump:
            if mode in [3,5]:
                plot_bcost[mode] = []
            if mode in [2,5]:
                plot_ncost[mode] = []

            for (n_max, b_max) in data_dump[mode]:
                if mode in [3,5]:
                    plot_bcost[mode] += [float(x[1])/1000 for x in data_dump[mode][(n_max, b_max)].values()]
                if mode in [2,5]:
                    plot_ncost[mode] += [float(x[0]) for x in data_dump[mode][(n_max, b_max)].values()]
        order_n = plot_ncost.keys()
        order_n.sort()
        order_b = plot_bcost.keys()
        order_b.sort()
        print np.median(plot_bcost[3]), np.median(plot_bcost[5])
        print 100*(np.median(plot_bcost[3])-np.median(plot_bcost[5]))/np.median(plot_bcost[3])
        plot_fname_ncost = fname.split('.pickle')[0]+'_ncost.pdf'
        plot_fname_bcost = fname.split('.pickle')[0]+'_bcost.pdf'
        print plot_fname_ncost, plot_fname_bcost
        plotCDF(plot_ncost, order_n, 'N (tuples/s)', 'Fraction of Intervals', 'N/A', 'N/A', plot_fname_ncost)
        plotCDF(plot_bcost, order_b, 'B (Kb)', 'Fraction of Intervals', 'N/A', 'N/A', plot_fname_bcost)


def plot_update_graphs():
    fname = 'data/updates_2017-04-06 20:33:41.885498.pickle'
    fname = 'data/updates_2017-04-11 20:20:55.226767.pickle'


    with open(fname,'r') as f:
        data_dump = pickle.load(f)
        plot_updates = {}
        for mode in data_dump:
            plot_updates[mode] = []
            for (n_max, b_max) in data_dump[mode]:
                plot_updates[mode] += [x for x in data_dump[mode][(n_max, b_max)].values()]
        order = plot_updates.keys()
        order.sort()
        plot_fname = fname.split('.pickle')[0]+'.pdf'
        plotCDF(plot_updates, order, 'Number of Updates', 'Fraction of Time', 'N/A', 0, 'data/plot_updates.pdf')



if __name__ == '__main__':
    # plot_heatmaps()
    #plot_learning_curve()
    plot_performance_graphs()
    # plot_update_graphs()