import pickle
import math
import time
import datetime
import numpy as np

from analysis.utils import *
from analysis.sosp_eval.utils import *
from analysis.plotlib import *
from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph

from perf_eval import do_perf_gains_analysis


def plot_var_thresh(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        thresholds = data.keys()
        thresholds.sort()
        plot_data = {}
        for thresh in thresholds:
            for mode in data[thresh]:
                if mode in [3, 4, 5]:
                    for (n_max, b_max) in data[thresh][mode]:
                        y = np.median([x[1] for x in data[thresh][mode][(n_max, b_max)].values()])
                        yerr = np.std([x[1] for x in data[thresh][mode][(n_max, b_max)].values()])
                        if mode not in plot_data:
                            plot_data[mode] = {}
                        plot_data[mode][thresh] = (y,yerr)

        xlabels = thresholds
        modes = plot_data.keys()
        bar_width = 20
        shift = (len(thresholds)-1.5) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(thresholds))]
        print xticks, xlabels
        mode_2_color = {5: 'g', 3: 'r', 4: 'm', 2: 'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {3: "Part-PISA", 4: "Static Ref.", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(thresholds))]
            y = [float(plot_data[mode][qid][0]) / 1000 for qid in thresholds]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=False, fontsize=7)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (len(thresholds) / 2 + 0.5) * bar_width)
        pl.xlabel('Threshold (percentile)')
        pl.ylabel('State (Kb)')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = 'data/var_thresh.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname

def plot_var_intervals(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        intervals = data.keys()
        intervals.sort()
        plot_data = {}
        for interval in intervals:
            for mode in data[interval]:
                if mode in [3, 4, 5]:
                    for (n_max, b_max) in data[interval][mode]:
                        y = np.median([x[1] for x in data[interval][mode][(n_max, b_max)].values()])
                        yerr = np.std([x[1] for x in data[interval][mode][(n_max, b_max)].values()])
                        if mode not in plot_data:
                            plot_data[mode] = {}
                        plot_data[mode][interval] = (y,yerr)

        xlabels = intervals
        modes = plot_data.keys()
        bar_width = 20
        shift = (len(intervals)-1.5) * bar_width
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        i = 0
        xticks = [0.5 * bar_width + q * shift + 0.5 * len(modes) * bar_width for q in range(len(intervals))]
        print xticks, xlabels
        mode_2_color = {5: 'g', 3: 'r', 4: 'm', 2: 'b'}
        mode_2_hatches = {0: '/', 1: '-', 2: '+', 3: 'o', 4: '\\', 5: 'x', 6: 'o', 7: 'O', 8: '.'}
        mode_2_legend = {3: "Only Part.", 4: "Static Ref.", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(intervals))]
            y = [float(plot_data[mode][qid][0]) / 1000 for qid in intervals]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (len(intervals) / 2 + 0.5) * bar_width)
        pl.xlabel('Threshold (percentile)')
        pl.ylabel('State (Kb)')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_var_interval.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname



def variable_threshold():
    thresholds = [90, 99, 99.9, 99.99, 99.999]
    thresh_2_fname = {90:'data/hypothesis_graph_1_threshold_90_1min_0_2017-04-19 02:05:31.397966.pickle',
                      99: 'data/hypothesis_graph_1_threshold_99_1min_0_2017-04-19 02:12:14.794386.pickle',
                      99.9:'data/hypothesis_graph_1_threshold_99.9_1min_0_2017-04-19 02:18:44.961427.pickle',
                      99.99:'data/hypothesis_graph_1_threshold_99.99_1min_0_2017-04-19 02:25:08.768957.pickle',
                      99.999:'data/hypothesis_graph_1_threshold_99.999_1min_0_2017-04-19 02:31:31.067577.pickle'
                      }
    data = {}
    modes = [2, 3, 4, 5]
    # modes = [5]
    TD = 20
    Ns = [1500]
    Bs = [20000]
    for thresh in thresholds:
        fnames = [thresh_2_fname[thresh]]
        data[thresh] = do_perf_gains_analysis(fnames, Ns, Bs, modes, TD)
    threshes = '_'.join([str(x) for x in thresh_2_fname.keys()]) + '_'
    dump_fname = 'data/var_thresh_' + str(threshes) + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping result to file:", dump_fname
    with open(dump_fname, 'w') as f:
        pickle.dump(data, f)
    plot_var_thresh(dump_fname)


def variable_window():
    interval_2_fnames = {1: ['data/hypothesis_graph_1_T_1_1min_0_2017-04-19 02:52:38.715748.pickle'],
                         2:['data/hypothesis_graph_1_T_2_1min_0_2017-04-19 02:59:15.293404.pickle'],
                         3:['data/hypothesis_graph_1_T_3_1min_0_2017-04-19 03:05:41.767800.pickle'],
                         4:['data/hypothesis_graph_1_T_4_1min_0_2017-04-19 03:12:05.602910.pickle'],
                         5:['data/hypothesis_graph_1_T_5_1min_0_2017-04-19 03:18:24.042926.pickle'],
                         6:['data/hypothesis_graph_1_T_6_1min_0_2017-04-19 03:24:42.626011.pickle'],
                         7:['data/hypothesis_graph_1_T_7_1min_0_2017-04-19 03:30:58.814648.pickle'],
                         8:['data/hypothesis_graph_1_T_8_1min_0_2017-04-19 03:37:14.701697.pickle'],
                         9:['data/hypothesis_graph_1_T_9_1min_0_2017-04-19 03:43:29.478099.pickle'],
                         10:['data/hypothesis_graph_1_T_10_1min_0_2017-04-19 03:49:42.939412.pickle']
                         }
    intervals = interval_2_fnames.keys()
    intervals.sort()
    # intervals = [7,8,9,10]
    data = {}
    modes = [2, 3, 4, 5]
    modes = [5]
    TD = 2
    Ns = [1000]
    Bs = [25000]
    for interval in intervals:
        fnames = interval_2_fnames[interval]
        print fnames
        data[interval] = do_perf_gains_analysis([str(x) for x in fnames], [x for x in Ns], [interval*x for x in Bs], modes, TD)
    threshes = '_'.join([str(x) for x in interval_2_fnames.keys()]) + '_'
    dump_fname = 'data/var_intervals_' + str(threshes) + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping result to file:", dump_fname
    print data
    with open(dump_fname, 'w') as f:
        pickle.dump(data, f)
    plot_var_intervals(dump_fname)


if __name__ == '__main__':
    variable_threshold()
    # variable_window()
    # dump_fname = 'data/var_thresh_99.999_90_99_99.99_99.9_2017-04-18 22:58:52.522746.pickle'
    # plot_var_thresh(dump_fname)