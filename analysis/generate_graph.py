#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import pickle
import time
import datetime

from sonata.query_engine.sonata_queries import *
from sonata.core.training.utils import get_spark_context_batch, create_spark_context
from sonata.core.integration import Target
from sonata.core.refinement import apply_refinement_plan, get_refined_query_id, Refinement
from sonata.core.training.hypothesis.hypothesis import Hypothesis


def generate_graph(query):
    sc = create_spark_context()
    (timestamps, training_data) = get_spark_context_batch(sc)
    target = Target()
    refinement_object = Refinement(query, target)
    refinement_object.update_filter(training_data)
    hypothesis = Hypothesis(query, sc, training_data, timestamps,refinement_object, target)
    G = hypothesis.G
    fname = 'data/hypothesis_graph_'+str(datetime.datetime.fromtimestamp(time.time()))+'.pickle'

    # dump the hypothesis graph: {ts:G[ts], ...}
    with open(fname, 'w') as f:
        pickle.dump(G, f)

if __name__ == '__main__':
    q1 = (PacketStream(1)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '95'))
          .map(keys=('dIP',))
          )

    generate_graph(q1)