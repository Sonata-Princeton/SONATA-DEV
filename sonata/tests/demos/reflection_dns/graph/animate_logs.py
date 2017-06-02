"""
A simple example of an animated plot
"""
import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from sonata.tests.macro_bench.graph.plotlib import *
log1 = 'sonata/tests/demos/reflection_dns/graph/emitter.log'

fig, ax = plt.subplots()
line1, = ax.plot(range(10), [100 for x in range(10)], color='r', label='Span Port', linewidth=4.0)
line2, = ax.plot(range(10), [100 for x in range(10)], color='k', label='Input Port', linewidth=4.0, linestyle='--')
pl.xlabel("Time (seconds)")
pl.ylabel("Packets per second")
ax.set_ylim(ymin=1.0)
ax.set_ylim(ymax=110.0)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fancybox=True, shadow=False)
for item in ([ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
ax.grid(True)

t_start = 4


def animate(i):
    print "Reading first", i, "lines"
    with open(log1, 'r') as f:
        csv_f = csv.reader(f)
        ts_packet_count = {}
        ctr = 0
        for row in csv_f:
            (name, qid, start, end) = row
            ts = round(float(start), 0)
            if ts not in ts_packet_count:
                ts_packet_count[ts] = 0
            ts_packet_count[ts] += 1
            ctr += 1

        xdata = []
        ydata = []
        timestamps = ts_packet_count.keys()
        timestamps.sort()
        xmin = timestamps[0]
        print int(i) - t_start

        if 0 < (int(i) - t_start):
            ctr = 0
            for ts in timestamps:
                xdata.append(t_start + ts - xmin)
                ydata.append(ts_packet_count[ts])
                ctr += 1
                if ctr > (int(i) - t_start):
                    break

            print xdata, ydata

            ax.figure.canvas.draw()

        line1.set_data(xdata, ydata)

    return line1,line2



ani = animation.FuncAnimation(fig, animate, np.arange(1, 201), interval=1000)
plt.show()
