#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
#  Ankita Pawar (ankscircle@gmail.com)

from sonata.core.utils import *


def get_refined_query_id(query, ref_level):
    return 10000*query.qid + ref_level


def apply_refinement_plan(sonata_query, refinement_key, refined_query_id, ref_level):
    # base refined query + headers
    refined_sonata_query = PacketStream(refined_query_id)
    refined_sonata_query.basic_headers = BASIC_HEADERS

    # Add refinement level, eg: 32, 24
    refined_sonata_query.map(map_keys=(refinement_key,), func=("mask", ref_level))

    # Copy operators to the new refined sonata query
    for operator in sonata_query.operators:
        copy_operators(refined_sonata_query, operator)

    return refined_sonata_query