from __future__ import print_function

from gurobipy import Model, GRB, GurobiError

Q = [1]
query_2_tables = {1: [1, 2]}

sigma_max = 2
width_max = 4
bits_max = 100

# cost_matrix = {1: {(0, 8): (1000, 20, 20), (0, 16): (1000, 70, 40), (0, 32): (1000, 120, 80),
#                    (8, 16): (500, 50, 40), (8, 32): (500, 90, 50), (16, 32): (300, 40, 20)}
#                }
#
# qid_2_R = {1: [0, 8, 16, 32]}

cost_matrix = {1: {(0, 32): {1: (1000, 80), 2: (80, 60)}}
               }

qid_2_R = {1: [0, 32]}


def solve_sonata_lp():
    name = "sonata"
    # try:
    # Create a new model
    m = Model(name)
    I = {}
    D = {}
    Last = {}
    S = {}
    F = {}
    query_2_n = {}
    Sigma = {}

    var_name = "sigma"
    dp_sigma = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
    m.addConstr(dp_sigma <= sigma_max)

    for qid in Q:
        I[qid] = {}
        D[qid] = {}
        Last[qid] = {}
        S[qid] = {}
        F[qid] = {}
        Sigma[qid] = {}
        query_2_n[qid] = {}
        for rid in qid_2_R[qid][1:]:
            # create indicator variable for refinement level rid for query qid
            var_name = "i_" + str(qid) + "_" + str(rid)
            I[qid][rid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

            if rid == qid_2_R[qid][1:][-1]:
                m.addConstr(I[qid][rid] == 1)

            D[qid][rid] = {}
            Last[qid][rid] = {}
            S[qid][rid] = {}
            F[qid][rid] = {}
            Sigma[qid][rid] = {}

            table_2_n = {}

            # add f variables for each previous refinement level
            for rid_prev in qid_2_R[qid]:
                # add f variable for previous refinement level rid_prev for table tid_new
                if rid_prev < rid:
                    var_name = "f_" + str(qid) + "_" + str(rid_prev) + "->" + str(rid)
                    F[qid][rid][rid_prev] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

            # sum of all f variables for each table is at max 1
            f_over__qr = [F[qid][rid][rid_prev] for rid_prev in F[qid][rid].keys()]
            m.addConstr(sum(f_over__qr) >= I[qid][rid])
            m.addConstr(sum(f_over__qr) <= 1)

            for tid in query_2_tables[qid]:
                tid_new = 1000000 * qid + 1000 * tid + rid
                # add stage variable
                var_name = "sigma_" + str(tid_new)
                Sigma[qid][rid][tid] = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
                m.addConstr(dp_sigma >= Sigma[qid][rid][tid])

                # add d variable for this table
                var_name = "d_" + str(tid_new)
                D[qid][rid][tid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

                S[qid][rid][tid] = {}
                for sid in range(1, sigma_max + 1):
                    # add f variable for stage sid rid_prev for table tid_new
                    var_name = "s_" + str(tid_new) + "_" + str(sid)
                    S[qid][rid][tid][sid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)
                    # If S[qid][rid][tid][sid] == 1 then Sigma[qid][rid][tid] == sid
                    m.addGenConstrIndicator(S[qid][rid][tid][sid], True, Sigma[qid][rid][tid] == sid)

                # a table can at most use one stage
                s_over_t = [S[qid][rid][tid][sid] for sid in range(1, sigma_max + 1)]
                m.addConstr(sum(s_over_t) >= D[qid][rid][tid])
                m.addGenConstrIndicator(D[qid][rid][tid], True, sum(s_over_t) == 1)
                m.addGenConstrIndicator(D[qid][rid][tid], False, sum(s_over_t) == 0)
                # m.addConstr(sum(s_over_t) <= 1)

                # add last variable for this table
                var_name = "last_" + str(tid_new)
                Last[qid][rid][tid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

                # create number of out packets for each table
                var_name = "n_" + str(tid_new)
                table_2_n[tid_new] = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name=var_name)

                n_over_tid = [F[qid][rid][rid_prev] * cost_matrix[qid][(rid_prev, rid)][tid][-1] for rid_prev in
                              F[qid][rid].keys()]
                m.addGenConstrIndicator(Last[qid][rid][tid], True, table_2_n[tid_new] >= sum(n_over_tid))
                m.addGenConstrIndicator(Last[qid][rid][tid], False, table_2_n[tid_new] == 0)

            # relate d and last variables for each query
            ind = 1
            for tid in query_2_tables[qid]:
                tmp = [D[qid][rid][tid1] for tid1 in query_2_tables[qid][:ind]]
                m.addConstr(D[qid][rid][tid] >= Last[qid][rid][tid])
                # m.addGenConstrIndicator(Last[qid][rid][tid], True, D[qid][rid][tid] == 1)
                # m.addGenConstrIndicator(Last[qid][rid][tid], False, D[qid][rid][tid] >= 0)
                ind += 1

            for (tid1, tid2) in zip(query_2_tables[qid][:-1], query_2_tables[qid][1:]):
                # m.addGenConstrIndicator(Last[qid][rid][tid2], True, D[qid][rid][tid1] == 1)
                m.addConstr(D[qid][rid][tid1] >= D[qid][rid][tid2])
                # m.addConstr(Last[qid][rid][tid1]+1 <= Last[qid][rid][tid2])

            # inter-query dependency
            for (tid1, tid2) in zip(query_2_tables[qid][:-1], query_2_tables[qid][1:]):
                sigma1 = Sigma[qid][rid][tid1]
                sigma2 = Sigma[qid][rid][tid2]
                m.addGenConstrIndicator(D[qid][rid][tid2], True, sigma1 + 1 <= sigma2)

            # create a query (qid, rid) specific count for number of out packets
            var_name = "n_" + str(qid) + "_" + str(rid)
            query_2_n[qid][rid] = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name=var_name)
            n_over_query = [table_2_n[tid_new] for tid_new in table_2_n.keys()]

            n_over_qr_no_dp = []
            for rid_prev in F[qid][rid].keys():
                n_over_qr_no_dp = [F[qid][rid][rid_prev] * cost_matrix[qid][(rid_prev, rid)][1][0] for rid_prev in
                                   F[qid][rid].keys()]

            var_name = "ind_" + str(qid) + str(rid)
            tmp_ind = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)
            m.addConstr(tmp_ind == 1 - sum([Last[qid][rid][tid] for tid in query_2_tables[qid]]))

            var_name = "qrn_" + str(qid) + "_" + str(rid)
            qrn = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name=var_name)
            m.addGenConstrIndicator(tmp_ind, True, qrn >= sum(n_over_qr_no_dp))
            m.addGenConstrIndicator(tmp_ind, False, qrn >= sum(n_over_query))

            m.addGenConstrIndicator(I[qid][rid], True, query_2_n[qid][rid] >= qrn)

            # sum of all Last variables is 1 for each (qid, rid)
            l_over_query = [Last[qid][rid][tid] for tid in query_2_tables[qid]]
            m.addConstr(sum(l_over_query) <= 1)

    # apply the pipeline width constraint
    for sid in range(1, 1 + sigma_max):
        for qid in Q:
            for rid in qid_2_R[qid][1:]:
                tmp = [S[qid][rid][tid][sid] for tid in query_2_tables[qid]]
                m.addConstr(sum(tmp) <= width_max)

    # apply the bits per stage constraint
    BS = {}
    All_BS = {}
    for sid in range(1, 1 + sigma_max):
        BS[sid] = {}
        All_BS[sid] = []
        for qid in Q:
            BS[sid][qid] = {}
            for rid in qid_2_R[qid][1:]:
                BS[sid][qid][rid] = {}
                for tid in query_2_tables[qid]:
                    var_name = "bs_" + str(qid) + "_" + str(rid)
                    BS[sid][qid][rid][tid] = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name=var_name)
                    b_over_r = [F[qid][rid][rid_prev] * cost_matrix[qid][(rid_prev, rid)][tid][1] for rid_prev in
                                F[qid][rid].keys()]
                    m.addGenConstrIndicator(S[qid][rid][tid][sid], True, BS[sid][qid][rid][tid] == sum(b_over_r))
                    m.addGenConstrIndicator(S[qid][rid][tid][sid], False, BS[sid][qid][rid][tid] == 0)
                    All_BS[sid].append(BS[sid][qid][rid][tid])
        m.addConstr(sum(All_BS[sid]) <= bits_max)

    # define the objective, i.e. minimize the total number of packets to send to stream processor
    total_packets = []
    for qid in Q:
        for rid in qid_2_R[qid][1:]:
            total_packets.append(query_2_n[qid][rid])

    m.setObjective(sum(total_packets), GRB.MINIMIZE)

    m.write(name + ".lp")
    m.optimize()
    print('Obj:', m.objVal)
    for v in m.getVars():
        print(v.varName, v.x)
        # except GurobiError:
        #     print('Error reported', GurobiError.message)


if __name__ == '__main__':
    solve_sonata_lp()
