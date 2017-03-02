from config import *
from utils import *
import math

class CostModel(object):
    def __init__(self, hypothesis):
        self.hypothesis = hypothesis
        self.generate_hypothesis_graph()


    def generate_hypothesis_graph(self):
        weights = {}
        for qid in self.hypothesis.query_out_transit:
            query = self.hypothesis.query_training.qid_2_query[qid]
            partition_plans = query.get_partition_plans()[qid]
            height_partition_tree = len(partition_plans.split(','))
            extreme_plan = [].append_multiple(1, height_partition_tree)
            for transit in self.hypothesis.query_out_transit[qid]:
                (ref_level_prev, ref_level_curr) = transit
                iter_qids_curr = self.hypothesis.refined_spark_queries[qid][ref_level_curr].keys()
                iter_qids_prev = self.hypothesis.refined_spark_queries[qid][ref_level_prev].keys()
                iter_qids_curr.sort()
                iter_qids_prev.sort()

                for partition_plan in partition_plans:
                    target_plan = ','.join(extreme_plan)
                    print partition_plan, transit, target_plan

                    bits_count = 0
                    packet_count = self.hypothesis.query_out_transit[qid][(0,ref_level_prev)][iter_qids_prev[-1]]
                    ctr = 0
                    for iter_qid in iter_qids_curr:
                        if target_plan == partition_plan:
                            break
                        last_operator_name = self.hypothesis.refined_spark_queries[qid][ref_level_curr][iter_qid].operators[-1].name
                        print iter_qid, last_operator_name
                        if last_operator_name in ['Distinct','Reduce']:
                            # Update the number of bits required to perform this operation
                            query_out = self.hypothesis.query_out_transit[qid][transit][iter_qid]
                            bits_count += get_data_plane_cost(last_operator_name, 'sum', query_out, thresh = 1, delta = 0.01)

                            next_operator_name = self.hypothesis.refined_spark_queries[qid][ref_level_curr][iter_qid+1].operators[-1].name
                            if next_operator_name == 'Filter':
                                query_out = self.hypothesis.query_out_transit[qid][transit][iter_qid+1]
                            packet_count -= get_streaming_cost(last_operator_name, query_out)

                            target_plan[ctr] = 0
                            ctr += 1