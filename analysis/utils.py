#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

def get_test_graph(G, n):
    G_out = {}
    timestamps = G.keys()
    timestamps.sort()
    for ts in timestamps[n:]:
        G_out[ts] = G[ts]

    return G_out


def get_training_graph(G, n):
    G_out = {}
    timestamps = G.keys()
    timestamps.sort()
    for ts in timestamps[:n]:
        G_out[ts] = G[ts]

    return G_out


def chunkify(lst, n):
    return [lst[i::n] for i in xrange(n)]