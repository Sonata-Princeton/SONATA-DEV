from config import *
from utils import *
import math
from itertools import repeat

class CostModel(object):
    def __init__(self, hypothesis):
        self.hypothesis = hypothesis
        self.sc = self.hypothesis.sc
        self.timestamps = self.hypothesis.timestamps
        # Get this from a config file
        self.delta = 0.01


        self.generate_hypothesis_graph()




    def generate_hypothesis_graph(self):
        weights = {}
        for qid in self.hypothesis.query_out_transit:
            weights[qid] = {}
            query = self.hypothesis.query_training.qid_2_query[qid]
            partition_plans = query.get_partition_plans()[qid]
            height_partition_tree = len(partition_plans[-1])
            extreme_plan = [1]
            extreme_plan.extend(repeat(1, height_partition_tree-1))
            #print extreme_plan, height_partition_tree, partition_plans[-1]
            for transit in self.hypothesis.query_out_transit[qid]:
                weights[qid][transit] = {}
                (ref_level_prev, ref_level_curr) = transit
                iter_qids_curr = self.hypothesis.refined_spark_queries[qid][ref_level_curr].keys()
                iter_qids_curr.sort()
                for partition_plan in partition_plans:

                    target_plan = ''.join([str(x) for x in extreme_plan])

                    bits_count = self.sc.parallelize([(x,0) for x in self.timestamps])
                    packet_count = self.sc.parallelize(self.hypothesis.query_out_transit[qid][transit][0])
                    print "======="
                    print "W/O Partition"
                    print "Bits Count Cost", bits_count.collect()[:2]
                    print "Packet Count Cost", packet_count.collect()[:2]

                    ctr = 0
                    for iter_qid in iter_qids_curr[1:-1]:
                        print partition_plan, transit, target_plan
                        if target_plan == partition_plan:

                            break
                        bits_count, packet_count, ctr, target_plan = update_counts(self.sc, self.hypothesis.refined_spark_queries[qid][ref_level_curr],
                                                                      self.hypothesis.query_out_transit[qid][transit],
                                                                      iter_qid, self.delta, bits_count, packet_count,
                                                                       ctr, target_plan)
                    final_weight = bits_count.join(packet_count).map(lambda s: (s[0], (s[1][0], s[1][1]))).collect()
                    print final_weight[:2]
                    weights[qid][transit][partition_plan] = (final_weight)
        self.weights = weights
        #print self.weights
