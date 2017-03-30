#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
import pickle

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


def get_plans_intensity(Ns, Bs, unique_plans):
    intensity = []
    ctr = 0
    for n in Ns:
        intensity.append([])
        for b in Bs:
            x = -1
            for plan in unique_plans:
                if (n, b) in unique_plans[plan]:
                    x = 1 * (1 + unique_plans.keys().index(plan))
                    print n, b, plan, x
                    break
            intensity[ctr].append(x)
        ctr += 1

    return intensity


def plot_data():
    # fname = 'data/alpha_tuning_dump_2017-03-29 20:07:13.376800.pickle'
    fname = 'data/alpha_tuning_dump_2017-03-30 11:33:50.334231.pickle'
    with open(fname, 'r') as f:
        data_dump = pickle.load(f)
        for mode in data_dump:
            (Ns, Bs, operational_alphas, unique_plans) = data_dump[mode]
            print unique_plans.keys()
            intensity_alpha = get_alpha_intensity(Ns, Bs, operational_alphas)
            intensity_plans = get_plans_intensity(Ns, Bs, unique_plans)
            heatmap_plot(Ns, Bs, intensity_alpha, 'Nmax (Kpps)', 'Bmax (Kb)', 'data/heatmap_alpha_'+str(mode)+'.pdf')
            heatmap_plot(Ns, Bs, intensity_plans, 'Nmax (Kpps)', 'Bmax (Kb)', 'data/heatmap_plans_'+str(mode)+'.pdf')


if __name__ == '__main__':
    plot_data()