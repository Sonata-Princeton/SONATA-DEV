import csv

from sonata.tests.macro_bench.graph.plotlib import *

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

# original_packet_count = {1453381248.0: 5542, 1453381249.0: 5646, 1453381250.0: 5452, 1453381251.0: 5425, 1453381252.0: 5506, 1453381253.0: 5608, 1453381254.0: 5479, 1453381255.0: 5538, 1453381256.0: 5487, 1453381257.0: 5623, 1453381258.0: 5484, 1453381259.0: 5599, 1453381260.0: 2834, 1453381200.0: 7257, 1453381201.0: 9081, 1453381202.0: 9060, 1453381203.0: 8227, 1453381204.0: 8096, 1453381205.0: 7488, 1453381206.0: 7087, 1453381207.0: 7025, 1453381208.0: 6972, 1453381209.0: 6841, 1453381210.0: 6898, 1453381211.0: 6988, 1453381212.0: 6667, 1453381213.0: 6728, 1453381214.0: 6452, 1453381215.0: 6551, 1453381216.0: 6571, 1453381217.0: 6333, 1453381218.0: 6393, 1453381219.0: 6252, 1453381220.0: 6350, 1453381221.0: 5999, 1453381222.0: 6194, 1453381223.0: 6225, 1453381224.0: 6127, 1453381225.0: 6059, 1453381226.0: 6293, 1453381227.0: 6272, 1453381228.0: 6237, 1453381229.0: 5939, 1453381230.0: 6117, 1453381231.0: 6133, 1453381232.0: 6103, 1453381233.0: 5880, 1453381234.0: 6011, 1453381235.0: 6020, 1453381236.0: 5896, 1453381237.0: 5739, 1453381238.0: 5877, 1453381239.0: 5703, 1453381240.0: 5811, 1453381241.0: 5707, 1453381242.0: 5594, 1453381243.0: 5684, 1453381244.0: 5593, 1453381245.0: 5483, 1453381246.0: 5591, 1453381247.0: 5668}

def plot_line(xlab, data, xlab2, data2, XLabel, YLabel, fname):

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    pl.plot(range(xlab), data, color=color_n[0],linestyle=linestyles[0], linewidth=2.0)
    pl.plot(range(xlab2), data2, color=color_n[1],linestyle=linestyles[1], linewidth=2.0)

    pl.xlabel(XLabel)
    pl.ylabel(YLabel)

    ax.set_ylim(ymin=0.0)
    ax.grid(True)
    plt.tight_layout()

    plot_name = fname+'.eps'
    pl.savefig(plot_name)

    plot_name = fname+'.png'
    pl.savefig(plot_name)

f = open('../results/emitter.log')
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

# original_ts_sorted = original_packet_count.keys()
# original_ts_sorted.sort()

data = []
ordered_ts = ts_packet_count.keys()
ordered_ts.sort()
print ordered_ts
for ts in ordered_ts:
    data.append(ts_packet_count[ts])

data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + data + [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

data_original = []
ctr = 1
for ts in range(0, 60):
    count = 100
    if ts > 20 and ts < 31:
        count += 304
    data_original.append(count)
    ctr += 1

data_original = [114, 143, 141, 127, 112, 119, 111, 132, 135, 129, 134, 131, 134, 101, 114, 147, 126, 104, 135, 143, 101, 444, 409, 436, 426, 425, 439, 426, 412, 436, 416, 135, 148, 135, 103, 139, 117, 123, 136, 124, 109, 128, 105, 110, 118, 126, 139, 134, 146, 109, 128, 135, 118, 104, 114, 131, 109, 114, 109, 101]

print "Original Data",len(data_original), data_original


print data, len(ordered_ts)
plot_line(len(data), data, len(data_original[1:]), data_original[1:],
          'Time (seconds)',
          'Number of Packets',
          '../graph/macro_n_packets')
