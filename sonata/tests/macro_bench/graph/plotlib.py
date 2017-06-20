#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import cumfreq
import pylab as pl
import numpy as np
from matplotlib.ticker import MaxNLocator
my_locator = MaxNLocator(6)

def plotCDF(data, order, xlabel, ylabel, Xmax, Xmin, fname, labels = None, isLog=False):
    xlab=[]
    raw={}
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    color_n=['r','b','k','g','m','k','w']
    markers=['o','*','^','s','d','3','d','o','*','^','1','4']
    linestyles=[ '-',':','--','-.','--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.']
    p1=[]
    legnd=[]
    i=0

    # To determine to plotting order
    if labels == None:
        labels = order
    print labels


    for key in labels:
        print key, data.keys()
        raw[key]=data[key]
        #print raw[key]
        raw[key].sort(reverse=True)
        num_bins=10000
        counts, bin_edges = np.histogram(raw[key],bins=num_bins,normed=True)
        cdf=np.cumsum(counts)
        scale = 1.0/cdf[-1]
        cdf=cdf*scale
        p1.append([])
        pl.plot(bin_edges[1:],cdf,label=key,color=color_n[i],linestyle=linestyles[i], linewidth=2.0)
        i+=1


    #pl.legend((p),legnd,'lower right')
    if len(labels)> 1:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
                  ncol=5, fancybox=True, shadow=False)
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    if isLog:
        pl.xscale('log')
    if Xmin != 'N/A':
        ax.set_xlim(xmin=Xmin)
    if Xmax != 'N/A':
        ax.set_xlim(xmax=Xmax)
    ax.set_ylim(ymax=1.0)
    ax.set_ylim(ymin=0.0)
    ax.grid(True)
    plt.tight_layout()
    plot_name= fname+'.eps'
    plot_name_png= fname+'.png'
    plot_name_jpg= fname+'.jpg'
    pl.savefig(plot_name)
    #pl.savefig(plot_name_png)
    #pl.savefig(plot_name_jpg)


def plotLine(data, order, xlabel, ylabel, Xmax, Xmin, fname, labels = None):
    xlab=[]
    raw={}
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    color_n=['r','k','g','c','m','b','m', 'g','m','c','r','b','k','g','m','c','r','b','k', 'g','m','c','r','b','k','w']
    markers=['o','*','^','s','d','3','d','o','*','^','1','4','o','*','^','s','d','3','d','o','*','^','1','4','o','*','^','s','d','3','d','o','*','^','1','4']
    linestyles=[ '-',':','--','-.','--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.', '--',':','-','-.']
    p1=[]
    legnd=[]
    i=0

    # To determine to plotting order
    if labels == None:
        labels = order


    for key in labels:
        raw[key]=data[key]
        raw[key].sort(reverse=True)
        num_bins=10000
        counts, bin_edges = np.histogram(raw[key],bins=num_bins,normed=True)
        cdf=np.cumsum(counts)
        scale = 1.0/cdf[-1]
        cdf=cdf*scale
        p1.append([])
        legnd.append(''+str(key))
        p1[i]=pl.plot(bin_edges[1:],cdf,label=key,color=color_n[i],linestyle=linestyles[i])
        i+=1
    i=0
    p=[]
    for k in data:
        p.append(p1[i][0])
        i+=1

    pl.legend((p),legnd,'lower right')
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    if Xmin != 'N/A':
        ax.set_xlim(xmin=Xmin)
    if Xmax != 'N/A':
        ax.set_xlim(xmax=Xmax)
    ax.set_ylim(ymax=1.0)
    ax.set_ylim(ymin=0.0)
    ax.grid(True)
    plt.tight_layout()
    plot_name= fname+'.eps'
    plot_name_png= fname+'.png'
    plot_name_jpg= fname+'.jpg'
    pl.savefig(plot_name)
    pl.savefig(plot_name_png)
    #pl.savefig(plot_name_jpg)