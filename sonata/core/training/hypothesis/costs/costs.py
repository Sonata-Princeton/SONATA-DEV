from itertools import repeat

from sonata.system_config import *

from sonata.core.training.utils import *


class Costs(object):
    def __init__(self, counts, P):
        self.counts = counts
        self.partitioning_plans = P
        self.sc = self.counts.sc
        self.timestamps = self.counts.timestamps
        # Get this from a config file
        self.delta = DELTA
        self.generate_hypothesis_graph()

    def generate_hypothesis_graph(self):
        costs = {}
        for qid in self.counts.query_out_transit:
            costs[qid] = {}
            query = self.counts.qid_2_query[qid]

            # TODO: get rid of this hardcoding
            partition_plans = self.partitioning_plans
            #partition_plans = ['00', '01', '11']

            print "Partitioning Plans:", partition_plans

            for transit in self.counts.query_out_transit[qid]:
                costs[qid][transit] = {}
                (ref_level_prev, ref_level_curr) = transit
                iter_qids_curr = self.counts.refined_spark_queries[qid][ref_level_curr].keys()
                iter_qids_curr.sort()
                part_ids = [x%1000 for x in iter_qids_curr]
                print iter_qids_curr
                for partition_plan in partition_plans:

                    bits_count = self.sc.parallelize([(x,0) for x in self.timestamps])
                    packet_count = self.sc.parallelize(self.counts.query_out_transit[qid][transit][0])
                    print "======="
                    print "W/O Partition"
                    #print "Bits Count Cost", bits_count.collect()[:2]
                    #print "Packet Count Cost", packet_count.collect()[:2]

                    ctr = 0
                    for iter_qid in iter_qids_curr[1:-1]:
                        print partition_plan, transit, iter_qid
                        if iter_qid%1000 == partition_plan:
                            break
                        bits_count, packet_count, ctr = update_counts(self.sc, self.counts.refined_spark_queries[qid][ref_level_curr],
                                                                                   self.counts.query_out_transit[qid][transit],
                                                                                   iter_qid, self.delta, bits_count, packet_count,
                                                                                   ctr)
                    final_weight = bits_count.join(packet_count).map(lambda s: (s[0], (s[1][0], s[1][1]))).collect()
                    #print final_weight[:2]
                    costs[qid][transit][partition_plan] = (final_weight)
        self.costs = costs
        #print self.weights
