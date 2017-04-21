import pickle
import math
import time
import datetime

from analysis.utils import *
from analysis.sosp_eval.utils import *
from analysis.plotlib import *
from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph

from analysis.multi_query.multi_query_tuning import do_alpha_tuning


def plot_alpha(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = []
        for qid in data:
            for mode in data[qid]:
                Ns = data[qid][mode][-2]
                Bs = data[qid][mode][-1]
                # print data[qid][mode]
                operational_alphas = data[qid][mode][3]
                intensity_alpha = get_alpha_intensity(Ns, Bs[:-1], operational_alphas)
                plot_fname = dump_fname.split('.pickle')[0] + '_heatmap_alpha_' + str(qid) + '_' + str(mode) + '.pdf'
                # print "Dumping", plot_fname
                if mode == 2: title = 'Part-OF'
                elif mode == 3: title = 'Part-PISA'
                elif mode == 4: title = 'Fixed Refinement'
                elif mode == 5: title = 'Sonata'

                plot_data.append({'Ns': Ns,
                                  'Bs': Bs[:-1],
                                  'intensity_alpha': intensity_alpha,
                                  'plot_fname':plot_fname,
                                  'title': title
                                  })

                # print Ns, Bs
                # heatmap_plot(Ns, Bs[:-1], intensity_alpha, 'Nmax (Kpps)', 'Bmax (Kb)', plot_fname)
        # print plot_data
        heatmap_sub_plot(plot_data)

def plot_unique_plans(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [5]:
                    y = data[qid][mode][0]
                    if mode not in plot_data:
                        plot_data[mode] = {}
                    plot_data[mode][qid] = y

        qids = data.keys()
        xlabels = []
        qids.sort()
        for qid in qids:
            if len(str(qid)) > 1:
                # tmp = '{'
                # for elem in str(qid):
                #     tmp += 'Q' + elem + ','
                # tmp = tmp[:-1] + '}'
                tmp = 'All'
            else:
                if qid == 1: tmp = 'DDoS-UDP'
                elif qid == 2: tmp = 'SSpreader'
                elif qid == 3: tmp = 'PortScan'
                else: tmp = 'Q' + str(qid)
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
            y = [int(plot_data[mode][qid]) for qid in qids]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('Number of Unique Plans')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_unique_plans.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname


def plot_infeasible_configs(dump_fname):
    with open(dump_fname, 'r') as f:
        data = pickle.load(f)
        # print data
        plot_data = {}
        for qid in data:
            for mode in data[qid]:
                if mode in [5]:
                    y = 100 * float(data[qid][mode][1]) / (data[qid][mode][1] + data[qid][mode][2])
                    if mode not in plot_data:
                        plot_data[mode] = {}
                    plot_data[mode][qid] = y

        qids = data.keys()
        xlabels = []
        qids.sort()
        for qid in qids:
            if len(str(qid)) > 1:
                # tmp = '{'
                # for elem in str(qid):
                #     tmp += 'Q' + elem + ','
                # tmp = tmp[:-1] + '}'
                tmp = 'All'
            else:
                if qid == 1: tmp = 'DDoS-UDP'
                elif qid == 2: tmp = 'SSpreader'
                elif qid == 3: tmp = 'PortScan'
                else: tmp = 'Q' + str(qid)
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
            y = [int(plot_data[mode][qid]) for qid in qids]
            ax.bar(x, y, bar_width, color=mode_2_color[mode], label=mode_2_legend[mode], hatch=mode_2_hatches[mode])
            print mode, x, y
            i += 1
        ax.yaxis.set_major_locator(my_locator)
        ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.1), ncol=3, fancybox=True, shadow=False)
        ax.set_xlim(xmin=0)
        ax.set_xlim(xmax=xticks[-1] + (float(len(modes)) / 2 + 0.5) * bar_width)
        pl.xlabel('Queries')
        pl.ylabel('Infeasible Configurations (\%)')
        plt.xticks(xticks, xlabels)

        ax.grid(True)
        plt.tight_layout()
        plot_fname = dump_fname.split('.pickle')[0] + '_infeasible_configs.pdf'
        pl.savefig(plot_fname)
        print "Saving...", plot_fname


def do_system_config_space_analysis_unique_plans(fnames, Ns, Bs, modes, td):
    debug = False
    debug = True
    # Ns = Ns[:2]
    # Bs = Bs[:2]

    out_data = {}
    for mode in modes:
        print "Mode:", mode
        out_data[mode] = {}
        operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fnames, mode, td)
        print operational_alphas

        unique_plans_count = 0
        infeasible_config_counts = 0
        feasible_config_counts = 0
        final_alpha_values = {}
        for fname in unique_plans:
            unique_plans_count += len(unique_plans[fname].keys())

        for config in operational_alphas:
            alpha = operational_alphas[config]
            final_alpha_values[config] = alpha
            if alpha < 0:
                infeasible_config_counts += 1
            else:
                feasible_config_counts += 1

        out_data[mode] = (
            unique_plans_count, infeasible_config_counts, feasible_config_counts,
            final_alpha_values, Ns, Bs,
            unique_plans)
    return out_data

def do_system_config_space_analysis(fnames, Ns, Bs, modes, td):
    debug = False
    debug = True
    # Ns = Ns[:2]
    # Bs = Bs[:2]

    out_data = {}
    for mode in modes:
        print "Mode:", mode
        out_data[mode] = {}
        operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fnames, mode, td)
        print operational_alphas

        unique_plans_count = 0
        infeasible_config_counts = 0
        feasible_config_counts = 0
        final_alpha_values = {}
        for fname in unique_plans:
            unique_plans_count += len(unique_plans[fname].keys())

        for config in operational_alphas:
            alpha = operational_alphas[config]
            final_alpha_values[config] = alpha
            if alpha < 0:
                infeasible_config_counts += 1
            else:
                feasible_config_counts += 1

        out_data[mode] = (
        unique_plans_count, infeasible_config_counts, feasible_config_counts, final_alpha_values, Ns, Bs)
    return out_data


def system_config_space_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs):
    data = {}
    modes = [2, 3, 4, 5]
    modes = [5]
    TD = 30
    Tmax = 20
    for qid in qid_2_fnames:
        print "Generating results for query", qid
        fnames = qid_2_fnames[qid]
        print "Running analysis for query", qid, "using:", fnames
        data[qid] = do_system_config_space_analysis(fnames, qid_2_Ns[qid], qid_2_Bs[qid], modes, TD)
    print data
    qids = '_'.join([str(x) for x in qid_2_fnames.keys()]) + '_'
    dump_fname = 'data/perf_gain_analysis_' + str(qids) + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping result to file:", dump_fname
    with open(dump_fname, 'w') as f:
        pickle.dump(data, f)
    plot_alpha(dump_fname)
    plot_unique_plans(dump_fname)
    plot_infeasible_configs(dump_fname)


def do_train_eval():
    # qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
    #                 2: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
    #                 12: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
    #                      'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
    #                 }

    # qid_2_fnames = {
    #     1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle']
    # }
    ## FINAL
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    2: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
                    3: ['data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle'],
                    123: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                          'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle',
                          'data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle']
                    }
    ## FINAL FOR UNIQUE PLANS
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'] }

    qid_2_fnames = {1: ['data/hypothesis_graph_1_plan_counts__5min_caida_2017-04-20 18:30:11.123669.pickle'],
                    2: ['data/hypothesis_graph_2_plan_counts__5min_caida_2017-04-20 19:22:24.625582.pickle'],
                    3: ['data/hypothesis_graph_3_plan_counts__5min_caida_2017-04-20 19:27:13.770639.pickle'],
                    4: ['data/hypothesis_graph_4_plan_counts__5min_caida_2017-04-20 19:34:34.652234.pickle'],
                    6: ['data/hypothesis_graph_6_plan_counts__5min_caida_2017-04-20 19:49:56.064561.pickle']
                    }

    qid_2_Ns = {}
    qid_2_Bs = {}
    for qid in qid_2_fnames:
        fnames = qid_2_fnames[qid]
        Ns, Bs = get_system_configs(fnames)
        qid_2_Ns[qid] = Ns
        qid_2_Bs[qid] = Bs

    system_config_space_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs)


if __name__ == '__main__':
    do_train_eval()
    dump_fname = 'data/perf_gain_analysis_1_2_12_2017-04-16 17:38:00.128793.pickle'

    # dump_fname = 'data/perf_gain_analysis_1_2_12_2017-04-17 08:11:44.377775.pickle'
    # plot_alpha(dump_fname)
    """
    Config:
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    2: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
                    3: ['data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle'],
                    123: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                          'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle',
                          'data/hypothesis_graph_2_min_0_2017-04-18 04:25:11.918672.pickle']
                    }
    modes = [2, 3, 4, 5]
    # modes = [5]
    TD = 30
    Tmax = 20
    """
    # dump_fname = 'data/perf_gain_analysis_123_1_2_3_2017-04-20 09:32:07.821087.pickle'
    # plot_alpha(dump_fname)
    # plot_unique_plans(dump_fname)
    # plot_infeasible_configs(dump_fname)
