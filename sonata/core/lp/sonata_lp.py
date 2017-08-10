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

        # Add pipeline specific variables
        pipeline_2_I = {}
        pipeline_2_O = {}
        pipeline_2_A = {}
        for pid in Q:
            pipeline_2_O[pid] = {}
            pipeline_2_I[pid] = {}
            pipeline_2_A[pid] = {}

            # create A variables
            for gid in range(len(G)):
                var_name = "A_" + str(pid) + "_" + str(gid)
                pipeline_2_A[pid][gid] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

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

        # # satisfy the constraint, sum(A) == sum(p_ind)
        # all_a = [A[gid] for gid in range(len(G))]
        # all_p = [pipeline_2_ind[pid] for pid in Q]
        # m.addConstr(sum(all_a) == sum(all_p))

        for qid in Q:
            I_for_P = [pipeline_2_I[pid][qid] for pid in Q]
            m.addConstr(sum(I_for_P) <= 1)

        for gid in range(len(G)):
            A_for_P = [pipeline_2_A[pid][gid] for pid in Q]
            m.addConstr(sum(A_for_P) <= 1)


        # relate A and I variables
        for pid in Q:
            for gid in range(len(G)):
                g = G[gid]
                for qid in g:
                    m.addGenConstrIndicator(pipeline_2_A[pid][gid], True, pipeline_2_I[pid][qid] == 1)

        for pid in Q:
            for qid in Q:
                tmp = []
                for gid in range(len(G)):
                    g = G[gid]
                    if qid in g:
                        tmp.append(pipeline_2_A[pid][gid])
                m.addConstr(sum(tmp) == pipeline_2_I[pid][qid])

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
        for pid in Q:
            for gid in range(len(G)):
                print(gid, gid_2_doubleD[gid], len(gid_2_doubleD[gid]))
                total_packets_expr_list.append(pipeline_2_A[pid][gid] * len(gid_2_doubleD[gid]))

        # Add cloned packet variable
        C = m.addVar(lb=0, ub=clone_max, vtype=GRB.INTEGER, name="Clone")
        m.addConstr(C == sum(total_packets_expr_list) - len(D))
        m.addConstr(C <= clone_max)

        table_2_stageE = {}
        table_2_stageF = {}
        for pid in Q:
            table_2_stageE[pid] = {}
            table_2_stageF[pid] = {}
            for qid in Q:
                table_2_stageE[pid][qid] = {}
                table_2_stageF[pid][qid] = {}
                for tid in query_2_tables[qid]:
                    var_name = "SE_" + str(pid) + "_" + str(qid) + "_" + str(tid)
                    table_2_stageE[pid][qid][tid] = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
                    m.addGenConstrIndicator(pipeline_2_I[pid][qid], False, table_2_stageE[pid][qid][tid] <= 0)
                    m.addGenConstrIndicator(pipeline_2_I[pid][qid], True, table_2_stageE[pid][qid][tid] >= 1)

                    var_name = "SF_" + str(pid) + "_" + str(qid) + "_" + str(tid)
                    table_2_stageF[pid][qid][tid] = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)
                    m.addGenConstrIndicator(pipeline_2_I[pid][qid], False, table_2_stageF[pid][qid][tid] <= 0)
                    m.addGenConstrIndicator(pipeline_2_I[pid][qid], True, table_2_stageF[pid][qid][tid] >= 1)

                    m.addConstr(table_2_stageF[pid][qid][tid] <= table_2_stageE[pid][qid][tid])

        # Apply intra-query dependencies
        for pid in Q:
            for qid in Q:
                for (tid1, tid2) in zip(query_2_tables[qid][:-1], query_2_tables[qid][1:]):
                    #m.addConstr(table_2_stage[pid][qid][tid2] - 1 - table_2_stage[pid][qid][tid1] >= 0)
                    m.addGenConstrIndicator(
                        pipeline_2_I[pid][qid], True,
                        table_2_stageF[pid][qid][tid2] - table_2_stageE[pid][qid][tid1] >= 1)

        # create sigma variables
        pid_2_sigma = {}
        for pid in Q:
            var_name = "sigma_" + str(pid)
            pid_2_sigma[pid] = m.addVar(lb=0, ub=sigma_max, vtype=GRB.INTEGER, name=var_name)

        # relate sigma with I
        for pid in Q:
            I_for_pid = [(len(query_2_tables[qid]) * pipeline_2_I[pid][qid]) for qid in Q]
            m.addConstr(sum(I_for_pid) == pid_2_sigma[pid])

        # apply inter-query dependencies
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
                            table_2_stageF[pid][qid2][first_tid_2] - table_2_stageE[pid][qid1][last_tid_1] >= 1)

                        m.addGenConstrIndicator(
                            pipeline_2_O[pid][qid2][qid1], True,
                            table_2_stageF[pid][qid1][first_tid_1] - table_2_stageE[pid][qid2][last_tid_2] >= 1)

        # create W variable
        W = {}

        for pid in Q:
            W[pid] = {}
            for qid in Q:
                W[pid][qid] = {}
                for tid in query_2_tables[qid]:
                    W[pid][qid][tid] = {}
                    for sid in range(1, 1+sigma_max):
                        var_name = "W_"+str(pid)+"_"+str(qid)+"_"+str(tid)+"_"+str(sid)
                        W[pid][qid][tid][sid] = m.addVar(lb=0, ub=table_2_bits[tid], vtype=GRB.INTEGER, name=var_name)
                        m.addGenConstrIndicator(pipeline_2_I[pid][qid], False, W[pid][qid][tid][sid] == 0)

        # apply assignment constraint
        for qid in Q:
            for tid in query_2_tables[qid]:
                for pid in Q:
                    tmp = [W[pid][qid][tid][sid] for sid in range(1, 1+sigma_max)]
                    var_name = "tmp_y_"+str(qid)+"_"+str(tid)+str(pid)
                    tmp_y = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)
                    m.addConstr(tmp_y >= pipeline_2_I[pid][qid]+tables[tid]["d"]-1)
                    m.addGenConstrIndicator(tmp_y, True, sum(tmp) >= table_2_bits[tid])

        # apply memory constraint
        for sid in range(1, 1+sigma_max):
            W_for_S = []
            for pid in Q:
                for qid in Q:
                    for tid in query_2_tables[qid]:
                        W_for_S.append(W[pid][qid][tid][sid])

            m.addConstr(sum(W_for_S) <= bits_max)

        # relate W and stageE and stageF variables
        for pid in Q:
            for qid in Q:
                for tid in query_2_tables[qid]:
                    for sid in range(1, 1+sigma_max):
                        # if W[pid][qid][tid][sid] > 0 then,
                        # table_2_stageF[pid][qid][tid] <= sid and  table_2_stageE[pid][qid][tid] >= sid

                        # create a new indicator variable
                        var_name = "fin_ind_"+str(pid)+"_"+str(qid)+"_"+str(tid)+"_"+str(sid)
                        tmp_ind = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)
                        m.addGenConstrIndicator(tmp_ind, False, W[pid][qid][tid][sid] == 0)
                        m.addGenConstrIndicator(tmp_ind, True, table_2_stageF[pid][qid][tid] <= sid)
                        m.addGenConstrIndicator(tmp_ind, True, table_2_stageE[pid][qid][tid] >= sid)








        # for sid in range(1,1+sigma_max):
        #     W[sid] = {}
        #     for tid in table_2_bits.keys():
        #         var_name = "W_"+str(sid)+"_"+str(tid)
        #         W[sid][tid] = m.addVar(lb=1, ub=table_2_bits[tid], vtype=GRB.INTEGER, name=var_name)
        #
        # # apply assignment constraint
        # for qid in Q:
        #     for tid in query_2_tables[qid]:
        #         tmp = [W[sid][tid] for sid in range(1, 1+sigma_max)]
        #         m.addConstr(sum(tmp) >= tables[tid]["d"]*table_2_bits[tid])
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

        out_str = "Stages"
        for sid in range(1,sigma_max+1):
            out_str += "|"+str(sid)
        out_str += "\n"

        for pid in Q:
            out_str += "P"+str(pid)+"|"
            for sid in range(1,sigma_max+1):
                out_sid = ""
                if pipeline_2_ind[pid].x > 0:
                    for qid in Q:
                        if pipeline_2_I[pid][qid].x > 0:
                            for tid in query_2_tables[qid]:
                                if W[pid][qid][tid][sid].x > 0:
                                    out_sid += "(S"+str(sid)+",Q"+str(qid)+",T"+str(tid)+",B="+str(W[pid][qid][tid][sid].x)+"),"
                    out_sid = out_sid[:-1]
                if out_sid == "":
                    out_sid = "XXXX"
                out_str += out_sid+"|"
            out_str += "\n"

        print(out_str)



    except GurobiError:
        print('Error reported', GurobiError.message)


if __name__ == '__main__':
    solve_sonata_lp()
