import pickle
import math
import time
import datetime

from analysis.utils import *
from analysis.sosp_eval.utils import *
from analysis.plotlib import *
from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph

# Packet Parser Overhead
parser_overhead = {'dns': 0.052094459533691406, 'tuple': 0.055909156799316406}

# Driver Overhead
add_count_2_time = {130: 116.89281463623047, 260: 171.89192771911621, 390: 170.61400413513184, 10: 151.89194679260254,
                    140: 121.67882919311523, 270: 126.34682655334473, 400: 177.22892761230469, 20: 97.3358154296875,
                    150: 110.00204086303711, 280: 131.67715072631836, 410: 161.35501861572266, 30: 89.437007904052734,
                    160: 109.36498641967773, 290: 131.64997100830078, 420: 156.82697296142578, 40: 155.69210052490234,
                    170: 115.0970458984375, 300: 127.69007682800293, 430: 155.25507926940918, 50: 105.27992248535156,
                    180: 117.4461841583252, 310: 191.3151741027832, 440: 172.52182960510254, 60: 92.607975006103516,
                    190: 122.17116355895996, 320: 186.45906448364258, 450: 169.17920112609863, 70: 89.874982833862305,
                    200: 157.05609321594238, 330: 176.01203918457031, 460: 164.34812545776367, 80: 98.065853118896484,
                    210: 172.34182357788086, 340: 250.36191940307617, 470: 158.26797485351562, 90: 95.350027084350586,
                    220: 116.4240837097168, 350: 215.90805053710938, 480: 170.85599899291992, 100: 96.848011016845703,
                    230: 175.76789855957031, 360: 199.63192939758301, 490: 162.78886795043945, 110: 100.24595260620117,
                    240: 207.76987075805664, 370: 233.67595672607422, 500: 174.58701133728027, 120: 134.39297676086426,
                    250: 122.2689151763916, 380: 219.02704238891602}
del_count_2_time = {130: 170.61805725097656, 260: 103.99103164672852, 390: 215.61002731323242, 10: 140.80309867858887,
                    140: 94.512939453125, 270: 108.30903053283691, 400: 129.87995147705078, 20: 105.48186302185059,
                    150: 95.526933670043945, 280: 106.01115226745605, 410: 126.95789337158203, 30: 78.44090461730957,
                    160: 95.064878463745117, 290: 101.51791572570801, 420: 122.61390686035156, 40: 89.751005172729492,
                    170: 99.943161010742188, 300: 140.66004753112793, 430: 116.55306816101074, 50: 133.99887084960938,
                    180: 102.3249626159668, 310: 138.11016082763672, 440: 125.45299530029297, 60: 84.606170654296875,
                    190: 183.06899070739746, 320: 135.58816909790039, 450: 122.61795997619629, 70: 115.66495895385742,
                    200: 103.90090942382812, 330: 162.08291053771973, 460: 117.42901802062988, 80: 85.543155670166016,
                    210: 98.326206207275391, 340: 125.53787231445312, 470: 123.27003479003906, 90: 90.488910675048828,
                    220: 96.429109573364258, 350: 165.679931640625, 480: 123.69799613952637, 100: 87.945938110351562,
                    230: 114.74108695983887, 360: 162.45007514953613, 490: 208.02783966064453, 110: 91.194868087768555,
                    240: 100.33106803894043, 370: 215.60478210449219, 500: 131.30807876586914, 120: 156.44598007202148,
                    250: 101.39894485473633, 380: 167.25492477416992}


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
            if qid in data.keys():
                for mode in data[qid]:
                    if mode in [5]:
                        for (n_max, b_max) in data[qid][mode]:
                            t_parse = []
                            t_driver = []
                            t_runtime = []
                            dmax = max(add_count_2_time.keys())
                            for ts in data[qid][mode][(n_max, b_max)]:
                                n = data[qid][mode][(n_max, b_max)][ts][0]
                                d = 10 * (int(data[qid][mode][(n_max, b_max)][ts][2]) / 10)
                                # print qid, n, d, data[qid][mode][(n_max, b_max)][ts][2], dmax, add_count_2_time[dmax]
                                t_parse.append(n * parser_overhead['tuple'])
                                if d in add_count_2_time:
                                    t_driver.append(add_count_2_time[d])
                                else:
                                    t_driver.append(add_count_2_time[dmax])
                                t_runtime.append(d * parser_overhead['tuple'])
                            # print qid, t_parse
                            y1 = np.median(t_parse)
                            yerr1 = np.std(t_parse)
                            y3 = np.median(t_driver)
                            yerr3 = np.std(t_driver)
                            y2 = np.median(t_runtime)
                            yerr2 = np.std(t_runtime)
                            if mode not in plot_data:
                                plot_data[mode] = {}
                            plot_data[mode][qid] = ((y1, y2, y3), (yerr1, yerr2, yerr3))
                            print mode, qid, plot_data[mode][qid]

        qids = data.keys()
        # qids = [3]
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
            xlabels.append(tmp)
        modes = plot_data.keys()
        bar_width = 20
        shift = (0.5 + len(modes)) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        mode_2_color = {0: 'r', 1: 'b', 2: 'g'}
        mode_2_hatches = {0: '/', 1: '\\', 2: '+', 3: 'o', 4: 'x', 5: '.', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2: "OF Only", 3: "P4 Only", 4: "Static Ref", 5: "SONATA"}

        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y1 = [1000*int(plot_data[mode][qid][0][0]) for qid in qids]
            y2 = [1000*int(plot_data[mode][qid][0][1]) for qid in qids]
            y3 = [1000*int(plot_data[mode][qid][0][2]) for qid in qids]
            color_alpha = 1
            # ax.bar(x, y1, bar_width, alpha=color_alpha, color=mode_2_color[0], label="Parser", hatch=mode_2_hatches[0])
            ax.bar(x, y2, bar_width, alpha=color_alpha, color=mode_2_color[1], label="Runtime", hatch=mode_2_hatches[1],
                   # bottom=y1
                   )
            ax.bar(x, y3, bar_width, alpha=color_alpha, color=mode_2_color[2], label="Driver Overhead",
                   hatch=mode_2_hatches[2],
                   bottom=y2
                   # bottom=[a + b for (a, b) in zip(y1, y2)]
                   )
            print mode, x, y1, y2, y3
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        # ax.set_ylim(ymax=80)
        pl.xlabel('Queries')
        pl.ylabel('Time (micro seconds)')
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
        shift = (0.5 + len(modes)) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        mode_2_color = {5: 'g', 3: 'r', 4: 'm', 2: 'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2: "OF Only", 3: "P4 Only", 4: "Static Ref", 5: "SONATA"}
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
                if mode in [2, 4, 5]:
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
        shift = (0.5 + len(modes)) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        mode_2_color = {5: 'g', 3: 'r', 4: 'm', 2: 'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2: "No Ref.", 4: "Static Ref.", 5: "SONATA"}
        all_ys = []
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [int(plot_data[mode][qid][0]) - 1 for qid in qids]
            all_ys += y
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        ax.set_ylim(ymax=2 + max(all_ys))
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
        shift = (0.5 + len(modes)) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(qids))]
        print xticks, xlabels
        mode_2_color = {5: 'g', 3: 'r', 4: 'm', 2: 'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {3: "P4 Target", 4: "Static Ref.", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [float(plot_data[mode][qid][0]) / 1000 for qid in qids]
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
        mode_2_color = {5: 'g', 3: 'r', 4: 'm', 2: 'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {2: "OF Target", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(qids))]
            y = [plot_data[mode][qid][0] for qid in qids]
            yerr = [plot_data[mode][qid][1] for qid in qids]
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
        print "Mode:", mode, Ns, Bs, fnames
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
                        v, e = G[G.keys()[0]]
                        p_max = 0
                        for r, p, l in v:
                            if p > p_max:
                                p_max = p
                        fname_2_G[fname] = G
                        fname_2_pmax[fname] = p_max
                for ts in timestamps[td:]:
                    n_cost = 0
                    b_cost = 0
                    delta_updates = 0
                    detection_delay = {}
                    parse_time_raw = 0.052
                    parse_time_tuple = 0.05
                    runtime_overhead = 0.3
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

                    t_runtime = runtime_overhead * delta_updates
                    t_driver = driver_overhead * delta_updates
                    if mode == 2:
                        t_parse = parse_time_raw * n_cost
                    else:
                        t_parse = parse_time_tuple * n_cost
                    overheads = (t_parse, t_runtime, t_driver)

                    data_dump[mode][(n_max, b_max)][ts] = (n_cost, b_cost, delta_updates,
                                                           np.median(detection_delay.values()), overheads)

    return data_dump


def perf_gain_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs):
    data = {}
    modes = [2, 3, 4, 5]
    # modes = [5]
    TD = 30
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
                    3: ['data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle'],
                    123: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                          'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle',
                          'data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle']
                    }
    # qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
    #                 16: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
    #                      'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
    #                 }
    qid_2_Ns = {1: [1500], 2: [1000], 3: [2500], 123: [1000]}
    qid_2_Bs = {1: [20000], 2: [45000], 3: [20000], 123: [95000]}

    # error_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)
    perf_gain_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)


if __name__ == '__main__':
    # do_perf_eval()

    # dump_fname = 'data/error_analysis_1,62017-04-15 20:53:19.680790.pickle'
    # plot_lcurve(dump_fname)





    # used for results till April 18th
    dump_fname = 'data/perf_gain_analysis_1_2_12_2017-04-16 16:36:31.767328.pickle'

    """
    #Config:
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    2: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
                    3: ['data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle'],
                    123: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                          'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle',
                          'data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle']
                    }
    qid_2_Ns = {1: [1500], 2: [1000], 3: [2500], 123: [1000]}
    qid_2_Bs = {1: [20000], 2: [45000], 3: [20000], 123: [95000]}
    """
    dump_fname = 'data/perf_gain_analysis_123_1_2_3_2017-04-18 19:39:34.483612.pickle'

    plot_perf_ngain(dump_fname)
    plot_perf_bgain(dump_fname)
    plot_perf_deltas(dump_fname)
    plot_perf_delay(dump_fname)
    plot_perf_overheads(dump_fname)
