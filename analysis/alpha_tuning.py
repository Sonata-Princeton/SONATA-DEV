#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle


def alpha_tuning(Ns, Bs):
    from sonata.core.training.learn.learn import Learn
    with open('hypothesis_graph.pickle', 'r') as f:
        G = pickle.load(f)
        # print G
        operational_alphas = {}
        unique_plans = {}
        for n_max in Ns:
            for b_max in Bs:
                alpha = 0.5
                beta = 0
                ctr = 0
                while True:
                    # print alpha
                    operational_alphas[(n_max, b_max)] = alpha
                    learn = Learn(G, alpha, beta, n_max, b_max)
                    # print alpha, n_max, learn.n_viol, b_max,  learn.b_viol
                    if not learn.n_viol and learn.b_viol:
                        alpha = (alpha) / 2
                    elif learn.n_viol and not learn.b_viol:
                        alpha = (1 + alpha) / 2

                    elif learn.n_viol and learn.b_viol:
                        operational_alphas[(n_max, b_max)] = -1
                        break
                    else:
                        # print learn.final_plan.path
                        path_string = learn.final_plan.__repr__()
                        if path_string not in unique_plans:
                            unique_plans[path_string] = {}
                        unique_plans[path_string][(n_max, b_max)] = alpha
                        break
                    ctr += 1
                    if ctr == 10:
                        operational_alphas[(n_max, b_max)] = -1
                        break
                if ctr < 10:
                    print ctr, n_max, b_max, operational_alphas[(n_max, b_max)], learn.final_plan.path
                    # return 0
        # print operational_alphas
        print [(k, len(v)) for k, v in unique_plans.iteritems()]

        return operational_alphas, unique_plans


def heatmap_plot(X, Y, data, xlabel, ylabel, plot_name):
    import matplotlib
    matplotlib.rc('text')
    matplotlib.use('Agg')
    from matplotlib import rc_file
    rc_file('analysis/matplotlibrc')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import MaxNLocator
    my_locator = MaxNLocator(6)

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
    plt.pcolormesh(x, y, intensity)
    plt.axis([x.min(), x.max(), y.min(), y.max()])
    plt.colorbar()  # need a colorbar to show the intensity scale
    plt.savefig(plot_name)


def get_intensity(Ns, Bs, operational_alphas):
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
    with open('alpha_tuning_dump.pickle', 'r') as f:
        (Ns, Bs, operational_alphas, unique_plans) = pickle.load(f)
        print unique_plans.keys()
        intensity_alpha = get_intensity(Ns, Bs, operational_alphas)
        intensity_plans = get_plans_intensity(Ns, Bs, unique_plans)
        # heatmap_plot(Ns, Bs, intensity_alpha, 'N_max', 'B_max', 'heatmap_alpha.pdf')
        heatmap_plot(Ns, Bs, intensity_plans, 'Nmax (Kpps)', 'Bmax (Kb)', 'heatmap_plans.pdf')


def generate_data():
    # Ns = [1500]
    # Bs = [16100]
    Ns = range(100, 5100, 100)
    Bs = range(1000, 51000, 1000)
    operational_alphas, unique_plans = alpha_tuning(Ns, Bs)
    data_dump = (Ns, Bs, operational_alphas, unique_plans)
    with open('alpha_tuning_dump.pickle', 'w') as f:
        pickle.dump(data_dump, f)


if __name__ == '__main__':
    # generate_data()
    plot_data()
