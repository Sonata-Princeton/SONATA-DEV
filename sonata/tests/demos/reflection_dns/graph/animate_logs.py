"""
A simple example of an animated plot
"""
import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from sonata.tests.macro_bench.graph.plotlib import *


log1 = 'sonata/tests/demos/reflection_dns/graph/emitter.log'

total_duration = 30
attack_duration = 10
attack_start_time = 5
NORMAL_PACKET_COUNT = 50

ATTACK_PACKET_COUNT = 50


fig, ax = plt.subplots()

fig.canvas.set_window_title("DNS Reflection Demo")

line1, = ax.plot(range(total_duration), [0 for x in range(total_duration)], color='r', label='Span Port', linewidth=4.0)
line2, = ax.plot(range(total_duration), [NORMAL_PACKET_COUNT for x in range(total_duration)], color='k', label='Input Port', linewidth=4.0, linestyle='--')
pl.xlabel("Time (seconds)")
pl.ylabel("Packets per second")
ax.set_ylim(ymin=0)

ax.set_ylim(ymax=10+NORMAL_PACKET_COUNT+ATTACK_PACKET_COUNT)

ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fancybox=True, shadow=False)
for item in ([ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
ax.grid(True)


def animate(i):
    with open(log1, 'r') as f:
        csv_f = csv.reader(f)
        ts_packet_count = {}
        ctr = 0

        # count_per_query = {}
        for row in csv_f:
            (name, qid, start, end) = row
            ts = round(float(start), 0)
            # if qid not in count_per_query:
            #     count_per_query[qid] = 0
            # count_per_query[qid] += 1

            if ts not in ts_packet_count:
                ts_packet_count[ts] = 0
            ts_packet_count[ts] += 1
            ctr += 1

        # print ts_packet_count
        # if '10016' in count_per_query: print "Received packets for /16: "+count_per_query['10016']
        # if '30032' in count_per_query: print "Received packets for /32: "+count_per_query['30032']

        xdata = range(1+i)
        ydata = [0 for x in range(1+i)]

        x2data = range(1+i)
        y2data = [NORMAL_PACKET_COUNT for x in range(1+i)]
        timestamps = ts_packet_count.keys()
        if len(timestamps) > 0:
            timestamps.sort()
            xmin = timestamps[0]


            if 0 <= (int(i) - attack_start_time):
                ctr = 0
                for ts in timestamps:
                    index_to_update = attack_start_time + ts - xmin
                    # xdata.append(attack_start_time + ts - xmin)
                    ydata[int(index_to_update)] = ts_packet_count[ts]
                    y2data[int(index_to_update)] += ATTACK_PACKET_COUNT

                    ctr += 1
                    if ctr > (int(i) - attack_start_time):
                        break

        ax.figure.canvas.draw()
        line1.set_data(xdata, ydata)
        line2.set_data(x2data, y2data)

    return line1,line2



ani = animation.FuncAnimation(fig, animate, np.arange(1, 201), interval=1000)
plt.show()
