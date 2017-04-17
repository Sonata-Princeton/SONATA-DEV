import csv

from analysis.plotlib import *

color_n=['r','k','k','g','m','k','w']
markers=['o','*','^','s','d','3','d','o','*','^','1','4']
linestyles=[ '-',':','--','-.','--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.']


def plot_line(xlab, data, xlab2, data2, XLabel, YLabel, fname):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    color_n = ['r', 'k', 'm', 'c', 'r', 'b', 'm', 'c']
    markers = ['o', '*']
    linestyles = ['-', ':']

    labels = ['Forwarding Port', 'Span Port']
    pl.plot(range(xlab), data, color=color_n[0],linestyle=linestyles[0], label=labels[1])
    pl.plot(range(xlab2), data2, color=color_n[1],linestyle=linestyles[1], label=labels[0])
    if len(labels) > 1:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fancybox=True, shadow=False)

    pl.xlabel('Time (seconds)')
    pl.ylabel('Number of Packets')
    ax.grid(True)
    plt.tight_layout()
    plot_name = fname
    pl.savefig(plot_name)
    ax.locator_params(nbins=6)

    plot_name = fname+'.pdf'
    print plot_name
    pl.savefig(plot_name)


if __name__ == '__main__':
    f = open('data/macro_emitter.log')
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

    data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + data + [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    data_original = [114, 143, 141, 127, 112, 119, 111, 132, 135, 129, 134, 131, 134, 101, 114, 147, 126, 104, 135, 143,
                     101, 444, 409, 436, 426, 425, 439, 426, 412, 436, 416, 135, 148, 135, 103, 139, 117, 123, 136, 124,
                     109, 128, 105, 110, 118, 126, 139, 134, 146, 109, 128, 135, 118, 104, 114, 131, 109, 114, 109, 101]

    print "Original Data",len(data_original), data_original

    print data, len(ordered_ts)
    plot_line(len(data), data, len(data_original[1:]), data_original[1:], 'Time (seconds)', 'Number of Packets',
              'data/macro_n_packets')