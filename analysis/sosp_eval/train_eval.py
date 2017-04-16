
from analysis.utils import *
from analysis.sosp_eval.utils import *
from analysis.plotlib import *
from sonata.core.training.learn.query_plan import QueryPlan
from sonata.core.training.learn.sonata_search import Search, map_input_graph

from analysis.multi_query.multi_query_tuning import do_alpha_tuning


def do_system_config_space_analysis(fnames, Ns, Bs, modes, td):
    debug = False
    debug = True

    out_data = {}
    for mode in modes:
        print "Mode:", mode
        out_data[mode] = {}
        operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fnames, mode)

        unique_plans_count = 0
        infeasible_config_counts = 0
        feasible_config_counts = 0
        for fname in unique_plans:
            unique_plans_count += len(unique_plans[fname].keys())

        for fname in operational_alphas:
            for config in operational_alphas[fname]:
                alpha = operational_alphas[fname][config]
                if alpha < 0:
                    infeasible_config_counts += 1
                else:
                    feasible_config_counts += 1
            break

        out_data[mode] = (unique_plans_count, infeasible_config_counts, feasible_config_counts, operational_alphas)





def system_config_space_analysis(qid_2_fnames, qid_2_Ns, qid_2_Bs):
    data = {}
    modes = [2, 3, 4, 5]
    # modes = [5]
    TD = 5
    Tmax = 20
    for qid in qid_2_fnames:
        fnames = qid_2_fnames[qid]
        print "Running analysis for query", qid, "using:", fnames
        data[qid] = do_system_config_space_analysis(fnames, qid_2_Ns[qid], qid_2_Bs[qid], modes, TD)
    print data.keys()
    qids = '_'.join([str(x) for x in qid_2_fnames.keys()]) + '_'
    dump_fname = 'data/perf_gain_analysis_' + str(qids) + str(datetime.datetime.fromtimestamp(time.time())) + '.pickle'
    print "Dumping result to file:", dump_fname
    with open(dump_fname, 'w') as f:
        pickle.dump(data, f)

    modes = [2, 3, 4, 5]
    # modes = [5]
    data_dump = {}
    for mode in modes:
        print mode
        operational_alphas, unique_plans = do_alpha_tuning(Ns, Bs, fnames, mode)
        data_dump[mode] = (Ns, Bs, operational_alphas, unique_plans)

def do_train_eval():
    qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
                    2: ['data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle'],
                    12: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
                         'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
                    }
    # qid_2_fnames = {1: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle'],
    #                 16: ['data/hypothesis_graph_1_2017-04-11 02:18:03.593744.pickle',
    #                      'data/hypothesis_graph_6_2017-04-12 15:30:31.466226.pickle']
    #
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