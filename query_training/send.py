from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener



class TupleEmitter(object):
    emitter_conf = {'spark_stream_address': 'localhost','spark_stream_port': 7979,
                    'window_interval' : 10
                    }
    fname = "/home/vagrant/dev/data/sample_data/sample_data.csv"

    def __init__(self):
        self.spark_stream_address = self.emitter_conf['spark_stream_address']
        self.spark_stream_port = self.emitter_conf['spark_stream_port']
        self.window_interval =  self.emitter_conf['window_interval']

        self.ipfix_data = self.load_data()
        self.ordered_ts = self.ipfix_data.keys()
        self.ordered_ts.sort()
        print "Loaded IPFIX data, all set to send packet tuples"

        self.listener = Listener((self.spark_stream_address, self.spark_stream_port))
        self.start()

    def start(self):
        while True:
            print "Waiting for socket"
            self.spark_conn = self.listener.accept()
            print "Now we can send the data to Stream Processor"
            self.start_send(self.window_interval)

    def start_send(self, window_interval):
        '''
        reads packets from IPFIX data file,
        sorts the time stamps, and
        sends them at regular intervals to P4-enabled switch.
        '''

        print "Total flow entries:", len(self.ordered_ts)

        #while True:
        print "Sending packets to P4 switch"
        current_time = 0
        flow_ctr = 0
        for ts in self.ordered_ts[:1000]:
            pkt_tuples = self.ipfix_data[ts]
            time_start = math.ceil(ts / window_interval)
            #time.sleep(1)
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
                #time.sleep(time_to_sleep)

                # update the current time stamp
                current_ts = time.time()
                # update flow count
                flow_ctr = 0
                #break

            else:
                #print line
                flow_ctr += 1
                for pkt_tuple in pkt_tuples:
                    pkt_tuple = [time_start] + list(pkt_tuple[2:-2])+[1,1]
                    print pkt_tuple
                    send_tuple = ",".join([str(x) for x in pkt_tuple])+ "\n"
                    print send_tuple
                    self.send_tuples(send_tuple)
                    break



    def load_data(self):
        print "load_data called"
        data = {}
        with open(self.fname, 'r') as f:
            for line in f:
                tmp = line.split("\n")[0].split(",")
                #send_packet(tmp[2:])
                ts = int(line.split(",")[0])
                if ts not in data:
                    data[ts] = []
                data[ts].append(tuple(line.split("\n")[0].split(",")))
                #break
        return data


    def send_tuples(self, pkt_tuple):
        self.spark_conn.send_bytes(pkt_tuple)

if __name__ == "__main__":
    te = TupleEmitter()