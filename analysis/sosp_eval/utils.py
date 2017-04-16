import pickle

from sonata.core.training.learn.learn import Learn
from analysis.utils import chunkify, get_training_graph


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

    for fname in learn:
        # print fname, learn[fname].final_plan
        # print learn[fname].final_plan.ncosts, learn[fname].final_plan.bcosts
        for ts in G_Trains[fname]:
            if ts not in total_n:
                total_n[ts] = 0
                total_b[ts] = 0
            # print total_n[ts], total_b[ts], learn[fname].final_plan.ncosts[ts], learn[fname].final_plan.bcosts[ts]
            total_n[ts] += learn[fname].final_plan.ncosts[ts]
            total_b[ts] += learn[fname].final_plan.bcosts[ts]

    max_n = max(total_n.values())
    max_b = max(total_b.values())
    # print "max tuples for this plan", alpha, max_n
    # print "max bits for this plan", alpha, max_b
    if max_n > n_max:
        n_viol = True
    if max_b > b_max:
        b_viol = True

    return n_viol, b_viol


def update_operational_alphas(operational_alphas, fnames, n_max, b_max, alpha):
    for fname in fnames:
        operational_alphas[fname][(n_max, b_max)] = alpha


def update_unique_plans(unique_plans, fnames, path_strings, n_max, b_max, alpha):
    for fname in fnames:
        path_string = path_strings[fname]
        if path_string not in unique_plans[fname]:
            unique_plans[fname][path_string] = {}
        unique_plans[fname][path_string][(n_max, b_max)] = alpha


def alpha_tuning_iter(fnames, n_max, b_max, mode, Td, q=None):
    memoized_learning = {}

    def memoize_learning(G, alpha, beta, n_max, b_max, mode):
        if (alpha, beta, n_max, b_max, mode) not in memoized_learning:
            memoized_learning[(alpha, beta, n_max, b_max, mode)] = Learn(G, alpha, beta, n_max, b_max, mode)
        return memoized_learning[(alpha, beta, n_max, b_max, mode)]

    def learn_for_alpha(G, fnames, alpha, beta, n_max, b_max, mode):
        learn = {}
        path_strings = {}
        cost = 0
        for fname in fnames:
            learn[fname] = memoize_learning(G[fname], alpha, beta, n_max, b_max, mode)
            path_strings[fname] = learn[fname].final_plan.__repr__()
            cost += learn[fname].final_plan.cost

        n_viol, b_viol = get_violation_flags(G_Trains, learn, n_max, b_max, alpha)

        return learn, path_strings, cost, n_viol, b_viol

    G_Trains = {}
    operational_alphas = {}
    unique_plans = {}
    learn = {}
    for fname in fnames:
        with open(fname,'r') as f:
            G = pickle.load(f)
            G_Trains[fname] = get_training_graph(G, Td)
        operational_alphas[fname] = {}
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

    print n_max, b_max
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

            print cost_left, curr_cost, cost_right
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
