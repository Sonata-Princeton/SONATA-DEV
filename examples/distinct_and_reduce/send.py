from scapy.all import *
import os
import sys
import glob
import math, time
import pickle

def load_data():
    print "load_data called"
    data = {}
    fname = "/home/vagrant/dev/data/sample_data/sample_data.csv"
    with open(fname, 'r') as f:
        for line in f:
            tmp = line.split("\n")[0].split(",")
            #send_packet(tmp[2:])
            ts = int(line.split(",")[0])
            if ts not in data:
                data[ts] = []
            data[ts].append(tuple(line.split("\n")[0].split(",")))
            #break
    return data


def send_packet(pkt_tuple):
    (sIP, sPort, dIP, dPort, nBytes, proto, sMac, dMac) = pkt_tuple
    p = Ether() / IP(dst=dIP, src=sIP) / TCP(dport=int(dPort), sport=int(sPort)) / "SONATA"
    sendp(p, iface = "out-veth-1", verbose=0)

def send_dummy_packets():
    sIPs = ['112.7.186.20', '112.7.186.19', '112.7.186.19', '112.7.186.18']
    for sIP in sIPs:
        p = Ether() / IP(dst='112.7.186.25', src=sIP) / TCP() / "SONATA"
        p.summary()
        sendp(p, iface = "out-veth-1", verbose=0)


def send_packets(time_slot):
    '''
    reads packets from IPFIX data file,
    sorts the time stamps, and
    sends them at regular intervals to P4-enabled switch.
    '''
    ipfix_data = load_data()
    ordered_ts = ipfix_data.keys()
    ordered_ts.sort()
    print "Total flow entries:", len(ordered_ts)

    #while True:
    print "Sending packets to P4 switch"
    current_time = 0
    flow_ctr = 0
    for ts in ordered_ts[:1000]:
        pkt_tuples = ipfix_data[ts]
        time_start = math.ceil(ts/time_slot)
        if current_time == 0:
            current_time = time_start
            current_ts = time.time()

        if time_start > current_time:
            time_to_process = time.time()-current_ts
            print "Sent ", flow_ctr, "flows between ", time_start, current_time
            print "Took ", time_to_process, " for processing"
            current_time = time_start
            if time_to_process > 1:
                time_to_sleep = 0
            else:
                time_to_sleep = 1 - time_to_process
            print "Sleeping for ",time_to_sleep," second"
            time.sleep(time_to_sleep)

            # update the current time stamp
            current_ts = time.time()
            # update flow count
            flow_ctr = 0
            #break

        else:
            #print line
            flow_ctr += 1
            for pkt_tuple in pkt_tuples:
                send_packet(pkt_tuple[2:])


T = 1000
send_packets(T)
"""
while True:
    print "Sending dummy packets: ...."
    send_dummy_packets()
    time.sleep(1)
"""
