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
    for n in Ns:
        intensity.append([])
        for b in Bs:
            intensity[ctr].append(operational_alphas[(n, b)])
        ctr += 1

    return intensity


def get_plans_intensity(Ns, Bs, unique_plans, operational_alphas):
    intensity = []
    ctr = 0
    for n in Ns:
        intensity.append([])
        for b in Bs:
            x = -1
            for plan in unique_plans:
                if (n, b) in unique_plans[plan]:
                    if operational_alphas[(n,b)] > 0:
                        x = 1 * (1 + unique_plans.keys().index(plan))
                    else:
                        x = 0
                    print n, b, plan, x
                    break
            intensity[ctr].append(x)
        ctr += 1

    return intensity


def plot_heatmaps():
    # fname = 'data/alpha_tuning_dump_2017-03-29 20:07:13.376800.pickle'
    fname = 'data/alpha_tuning_dump_2017-03-30 11:33:50.334231.pickle'
    fname = 'data/alpha_tuning_dump_2017-03-30 17:17:07.283793.pickle'
    with open(fname, 'r') as f:
        data_dump = pickle.load(f)
        for mode in data_dump:
            (Ns, Bs, operational_alphas, unique_plans) = data_dump[mode]
            print mode, unique_plans.keys()
            intensity_alpha = get_alpha_intensity(Ns, Bs, operational_alphas)
            intensity_plans = get_plans_intensity(Ns, Bs, unique_plans, operational_alphas)
            heatmap_plot(Ns, Bs, intensity_alpha, 'Nmax (Kpps)', 'Bmax (Kb)', 'data/heatmap_alpha_'+str(mode)+'.png')
            heatmap_plot(Ns, Bs, intensity_plans, 'Nmax (Kpps)', 'Bmax (Kb)', 'data/heatmap_plans_'+str(mode)+'.png')


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
    with open(fname,'r') as f:
        data_dump = pickle.load(f)
        plot_ncost = {}
        plot_bcost = {}
        for mode in data_dump:
            plot_ncost[mode] = []
            plot_bcost[mode] = []
            for (n_max, b_max) in data_dump[mode]:
                plot_ncost[mode] += [float(x[0])/1000 for x in data_dump[mode][(n_max, b_max)].values()]
                plot_bcost[mode] += [float(x[1])/1000 for x in data_dump[mode][(n_max, b_max)].values()]
        order = plot_ncost.keys()
        order.sort()
        plotCDF(plot_ncost, order, 'N (K tuples/s)', 'Fraction of Time', 'N/A', 'N/A', 'data/plot_perf_ncost.pdf')
        plotCDF(plot_bcost, order, 'B (Kb)', 'Fraction of Time', 'N/A', 0, 'data/plot_perf_bcost.pdf')


def plot_update_graphs():
    fname = 'data/updates_2017-04-06 20:33:41.885498.pickle'
    with open(fname,'r') as f:
        data_dump = pickle.load(f)
        plot_updates = {}
        for mode in data_dump:
            plot_updates[mode] = []
            for (n_max, b_max) in data_dump[mode]:
                plot_updates[mode] += [x for x in data_dump[mode][(n_max, b_max)].values()]
        order = plot_updates.keys()
        order.sort()
        plotCDF(plot_updates, order, 'Number of Updates', 'Fraction of Time', 'N/A', 0, 'data/plot_updates.pdf')



if __name__ == '__main__':
    # plot_heatmaps()
    #plot_learning_curve()
    plot_performance_graphs()
    plot_update_graphs()