#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

import math
import numpy as np


def get_probability(s, thresh):
    if thresh in set(s):
        out = float(s.count(thresh)) / len(s[1])
    return out


def get_cms_width(s, thresh, delta):
    s = list(s)
    max_s = max(s)
    if max_s < thresh:
        max_s = thresh
    bins = range(2 + max_s)
    pdfs, bins = np.histogram(s, bins, density=True)
    bin_2_prob = dict((x, y) for x, y in zip(list(bins), list(pdfs)))
    max_error = 0
    if bin_2_prob != {}:
        error_probability = 0
        bins = list(bins)
        bins.sort(reverse=True)

        for elem in bins:
            if elem <= thresh:
                error_probability += bin_2_prob[elem]
                if error_probability >= delta and elem < thresh and bin_2_prob[elem] > 0:
                    break
                else:
                    max_error = 0.99 + (thresh - elem)
    else:
        max_error = thresh
    N = sum(s)
    w = float(2*N)/max_error

    return int(math.ceil(w))


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
            #bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], math.log(max(s[1]), 2)))
            bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], 16))

            # total number of bits required for this data structure
            # print query_out
            tmp = sc.parallelize(query_out)
            n_bits_wo_cmsketch = bits_per_element.join(tmp).map(lambda s: (s[0], math.ceil(s[1][0] * (len(s[1][1])))))
            #print "W/O Sketches", n_bits_wo_cmsketch.collect()
            n_bits_wo_cmsketch_mean = np.mean(n_bits_wo_cmsketch.map(lambda s: s[1]).collect())

            ## number of bits required with count min sketch

            # number of bits required to maintain the count
            #bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], math.ceil(math.log(max(s[1]), 2))))
            bits_per_element = sc.parallelize(query_out).map(lambda s: (s[0], 16))
            #print "bits/elem:", bits_per_element.collect()

            d = math.ceil(math.log(int(1 / delta), 2))
            #print "d:", d
            w = sc.parallelize(query_out).map(lambda s: (s[0], get_cms_width(s[1], thresh, delta)))
            #print w.collect()

            n_bits_sketch = w.join(bits_per_element).map(lambda s: (s[0], int(s[1][0] * s[1][1] * d)))
            #print "With Sketches", n_bits_sketch.collect()
            n_bits_sketch_mean = np.mean(n_bits_sketch.map(lambda s: s[1]).collect())
            #print "With Sketches", n_bits_sketch_mean, "W/o Sketches", n_bits_wo_cmsketch_mean

            n_bits_min = min([n_bits_wo_cmsketch_mean, n_bits_sketch_mean])
            # print n_bits_min
            if n_bits_min == n_bits_wo_cmsketch_mean:
                n_bits = n_bits_wo_cmsketch
            else:
                n_bits = n_bits_sketch
        else:
            print "Currently not supported"
    #print "n_bits:", n_bits.collect()
    return n_bits


if __name__ == '__main__':
    s = [1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 15]
    thresh = 10
    delta = 0.01
    w = get_cms_width(s, thresh, delta)
    print w
