#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import math


def get_data_plane_cost(sc, operator_name, transformation_function, query_out, thresh=1, delta=0.01):
    # get data plane cost for given query output and operator name
    n_bits = 0
    if operator_name == "Distinct":
        # here query_out query_out = [(ts,#distinct elements), ...]
        bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], 1))

        # total number of bits required for this data structure
        tmp = sc.parallelize(query_out)
        n_bits = bits_per_element.join(tmp).map(lambda s: (s[0], math.ceil(s[1][0] * s[1][1])))

    elif operator_name == "Reduce":
        if transformation_function == 'sum':
            # it can use count-min sketch, here query_out = [(ts,[count1, count2, ...]), ...]

            ## number of bits required w/o using any sketch
            # number of bits required to maintain the count
            bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], math.log(max(s[1]), 2)))

            # total number of bits required for this data structure
            # print query_out
            tmp = sc.parallelize(query_out)
            n_bits_wo_cmsketch = bits_per_element.join(tmp).map(lambda s: (s[0], math.ceil(s[1][0] * (len(s[1][1])))))
            # print "W/O Sketches", n_bits_wo_cmsketch.collect()
            n_bits_wo_cmsketch_max = max(n_bits_wo_cmsketch.map(lambda s: s[1]).collect())

            ## number of bits required with count min sketch

            # number of bits required to maintain the count
            bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], math.ceil(math.log(max(s[1]), 2))))
            # print "bits/elem:", bits_per_element.collect()

            d = math.ceil(math.log(int(1 / delta), 2))
            # print "d:", d
            # get the probability of threshold value for the given threshold
            # print thresh
            f_th = sc.parallelize(query_out).map(lambda s: (s[0], float(s[1].count(thresh)) / len(s[1])))
            N = sc.parallelize(query_out).map(lambda s: (s[0], float(sum(s[1]))))
            # print "f_th:", f_th.collect()
            # print "N:", N.collect()
            w = f_th.join(N).map(lambda s: (s[0], math.ceil(4 * s[1][1] * s[1][0] / delta)))
            # print "w:", w.collect()

            n_bits_sketch = w.join(bits_per_element).map(lambda s: (s[0], int(s[1][0] * s[1][1] * d)))
            # print "With Sketches", n_bits_sketch.collect()
            n_bits_sketch_max = max(n_bits_sketch.map(lambda s: s[1]).collect())
            # print "With Sketches", n_bits_sketch_max, "W/o Sketches", n_bits_wo_cmsketch_max

            n_bits_min = min([n_bits_wo_cmsketch_max, n_bits_sketch_max])
            # print n_bits_min
            if n_bits_min == n_bits_wo_cmsketch_max:
                n_bits = n_bits_wo_cmsketch
            else:
                n_bits = n_bits_sketch

        else:
            print "Currently not supported"
    return n_bits
