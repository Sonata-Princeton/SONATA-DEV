from plotlib import *
import numpy as np
import pickle
import math
import csv

color_n=['r','b','k','g','m','k','w']
markers=['o','*','^','s','d','3','d','o','*','^','1','4']
linestyles=[ '-',':','--','-.','--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.']

"""
emitter,13107,1485140031.82,1485140031.82
emitter,10008,1485140031.82,1485140031.82
emitter,13107,1485140032.26,1485140032.26
emitter,13107,1485140035.82,1485140035.82
emitter,10008,1485140035.82,1485140035.82
emitter,13107,1485140036.27,1485140036.27
emitter,10008,1485140036.27,1485140036.27
emitter,10008,1485140044.87,1485140044.87
emitter,10008,1485140044.87,1485140044.87
"""

def plot_line(xlab, data, XLabel, YLabel, fname):

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    pl.plot(range(xlab), data, color=color_n[0],linestyle=linestyles[0], linewidth=2.0)

    pl.xlabel(XLabel)
    pl.ylabel(YLabel)

    ax.set_ylim(ymin=0.0)
    ax.grid(True)
    plt.tight_layout()

    plot_name = fname+'.eps'
    pl.savefig(plot_name)

f = open('macro_bench/emitter.log')
csv_f = csv.reader(f)

ts_packet_count = {}

for row in csv_f:
    print row
    (name, qid, start, end) = row
    ts = round(float(start), 0)
    if ts not in ts_packet_count:
        ts_packet_count[ts] = 0
    ts_packet_count[ts] += 1

print "Number of TSs: ",len(ts_packet_count.keys())
print ts_packet_count

data = []
ordered_ts = ts_packet_count.keys()
ordered_ts.sort()
print ordered_ts
for ts in ordered_ts:
    data.append(ts_packet_count[ts])

print data, len(ordered_ts)
plot_line(len(ordered_ts), data, 'Threshold (Percentile)', 'Number of Buckets (Normalized)', 'macro_n_packets')

