import pickle
import math
import time
import datetime

from analysis.utils import *
from analysis.sosp_eval.utils import *
from analysis.plotlib import *
from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph





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


def plot_perf_overheads(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [5]:
                    for (n_max, b_max) in data[qid][mode]:
                        y1 = np.median([x[4][0] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr1 = np.std([x[4][0] for x in data[qid][mode][(n_max, b_max)].values()])
                        y2 = np.median([x[4][1] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr2 = np.std([x[4][1] for x in data[qid][mode][(n_max, b_max)].values()])
                        y3 = np.median([x[4][2] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr3 = np.std([x[4][2] for x in data[qid][mode][(n_max, b_max)].values()])
                        if mode not in plot_data:
                            plot_data[mode] = {}
                        plot_data[mode][qid] = ((y1, y2, y2), (yerr1, yerr2, yerr3))
                        print mode, qid, plot_data[mode][qid]

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
        mode_2_color = {0:'r', 1:'b', 2:'g'}
        mode_2_hatches = {0: '/', 1: '\\', 2: '+', 3: 'o', 4: 'x', 5: '.', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2:"OF Only",3: "P4 Only", 4: "Static Ref", 5: "SONATA"}

        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y1 = [int(plot_data[mode][qid][0][0]) for qid in qids]
            y2 = [int(plot_data[mode][qid][0][1]) for qid in qids]
            y3 = [int(plot_data[mode][qid][0][2]) for qid in qids]
            color_alpha = 1
            ax.bar(x, y1, bar_width, alpha=color_alpha, color=mode_2_color[0], label="Parser", hatch=mode_2_hatches[0])
            ax.bar(x, y2, bar_width, alpha=color_alpha, color=mode_2_color[1], label="Runtime", hatch=mode_2_hatches[1],
                   bottom = y1)
            ax.bar(x, y3, bar_width, alpha=color_alpha, color=mode_2_color[2], label="Driver Overhead", hatch=mode_2_hatches[2],
                   bottom = y2)
            print mode, x, y1, y2, y3
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('Time (ms)')
        plt.xticks(xticks, xlabels)

        # ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_overheads.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname



def plot_perf_deltas(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [4, 5]:
                    for (n_max, b_max) in data[qid][mode]:
                        y = np.median([x[2] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr = np.std([x[2] for x in data[qid][mode][(n_max, b_max)].values()])
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
        mode_2_color = {5:'g', 3:'r', 4:'m', 2:'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2:"OF Only",3: "P4 Only", 4: "Static Ref", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [int(plot_data[mode][qid][0]) for qid in qids]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('Number of Updates')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_deltas.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname


def plot_perf_delay(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [2,4,5]:
                    for (n_max, b_max) in data[qid][mode]:
                        y = np.median([x[3] for x in data[qid][mode][(n_max, b_max)].values()])
                        yerr = np.std([x[3] for x in data[qid][mode][(n_max, b_max)].values()])
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
        modes.sort()
        bar_width = 20
        shift = (0.5+len(modes)) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        mode_2_color = {5:'g', 3:'r', 4:'m', 2:'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2:"No Ref.",4: "Static Ref.", 5: "SONATA"}
        all_ys = []
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [int(plot_data[mode][qid][0])-1 for qid in qids]
            all_ys += y
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        ax.set_ylim(ymax=2+max(all_ys))
        pl.xlabel('Queries')
        pl.ylabel('Detection Delay (seconds)')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_delay.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname




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
        mode_2_color = {5:'g', 3:'r', 4:'m', 2:'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {3: "P4 Target", 4: "Static Ref.", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [float(plot_data[mode][qid][0])/1000 for qid in qids]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('State (Kb)')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_bgain.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname


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
        mode_2_color = {5:'g', 3:'r', 4:'m', 2:'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2: "OF Target", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [plot_data[mode][qid][0] for qid in qids]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
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
        plot_fname = dump_fname.split('.pickle')[0] + '_ngain.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname


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


        plot_fname = dump_fname.split('.pickle')[0] + '_lcurve.pdf'
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
                fname_2_pmax = {}
                for fname in fnames:
                    with open(fname, 'r') as f:
                        G = pickle.load(f)
                        v,e = G[G.keys()[0]]
                        p_max = 0
                        for r,p,l in v:
                            if p > p_max:
                                p_max = p
                        fname_2_G[fname] = G
                        fname_2_pmax[fname] = p_max
                for ts in timestamps[td:]:
                    n_cost = 0
                    b_cost = 0
                    delta_updates = 0
                    detection_delay = {}
                    parse_time_raw = 1
                    parse_time_tuple = 0.5
                    runtime_overhead = 1
                    driver_overhead = 1

                    for fname in fnames:
                        G = fname_2_G[fname]
                        p_max = fname_2_pmax[fname]

                        v, e = G[ts]
                        trained_learn = learn[fname]
                        trained_path = trained_learn.final_plan.path
                        alpha = operational_alphas[(n_max, b_max)]

                        detection_delay[fname] = len(trained_learn.final_plan.path[:-1])

                        for (e1, e2) in zip(trained_path[:-1], trained_path[1:])[:-1]:
                            # print e1, e2, e[(e1.state, e2.state)]
                            if type(e[(e1.state, e2.state)][0]) == type(1):
                                b_cost += e[(e1.state, e2.state)][0]
                            else:
                                b_cost += min(e[(e1.state, e2.state)][0])
                            n_cost += e[(e1.state, e2.state)][1]

                            # update delta updates
                            r2, p2, l2 = e2.state
                            e2_new = r2, p_max, l2
                            delta_updates += e[(e1.state, e2_new)][1]

                    t_runtime = runtime_overhead*delta_updates
                    t_driver = driver_overhead*delta_updates
                    if mode == 2:
                        t_parse = parse_time_raw*n_cost
                    else:
                        t_parse = parse_time_tuple*n_cost
                    overheads = (t_parse, t_runtime, t_driver)

                    data_dump[mode][(n_max, b_max)][ts] = (n_cost, b_cost, delta_updates,
                                                           np.median(detection_delay.values()), overheads)

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
    plot_perf_bgain(dump_fname)
    plot_perf_deltas(dump_fname)
    plot_perf_delay(dump_fname)
    plot_perf_overheads(dump_fname)


def do_perf_eval():
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    2: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
                    12: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                         'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
                    }
    # qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
    #                 16: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
    #                      'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
    #                 }
    qid_2_Ns = {1: [1000], 2: [1000], 12: [2000]}
    qid_2_Bs = {1: [50000], 2: [40000], 12: [90000]}

    # error_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)
    perf_gain_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)


if __name__ == '__main__':
    # do_perf_eval()

    # dump_fname = 'data/error_analysis_1,62017-04-15 20:53:19.680790.pickle'
    # plot_lcurve(dump_fname)

    dump_fname = 'data/perf_gain_analysis_1_2_12_2017-04-16 11:13:54.285945.pickle'
    # plot_perf_ngain(dump_fname)
    # plot_perf_bgain(dump_fname)
    # plot_perf_deltas(dump_fname)
    # plot_perf_delay(dump_fname)
    plot_perf_overheads(dump_fname)
