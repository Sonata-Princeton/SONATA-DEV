#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)


from sonata.query_engine.sonata_queries import *
from sonata.core.training.utils import get_spark_context_batch, create_spark_context
from sonata.core.integration import Target
from sonata.core.refinement import apply_refinement_plan, get_refined_query_id, Refinement
from sonata.core.training.hypothesis.hypothesis import Hypothesis
from sonata.core.partition import get_dataplane_query, get_streaming_query


def compile_queries(query):
    target = Target()
    assert hasattr(target, 'costly_operators')
    refinement_object = Refinement(query, target)

    local_best_plan = [(16, 5, 1), (32, 1, 1)]
    print "# of iteration levels", len(local_best_plan)
    prev_r = 0
    dp_queries = {}
    sp_queries = {}
    for (r, p, l) in local_best_plan:
        # Get the query id
        refined_query_id = get_refined_query_id(query, r)

        # Generate query for this refinement level
        refined_sonata_query = refinement_object.get_refined_updated_query(r, prev_r)

        if prev_r > 0:
            p += 1

        # Apply the partitioning plan for this refinement level
        dp_query = get_dataplane_query(refined_sonata_query, refined_query_id, p)
        dp_queries[refined_query_id] = dp_query

        # Generate input and output mappings
        sp_query = get_streaming_query(refined_sonata_query, refined_query_id, p)
        sp_queries[refined_query_id] = sp_query

        prev_r = r



if __name__ == '__main__':
    # Follows Table 1 in the paper

    # Traffic anomaly detection (All UDP traffic)
    q1 = (PacketStream(1)
          .filter(filter_keys=('proto',), func=('eq', 17))
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('dIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('dIP',))
          )

    # heavy hitter detection
    q2 = (PacketStream(2)
          .map(keys=('dIP', 'dPort','sPort','sIP'), values=('nBytes',))
          .reduce(keys=('dIP', 'dPort','sPort','sIP',), func=('sum',))
          .filter(filter_vals=('nBytes',), func=('geq', '99'))
          .map(keys=('dIP',))
          )

    # super spreader detection
    q3 = (PacketStream(3)
          .map(keys=('dIP', 'sIP'))
          .distinct(keys=('dIP', 'sIP'))
          .map(keys=('sIP',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('sIP',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99.99'))
          .map(keys=('sIP',))
          )

    # ssh brute forcing
    q4 = (PacketStream(4)
          # .filter(filter_keys=('proto',), func=('eq', 6))
          .map(keys=('dIP', 'sIP', 'nBytes'))
          .distinct(keys=('dIP', 'sIP', 'nBytes'))
          .map(keys=('dIP','nBytes'), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('dIP','nBytes'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('dIP',))
          )

    # DNS TTL change detection
    q5 = (PacketStream(5)
          .filter(filter_keys=('sPort',), func=('eq', 53))
          .map(keys=('domain', 'ttl'), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('domain', 'ttl'), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('domain',))
          )

    # IP-2-Domain Anomaly
    q6 = (PacketStream(6)
          .filter(filter_keys=('sPort',), func=('eq', 53))
          .map(keys=('qname', 'rdata'))
          .distinct()
          .map(keys=('rdata',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('rdata',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('rdata',))
          )


    # Domain-2-IP Anomaly
    q7 = (PacketStream(7)
          .filter(filter_keys=('sPort',), func=('eq', 53))
          .map(keys=('qname', 'rdata'))
          .distinct()
          .map(keys=('qname',), map_values=('count',), func=('eq', 1,))
          .reduce(keys=('qname',), func=('sum',))
          .filter(filter_vals=('count',), func=('geq', '99'))
          .map(keys=('qname',))
          )

    # Loop freedom detection
    # q4 = (PacketStream(4)
    #       .map(keys=('flowID', 'path'))
    #       .distinct()
    #       .map(keys=('qname',), map_values=('count',), func=('eq', 1,))
    #       .reduce(keys=('qname',), func=('sum',))
    #       .filter(filter_vals=('count',), func=('geq', '99'))
    #       .map(keys=('qname',))
    #       )


    # Congested link detection

    # Silent packet drop detection

    # Path Conformance detection






    compile_queries(q1)