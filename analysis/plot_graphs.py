#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
import pickle

from analysis.plotlib import plotLine

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
    fname = 'data/bias_var_analysis_2017-03-31 02:18:06.331508.pickle'
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
                data['In'] = (x, y1)
                data['Out'] = (x, y2)
                order = ['In', 'Out']
                plot_fname = 'data/lcurve_'+"_".join([str(x) for x in [mode,n_max,b_max]])+'.pdf'
                print plot_fname, data
                plotLine(data, order, 'Training Data Size', 'RMSE', 'N/A', 'N/A', plot_fname)


if __name__ == '__main__':
    # plot_heatmaps()
    plot_learning_curve()