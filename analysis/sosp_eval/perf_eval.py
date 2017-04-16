import pickle
import math
import time
import datetime

from analysis.utils import *
from analysis.sosp_eval.utils import *
from analysis.plotlib import *
from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph


def get_timestamps_from_fnames(fnames):
    for fname in fnames:
        with open(fname, 'r') as f:
            G = pickle.load(f)
            timestamps = G.keys()
            timestamps.sort()
            return timestamps


def do_bias_variance_analysis(fnames, Ns, Bs, modes, TDs, Tmax=300):
    debug = False
    # debug = True

    data_dump = {}
    for mode in modes:
        print "Mode:", mode
        data_dump[mode] = {}
        for n_max in Ns:
            for b_max in Bs:
                data_dump[mode][(n_max, b_max)] = {}
                for td in TDs:
                    print "Training for", td, "data points"
                    # use the tuner for multi-queries
                    operational_alphas, unique_plans, learn = alpha_tuning_iter(fnames, n_max, b_max, mode, td)
                    timestamps = get_timestamps_from_fnames(fnames)
                    # alpha, trained_learn = alpha_tuning_iter(fnames, n_max, b_max, mode, td)

                    in_rmse = 0
                    out_rmse = 0
                    for fname in fnames:
                        in_sample_error = {}
                        out_sample_error = {}
                        trained_learn = learn[fname]
                        alpha = operational_alphas[(n_max, b_max)]
                        with open(fname, 'r') as f:
                            G = pickle.load(f)

                            if debug: print "After tuning for config", n_max, b_max, "we get alpha", \
                                alpha, "path", \
                                learn[fname].final_plan, learn[fname].final_plan.rmse

                            ctr = 1
                            for ts in timestamps[:Tmax]:
                                g = update_edges(G[ts], n_max, b_max, alpha, mode)
                                training_plan = QueryPlan(map_input_graph(g), trained_learn.final_plan.path)
                                local_best_plan = QueryPlan(map_input_graph(g), Search(g).final_plan.path)
                                local_error = (training_plan.cost - local_best_plan.cost)
                                if debug: print "time", ts, "learned plan", training_plan, "local best plan", local_best_plan
                                if debug: print "Cost1", training_plan.cost, "Cost2", local_best_plan.cost, local_error

                                if ctr > td:
                                    if local_best_plan.cost > 0:
                                        out_sample_error[ts] = local_error
                                    else:
                                        out_sample_error[ts] = 0
                                else:
                                    in_sample_error[ts] = local_error
                                ctr += 1

                            # print in_sample_error.values(), out_sample_error.values()
                            in_rmse += (math.sqrt(sum([x * x for x in in_sample_error.values()]))) / len(
                                in_sample_error.keys())
                            out_rmse += (math.sqrt(sum([x * x for x in out_sample_error.values()])) / len(
                                out_sample_error.keys()))
                            print "Errors:", in_rmse, out_rmse
                            data_dump[mode][(n_max, b_max)][td] = (in_rmse, out_rmse)

    return data_dump


def plotLine_lcurve(data, order, xlabel, ylabel, Xmax, Xmin, fname, labels=None):
    xlab = []
    raw = {}
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    color_n = ['r', 'b', 'm', 'c', 'r', 'b', 'm', 'c']
    markers = ['o', '*']
    linestyles = [':']
    p1 = []

    # To determine to plotting order
    if labels is None:
        labels = order
    ctr = 0
    for key in labels:
        (x, y) = data[key]
        if 'Test' in key:
            pl.plot(x, y, label=key, marker=markers[0], markerfacecolor=color_n[ctr], linestyle=linestyles[0],
                    color='k')
        else:
            pl.plot(x, y, label=key, marker=markers[1], markerfacecolor=color_n[ctr], linestyle=linestyles[0],
                    color='k')
        ctr += 1

    if len(labels) > 1:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fancybox=True, shadow=False)

    # pl.legend((p), legnd, 'lower right')
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    # pl.yscale('log')
    # ax.set_ylim(ymin=.0001)
    ax.grid(True)
    plt.tight_layout()
    plot_name = fname
    pl.savefig(plot_name)


def plot_perf_bgain(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [3, 4, 5]:
                    for (n_max, b_max) in data[qid][mode]:
                        y = np.median([x[1] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr = np.std([x[1] for x in data[qid][mode][(n_max, b_max)].values()])
                        if mode not in plot_data:
                            plot_data[mode] = {}
                        plot_data[mode][qid] = (y, yerr)
                        print mode, qid, y

        qids = data.keys()
        xlabels = []
        qids.sort()
        for qid in qids:
            if len(str(qid)) > 1:
                tmp = '{'
                for elem in str(qid):
                    tmp += 'Q' + elem + ','
                tmp = tmp[:-1] + '}'
            else:
                tmp = 'Q' + str(qid)
            print tmp
            xlabels.append(tmp)
        modes = plot_data.keys()
        bar_width = 20
        shift = (0.5+len(modes)) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        color_n = ['r', 'b', 'm', 'c', 'r', 'b', 'm', 'c']
        hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {3: "P4 Target", 4: "Static Ref.", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [plot_data[mode][qid][0] for qid in qids]
            ax.bar(x, y, bar_width, color=color_n[i], label=mode_2_legend[mode], hatch=hatches[i])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('Number of Tuples')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_name = 'data/test_bgain.pdf'
        pl.savefig(plot_name)
        print "Saving...", plot_name


def plot_perf_ngain(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [2, 5]:
                    for (n_max, b_max) in data[qid][mode]:
                        y = np.median([x[0] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr = np.std([x[0] for x in data[qid][mode][(n_max, b_max)].values()])
                        if mode not in plot_data:
                            plot_data[mode] = {}
                        plot_data[mode][qid] = (y, yerr)
                        print mode, qid, y

        qids = data.keys()
        xlabels = []
        qids.sort()
        for qid in qids:
            if len(str(qid)) > 1:
                tmp = '{'
                for elem in str(qid):
                    tmp += 'Q' + elem + ','
                tmp = tmp[:-1] + '}'
            else:
                tmp = 'Q' + str(qid)
            print tmp
            xlabels.append(tmp)
        modes = plot_data.keys()
        bar_width = 20
        shift = 2.5 * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        color_n = ['r', 'b', 'm', 'c', 'r', 'b', 'm', 'c']
        hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2: "OF Target", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [plot_data[mode][qid][0] for qid in qids]
            ax.bar(x, y, bar_width, color=color_n[i], label=mode_2_legend[mode], hatch=hatches[i])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (len(modes) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('Number of Tuples')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_name = 'test.pdf'
        pl.savefig(plot_name)
        print "Saving...", plot_name


def plot_lcurve(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode == 5:
                    for (n_max, b_max) in data[qid][mode]:
                        iter_data = data[qid][mode][(n_max, b_max)]
                        x = iter_data.keys()
                        x.sort()
                        y1 = [iter_data[elem][0] for elem in x]
                        y2 = [iter_data[elem][1] for elem in x]
                        queries = ''
                        for elem in str(qid):
                            queries += 'Q' + elem + ','
                        queries = queries[:-1]
                        label1 = 'Training Error ' + queries
                        label2 = 'Test Error ' + queries
                        plot_data[label1] = (x, y1)
                        plot_data[label2] = (x, y2)
        print plot_data
        order = []
        for qid in data:
            queries = ''
            for elem in str(qid):
                queries += 'Q' + elem + ','
            queries = queries[:-1]
            order.append('Training Error ' + queries)

        for qid in data:
            queries = ''
            for elem in str(qid):
                queries += 'Q' + elem + ','
            queries = queries[:-1]
            order.append('Test Error ' + queries)

        dump_fname.split('.pickle')[0]
        plot_fname = dump_fname.split('.pickle')[0] + '_lcurve_.pdf'
        print plot_fname, plot_data, order

        plotLine_lcurve(plot_data, order, 'Training Data Size (seconds)', 'Error', 'N/A', 'N/A', plot_fname)


def error_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs):
    data = {}
    modes = [2, 3, 4, 5]
    modes = [5]
    TDs = range(0, 101, 10)[1:]
    TDs = [4, 5]
    Tmax = 10
    for qid in qid_2_fnames:
        fnames = qid_2_fnames[qid]
        print "Running analysis for query", qid, "using:", fnames
        data[qid] = do_bias_variance_analysis(fnames, qid_2_Ns[qid], qid_2_Bs[qid], modes, TDs, Tmax)
    print data
    qids = '_'.join([str(x) for x in qid_2_fnames.keys()]) + '_'
    dump_fname = 'data/error_analysis_' + str(qids) + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping result to file:", dump_fname
    with open(dump_fname, 'w') as f:
        pickle.dump(data, f)
    plot_lcurve(dump_fname)


def do_perf_gains_analysis(fnames, Ns, Bs, modes, td):
    debug = False
    debug = True

    data_dump = {}
    for mode in modes:
        print "Mode:", mode
        data_dump[mode] = {}
        for n_max in Ns:
            for b_max in Bs:
                data_dump[mode][(n_max, b_max)] = {}
                operational_alphas, unique_plans, learn = alpha_tuning_iter(fnames, n_max, b_max, mode, td)
                timestamps = get_timestamps_from_fnames(fnames)
                fname_2_G = {}
                for fname in fnames:
                    with open(fname, 'r') as f:
                        G = pickle.load(f)
                        fname_2_G[fname] = G
                for ts in timestamps[td:]:
                    n_cost = 0
                    b_cost = 0
                    for fname in fnames:
                        G = fname_2_G[fname]
                        v, e = G[ts]
                        in_sample_error = {}
                        out_sample_error = {}
                        trained_learn = learn[fname]
                        trained_path = trained_learn.final_plan.path
                        alpha = operational_alphas[(n_max, b_max)]

                        for (e1, e2) in zip(trained_path[:-1], trained_path[1:])[:-1]:
                            # print e1, e2, e[(e1.state, e2.state)]
                            if type(e[(e1.state, e2.state)][0]) == type(1):
                                b_cost += e[(e1.state, e2.state)][0]
                            else:
                                b_cost += min(e[(e1.state, e2.state)][0])
                            n_cost += e[(e1.state, e2.state)][1]

                    data_dump[mode][(n_max, b_max)][ts] = (n_cost, b_cost)
    return data_dump
    #
    # # print data_dump
    # # fname_dump = 'data/performance_gains_' + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    # fname_dump = fname.split('.pickle')[0]+'_performance_gains.pickle'
    # print "Dumping data to", fname_dump
    # with open(fname_dump, 'w') as f:
    #     pickle.dump(data_dump, f)


def perf_gain_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs):
    data = {}
    modes = [2, 3, 4, 5]
    # modes = [5]
    TD = 5
    Tmax = 20
    for qid in qid_2_fnames:
        fnames = qid_2_fnames[qid]
        print "Running analysis for query", qid, "using:", fnames
        data[qid] = do_perf_gains_analysis(fnames, qid_2_Ns[qid], qid_2_Bs[qid], modes, TD)
    print data.keys()
    qids = '_'.join([str(x) for x in qid_2_fnames.keys()]) + '_'
    dump_fname = 'data/perf_gain_analysis_' + str(qids) + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping result to file:", dump_fname
    with open(dump_fname, 'w') as f:
        pickle.dump(data, f)
    plot_perf_ngain(dump_fname)


def do_perf_eval():
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    6: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
                    16: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                         'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
                    }
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    16: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                         'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
                    }
    qid_2_Ns = {1: [1000], 6: [1000], 16: [2000]}
    qid_2_Bs = {1: [50000], 6: [40000], 16: [90000]}

    # error_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)
    perf_gain_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)


if __name__ == '__main__':
    # do_perf_eval()

    # dump_fname = 'data/error_analysis_1,62017-04-15 20:53:19.680790.pickle'
    # plot_lcurve(dump_fname)
    dump_fname = 'data/perf_gain_analysis_16_1_2017-04-15 22:38:18.909253.pickle'
    plot_perf_ngain(dump_fname)
    plot_perf_bgain(dump_fname)
