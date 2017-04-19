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
        mode_2_legend = {3: "Only Part.", 4: "Static Ref.", 5: "SONATA"}
        for mode in modes:
            x = [0.5 * bar_width + q * shift + i * bar_width for q in range(len(thresholds))]
            y = [float(plot_data[mode][qid][0]) / 1000 for qid in thresholds]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (len(thresholds) / 2 + 0.5) * bar_width)
        pl.xlabel('Threshold (percentile)')
        pl.ylabel('State (Kb)')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_var_thresh.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname
    return 0


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
    TD = 10
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
    return 0


if __name__ == '__main__':
    # variable_threshold()
    dump_fname = 'data/var_thresh_99.999_90_99_99.99_99.9_2017-04-18 22:58:52.522746.pickle'
    plot_var_thresh(dump_fname)