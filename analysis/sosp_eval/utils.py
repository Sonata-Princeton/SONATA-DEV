import pickle

from sonata.core.training.learn.learn import Learn
from analysis.utils import chunkify, get_training_graph
from analysis.plotlib import *


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

def heatmap_sub_plot(dataAll,fname):
    # here's our data to plot, all normal Python lists
    # x = [math.log(e, 10) for e in X]
    # y = [math.log(e, 10) for e in Y]

    data = dataAll[0]
    matplotlib.rcParams.update({'font.size': 11})
    matplotlib.rcParams.update({'figure.figsize': (6.3, 3.9)})  #6.3, 3.9

    x = [float(t) / 1000 for t in data['Ns']]
    y = [float(t) / 1000 for t in data['Bs']]
    # setup the 2D grid with Numpy
    x, y = np.meshgrid(x, y)


    f, axes = plt.subplots(2, 2, sharex='col', sharey='row')


    plt.subplots_adjust(wspace=0.1, hspace=0.2)

    f.add_subplot(111, frameon=False)

    # ax = f.add_subplot(1, 1, 1)
    for ax in axes.flat:
        ax.locator_params(nbins=6)
        ax.set_xlim(xmax = x.max())
        ax.set_ylim(ymax = y.max())
        ax.set_xlim(xmin = x.min())
        ax.set_ylim(ymin = y.min())


    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.xlabel('Nmax (Kpps)')
    plt.ylabel('Bmax (Kb)')

    for data, ax in zip(dataAll, axes.flat):
        im = ax.pcolormesh(x, y, np.array(data['intensity_alpha']), cmap='gnuplot')
        ax.set_title(data['title'])

    cax = f.add_axes([.91, 0.1, 0.03, 0.8])
    foo = f.colorbar(im, cax=cax)

    plt.savefig(fname)

def get_alpha_intensity(Ns, Bs, operational_alphas):
    intensity = []
    ctr = 0
    for b in Bs:

        intensity.append([])
        for n in Ns:
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

def get_system_configs(fnames):
    import math
    max_counts = {}
    total_nmax = 0
    total_bmax = 0
    for fname in fnames:
        nmax = 0
        bmax = 0
        p_max = 0
        with open(fname, 'r') as f:
            G = pickle.load(f)
            G_Train = get_training_graph(G, 20)
            for ts in G_Train:
                v, e = G_Train[ts]
                for r, p, l in v:
                    if p > p_max:
                        p_max = p
                n = int(e[(0, 0, 0), (32, 0, 1)][1])
                if type(e[(0, 0, 0), (32, p_max, 1)][0]) == type(1):
                    b = int(e[(0, 0, 0), (32, p_max, 1)][0])
                else:
                    b = int(max(e[(0, 0, 0), (32, p_max, 1)][0]))

                if b > bmax:
                    bmax = b
                if n > nmax:
                    nmax = n
        total_nmax += nmax
        total_bmax += bmax
        max_counts[fname] = (nmax,bmax)
    print max_counts


    nStep = math.ceil(float(total_nmax) / 10)
    bStep = math.ceil(float(total_bmax) / 10)

    print "Nmax:", total_nmax, "Bmax:", total_bmax
    print nStep, bStep

    Ns = range(int(nStep), 20*int(nStep), int(nStep))
    Bs = range(int(bStep), 20*int(bStep), int(bStep))
    print "Ns:", Ns, "Bs:", Bs
    return Ns, Bs


def get_timestamps_from_fnames(fnames):
    for fname in fnames:
        with open(fname, 'r') as f:
            G = pickle.load(f)
            timestamps = G.keys()
            timestamps.sort()
            return timestamps

def update_edges(G, n_max, b_max, alpha, mode):
    G_new = {}
    (v, edges) = G
    updated_edges = {}
    for edge in edges:
        (r1, p1, l1), (r2, p2, l2) = edge
        # print edge, edges[edge]
        # These are tmp fixes
        if l2 > 0 and edges[edge] != (0, 0):
            (b_hash, b_sketch), n = edges[edge]
            if mode >= 4:
                # Use sketches
                b = min([b_hash, b_sketch])
            else:
                # Use hash tables only
                b = b_hash

            weight = (alpha * float(n) / n_max) + ((1 - alpha) * float(b) / b_max)
            updated_edges[edge] = weight
        else:
            updated_edges[edge] = 0

    G_new = (v, updated_edges)

    return G_new


def get_violation_flags(G_Trains, learn, n_max, b_max, alpha):
    n_viol = False
    b_viol = False
    total_n = {}
    total_b = {}
    debug = True

    for fname in learn:
        if debug: print alpha, fname, learn[fname].final_plan
        print max(learn[fname].final_plan.ncosts.values()), max(learn[fname].final_plan.bcosts.values())
        for ts in G_Trains[fname]:
            if ts not in total_n:
                total_n[ts] = 0
                total_b[ts] = 0
            # print total_n[ts], total_b[ts], learn[fname].final_plan.ncosts[ts], learn[fname].final_plan.bcosts[ts]
            total_n[ts] += learn[fname].final_plan.ncosts[ts]
            total_b[ts] += learn[fname].final_plan.bcosts[ts]

    max_n = max(total_n.values())
    max_b = max(total_b.values())
    if debug: print "max tuples for this plan", alpha, max_n
    if debug: print "max bits for this plan", alpha, max_b
    if max_n > n_max:
        n_viol = True
    if max_b > b_max:
        b_viol = True

    return n_viol, b_viol


def update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha):
    operational_alphas[(n_max, b_max)] = alpha


def update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha):
    for fname in fnames:
        path_string = path_strings[fname]
        if path_string not in unique_plans[fname]:
            unique_plans[fname][path_string] = {}
        unique_plans[fname][path_string][(n_max, b_max)] = alpha


def alpha_tuning_iter(fnames, n_max, b_max, mode, td, q=None):
    memoized_learning = {}

    def memoize_learning(G, alpha, beta, n_max, b_max, mode, fname):
        if (alpha, beta, n_max, b_max, mode, fname) not in memoized_learning:
            memoized_learning[(alpha, beta, n_max, b_max, mode, fname)] = Learn(G, alpha, beta, n_max, b_max, mode)
        return memoized_learning[(alpha, beta, n_max, b_max, mode, fname)]

    def learn_for_alpha(G, fnames, alpha, beta, n_max, b_max, mode):
        learn = {}
        path_strings = {}
        cost = 0
        for fname in fnames:
            learn[fname] = memoize_learning(G[fname], alpha, beta, n_max, b_max, mode, fname)
            path_strings[fname] = learn[fname].final_plan.__repr__()
            cost += learn[fname].final_plan.cost

        n_viol, b_viol = get_violation_flags(G_Trains, learn, n_max, b_max, alpha)

        return learn, path_strings, cost, n_viol, b_viol

    G_Trains = {}
    operational_alphas = {}
    unique_plans = {}
    for fname in fnames:
        with open(fname,'r') as f:
            G = pickle.load(f)
            # print "Training Duration", td
            G_Trains[fname] = get_training_graph(G, td)
        unique_plans[fname] = {}

    prev_alpha = 0
    alpha = 0.5
    prev_cost = 0
    curr_cost = 0

    upper_limit = 1.0
    lower_limit = 0
    beta = 0
    ctr = 0

    max_iter = 10

    # print n_max, b_max
    debug = False
    debug = True
    while True:
        # print alpha
        operational_alphas[(n_max, b_max)] = alpha
        learn, path_strings, curr_cost, n_viol, b_viol = learn_for_alpha(G_Trains, fnames, alpha, beta, n_max, b_max, mode)

        if debug: print alpha, n_max, n_viol, b_max, b_viol

        if not n_viol and b_viol:
            upper_limit = alpha
            alpha = (upper_limit + lower_limit) / 2
            update_operational_alphas(operational_alphas, fnames, n_max, b_max, -1)
            update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
        elif n_viol and not b_viol:
            lower_limit = alpha
            alpha = (upper_limit + lower_limit) / 2
            if ctr == max_iter - 1:
                update_operational_alphas(operational_alphas, fnames, n_max, b_max, -1)
                update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
        elif n_viol and b_viol:
            update_operational_alphas(operational_alphas, fnames, n_max, b_max, -1)
            update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
            break
        else:
            # print trained_learn.local_best_plan.path

            alpha_right = (alpha + upper_limit) / 2
            learn_right, _, cost_right, n_viol_right, b_viol_right = learn_for_alpha(G_Trains, fnames, alpha_right,
                                                                                     beta, n_max, b_max, mode)
            if n_viol_right or b_viol_right:
                cost_right = 100

            alpha_left = (alpha + lower_limit) / 2
            learn_left, _, cost_left, n_viol_left, b_viol_left = learn_for_alpha(G_Trains, fnames, alpha_left,
                                                                                 beta, n_max, b_max, mode)
            if n_viol_left or b_viol_left:
                cost_left = 100

            if debug: print cost_left, curr_cost, cost_right
            if cost_left < curr_cost:
                upper_limit = alpha_left
                alpha = alpha_left
            elif cost_right < curr_cost:
                lower_limit = alpha_right
                alpha = alpha_right
            else:
                update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha)
                update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)
                break
            if ctr == max_iter - 1:
                update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha)
                update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha)

        ctr += 1
        if ctr == max_iter:
            break

    if q is None:
        return operational_alphas, unique_plans, learn
    else:
        q.put((operational_alphas, unique_plans, learn))

