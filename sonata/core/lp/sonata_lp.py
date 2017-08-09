from __future__ import print_function

from gurobipy import Model, GRB, GurobiError

Q = [1, 2, 3]
D = ['a', 'b', 'c', 'd', 'e']
query_2_tables = {1: [1, 2], 2: [3, 4], 3: [5, 6]}
query_2_D = {1: ['a', 'b', 'c'], 2: ['c', 'd', 'e'], 3: ['c', 'e']}
table_2_bits = {1: 100, 2: 80, 3: 40, 4: 20, 5: 40, 6: 30}

sigma_max = 4
clone_max = 1
bits_max = 80


def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]] + item
            yield item


def solve_sonata_lp():
    name = "sonata"
    try:
        # Create a new model
        m = Model(name)
        # create table tuples
        tables = {}
        table_2_qid = {}
        table_2_d = {}
        table_2_last = {}

        for qid in query_2_tables:
            table_2_last[qid] = {}
            table_2_d[qid] = {}
            for tid in query_2_tables[qid]:
                table_2_qid[tid] = qid

                # add a binary decision variable d
                var_name = "d_" + str(tid)
                table_2_d[qid][tid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

                # add a binary decision variable last
                var_name = "last_" + str(tid)
                table_2_last[qid][tid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

        for tid in table_2_bits.keys():
            tables[tid] = {}
            qid = table_2_qid[tid]
            tables[tid]["qid"] = qid
            tables[tid]["d"] = table_2_d[qid][tid]
            tables[tid]["last"] = table_2_last[qid][tid]

        # print (tables)

        # satisfy the `last` variable constraint for each query
        qid_2_last = {}
        for qid in Q:
            var_name = "qid_last_" + str(qid)
            qid_2_last[qid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)
            tmp = [table_2_last[qid][tid] for tid in query_2_tables[qid]]
            m.addConstr(sum(tmp) == qid_2_last[qid])

        # relate d & last variables
        for qid in Q:
            ind = 1
            for tid in query_2_tables[qid]:
                tmp = [table_2_d[qid][tid1] for tid1 in query_2_tables[qid][:ind]]
                m.addConstr(sum(tmp) >= table_2_last[qid][tid] * ind)
                ind += 1

        # Enumerate powerset for queries
        G = list(powerset(Q))[:-1]
        print(G)

        # compute the cardinality of elements in G
        gid_2_doubleD = {}
        gid = 0
        for g in G:
            output_set = set()
            for qid in g:
                output_set = output_set.union(query_2_D[qid])
            gid_2_doubleD[gid] = output_set
            gid += 1

        print(gid_2_doubleD)

        # create A variables
        A = {}
        for gid in range(len(G)):
            var_name = "A_" + str(gid)
            A[gid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

        # Add pipeline specific variables
        pipeline_2_I = {}
        pipeline_2_O = {}
        for pid in Q:
            pipeline_2_O[pid] = {}
            pipeline_2_I[pid] = {}

            # create I variables
            for qid in Q:
                var_name = "I_" + str(pid) + "_" + str(qid)
                pipeline_2_I[pid][qid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

            # create O variables
            for qid1 in Q:
                pipeline_2_O[pid][qid1] = {}
                for qid2 in Q:
                    if qid1 != qid2:
                        var_name = "O_" + str(pid) + "_" + str(qid1) + "_" + str(qid2)
                        pipeline_2_O[pid][qid1][qid2] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

        # complimentary O constraint
        for pid in Q:
            for qid1 in Q:
                for qid2 in Q:
                    if qid1 != qid2:
                        m.addConstr(pipeline_2_O[pid][qid1][qid2] + pipeline_2_O[pid][qid2][qid1] <= 1)
                        # if I1 & I2 then O12+O21
                        m.addConstr(
                            pipeline_2_O[pid][qid1][qid2] + pipeline_2_O[pid][qid2][qid1] >= pipeline_2_I[pid][qid1] +
                            pipeline_2_I[pid][qid2] - 1)

                        # if (1-I1) or (1-I2) then !(O12+O21)
                        m.addConstr(
                            pipeline_2_O[pid][qid1][qid2] + pipeline_2_O[pid][qid2][qid1] <= 0.5 * (
                                pipeline_2_I[pid][qid1] + pipeline_2_I[pid][qid2]))

        # create an indicator variable for pipelines
        pipeline_2_ind = {}
        for pid in Q:
            var_name = "P_ind_" + str(pid)
            pipeline_2_ind[pid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

            for qid in Q:
                m.addConstr(pipeline_2_I[pid][qid] <= pipeline_2_ind[pid])

            I_for_P = [pipeline_2_I[pid][qid] for qid in Q]
            m.addConstr(pipeline_2_ind[pid] <= sum(I_for_P))

        # satisfy the constraint, sum(A) == sum(p_ind)
        all_a = [A[gid] for gid in range(len(G))]
        all_p = [pipeline_2_ind[pid] for pid in Q]
        m.addConstr(sum(all_a) == sum(all_p))

        # relate A and I variables
        A_2_I = []
        for gid in range(len(G)):
            g = G[gid]
            I_for_g = []
            for qid in g:
                I_for_g += [pipeline_2_I[pid][qid] for pid in Q]
                A_2_I += I_for_g
                m.addConstr(sum([pipeline_2_I[pid][qid] for pid in Q]) >= A[gid])
            m.addConstr(sum(I_for_g) >= A[gid] * len(g))

        # m.addConstr(sum(A_2_I) == len(Q))

        # objective
        objective_expr = ([table_2_bits[tid] * tables[tid]["last"] for tid in table_2_bits.keys()] +
                          [1000 * (1 - qid_2_last[qid]) for qid in Q])
        m.setObjective(sum(objective_expr), GRB.MINIMIZE)

        # satisfy the constraints on I variable
        for qid in Q:
            tmp = [pipeline_2_I[pid][qid] for pid in Q]
            m.addConstr(sum(tmp) == 1)

        # satisfy mirroring overhead constraint
        total_packets_expr_list = []
        for gid in range(len(G)):
            print(gid, gid_2_doubleD[gid], len(gid_2_doubleD[gid]))
            total_packets_expr_list.append(A[gid] * len(gid_2_doubleD[gid]))

        # Add cloned packet variable
        C = m.addVar(lb=0, ub=clone_max, vtype=GRB.INTEGER, name="Clone")
        m.addConstr(C == sum(total_packets_expr_list) - len(D))
        m.addConstr(C <= clone_max)

        # Add stage variables
        table_2_stage = {}
        for pid in Q:
            table_2_stage[pid] = {}
            for qid in Q:
                table_2_stage[pid][qid] = {}
                for tid in query_2_tables[qid]:
                    var_name = "S_" + str(pid) + "_" + str(qid) + "_" + str(tid)
                    table_2_stage[pid][qid][tid] = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
                    m.addGenConstrIndicator(pipeline_2_I[pid][qid], False, table_2_stage[pid][qid][tid] <= 0)
                    m.addGenConstrIndicator(pipeline_2_I[pid][qid], True, table_2_stage[pid][qid][tid] >= 1)

        # Apply intra-query dependencies
        for pid in Q:
            for qid in Q:
                for (tid1, tid2) in zip(query_2_tables[qid][:-1], query_2_tables[qid][1:]):
                    #m.addConstr(table_2_stage[pid][qid][tid2] - 1 - table_2_stage[pid][qid][tid1] >= 0)
                    m.addGenConstrIndicator(
                        pipeline_2_I[pid][qid], True,
                        table_2_stage[pid][qid][tid2] - table_2_stage[pid][qid][tid1] >= 1)

        # create sigma variables
        pid_2_sigma = {}
        for pid in Q:
            var_name = "sigma_" + str(pid)
            pid_2_sigma[pid] = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)

        # relate sigma with I
        for pid in Q:
            I_for_pid = [(len(query_2_tables[qid]) * pipeline_2_I[pid][qid]) for qid in Q]
            m.addConstr(sum(I_for_pid) == pid_2_sigma[pid])

        # # apply inter-query dependencies
        for pid in Q:
            for qid1 in Q:
                last_tid_1 = query_2_tables[qid1][-1]
                first_tid_1 = query_2_tables[qid1][0]
                for qid2 in Q:
                    if qid1 != qid2:
                        last_tid_2 = query_2_tables[qid2][-1]
                        first_tid_2 = query_2_tables[qid2][0]
                        m.addGenConstrIndicator(
                            pipeline_2_O[pid][qid1][qid2], True,
                            table_2_stage[pid][qid2][first_tid_2] - table_2_stage[pid][qid1][last_tid_1] >= 1)

                        m.addGenConstrIndicator(
                            pipeline_2_O[pid][qid2][qid1], True,
                            table_2_stage[pid][qid1][first_tid_1] - table_2_stage[pid][qid2][last_tid_2] >= 1)


        # # add E & F variables
        # qid_2_E = {}
        # qid_2_F = {}
        #
        # for qid in Q:
        #     qid_2_E[qid] = {}
        #     qid_2_F[qid] = {}
        #     for tid in query_2_tables[qid]:
        #         # add E variable
        #         var_name = "E_"+str(qid)+"_"+str(tid)
        #         qid_2_E[qid][tid] = m.addVar(lb=1, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
        #
        #         # add F variable
        #         var_name = "F_"+str(qid)+"_"+str(tid)
        #         qid_2_F[qid][tid] = m.addVar(lb=1, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
        #         m.addConstr(qid_2_F[qid][tid] <= qid_2_E[qid][tid])
        #
        # # apply intra-query dependency constraints
        # for qid in Q:
        #     for (tid1, tid2) in zip(query_2_tables[qid][:-1], query_2_tables[qid][1:]):
        #         m.addConstr(1+qid_2_E[qid][tid1] <= qid_2_F[qid][tid2])
        #
        # # apply inter-query dependency constraints
        # for qid1 in Q:
        #     last_tid_1 = query_2_tables[qid1][-1]
        #     first_tid_1 = query_2_tables[qid1][0]
        #     for qid2 in Q:
        #         last_tid_2 = query_2_tables[qid2][-1]
        #         first_tid_2 = query_2_tables[qid2][0]
        #         if qid1 != qid2:
        #             print((qid1,last_tid_1), (qid2,first_tid_2))
        #             print((qid2,last_tid_2), (qid1,first_tid_1))
        #             var_name = "tmp_y_"+str(qid1)+"_"+str(qid2)
        #             tmp_y = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)
        #             M = 2
        #             m.addConstr(o_vars[qid1][qid2] <= M*tmp_y)
        #             # m.addConstr(qid_2_E[qid1][last_tid_1] - qid_2_F[qid2][first_tid_2] + 1 <= M*(1-tmp_y))
        #
        #             # m.addConstr(qid_2_F[qid2][last_tid_2] - qid_2_E[qid1][first_tid_1] + 1 <= tmp_y2)
        #             # m.addConstr(-1*qid_2_F[qid2][last_tid_2] + qid_2_E[qid1][first_tid_1] + 1 <= 1-tmp_y2)
        #
        # # create W variable
        # W = {}
        # for sid in range(1,1+sigma_max):
        #     W[sid] = {}
        #     for tid in table_2_bits.keys():
        #         var_name = "W_"+str(sid)+"_"+str(tid)
        #         W[sid][tid] = m.addVar(lb=1, ub=table_2_bits[tid], vtype=GRB.INTEGER, name=var_name)
        #
        # # apply assignment constraint
        # for tid in table_2_bits.keys():
        #     tmp = [W[sid][tid] for sid in range(1,1+sigma_max)]
        #     m.addConstr(sum(tmp) <= tables[tid]["d"]*table_2_bits[tid])
        #
        # # apply memory constraint
        # for sid in range(1,1+sigma_max):
        #     tmp = [W[sid][tid] for tid in table_2_bits.keys()]
        #     m.addConstr(sum(tmp) <= bits_max)
        #
        # # apply stage constraint
        # # create stage indicator variable SI
        # SIs = {}
        # sigma = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name="sigma")
        # for sid in range(1,1+sigma_max):
        #     var_name = "SI_"+str(sid)
        #     SIs[sid] = m.addVar(lb=0, ub=1, vtype=GRB.INTEGER, name=var_name)
        #
        # for sid in range(1,1+sigma_max):
        #     m.addConstr(sigma >= sid*SIs[sid])
        #     tmp = [W[sid][tid] for tid in table_2_bits.keys()]
        #     m.addConstr(sum(tmp) >= SIs[sid])
        m.write(name + ".lp")
        m.optimize()
        print('Obj:', m.objVal)
        for v in m.getVars():
            print(v.varName, v.x)

    except GurobiError:
        print('Error reported', GurobiError.message)


if __name__ == '__main__':
    solve_sonata_lp()
