import pickle
from sonata_new_lp import solve_sonata_lp


def test_ddos_query():
    fname = "data/costs_1_2017-04-12 11:50:14.787439.pickle"
    cost_matrix = {}
    Q = []
    query_2_tables = {}
    qid_2__r = {}

    sigma_max = 4
    width_max = 1
    bits_max = 40000
    ref_levels = [0, 8, 16, 24, 32]

    with open(fname) as f:
        data = pickle.load(f)
        for qid in data:
            cost_matrix[qid] = {}
            query_2_tables[qid] = []
            qid_2__r[qid] = []
            Q.append(qid)
            for transit in data[qid]:
                (r1, r2) = transit
                if r1 in ref_levels and r2 in ref_levels:
                    cost_matrix[qid][transit] = {}
                    qid_2__r[qid] = list(set(qid_2__r[qid]).union([r1, r2]))
                    for tid1, tid2 in (data[qid][transit].keys()[:-1], data[qid][transit].keys()[1:]):
                        cost_matrix[qid][transit][tid2] = (
                            data[qid][transit][tid1][0][1][-1], data[qid][transit][tid2][0][1][0][0],
                            data[qid][transit][tid2][0][1][1])
                        query_2_tables[qid] = list(set(query_2_tables[qid]).union([tid2]))

            qid_2__r[qid].sort()
            query_2_tables[qid].sort()
    # print qid_2__r, Q, query_2_tables
    # print cost_matrix
    mode = 2
    m = solve_sonata_lp(Q, query_2_tables, cost_matrix, qid_2__r, sigma_max, width_max, bits_max, mode)

    mode = 3
    m = solve_sonata_lp(Q, query_2_tables, cost_matrix, qid_2__r, sigma_max, width_max, bits_max, mode)

    mode = 4
    m = solve_sonata_lp(Q, query_2_tables, cost_matrix, qid_2__r, sigma_max, width_max, bits_max, mode)

    mode = 6
    m = solve_sonata_lp(Q, query_2_tables, cost_matrix, qid_2__r, sigma_max, width_max, bits_max, mode)



if __name__ == '__main__':
    test_ddos_query()
