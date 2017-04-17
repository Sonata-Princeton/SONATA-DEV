import pickle
import csv
import numpy as np


def process_parser_overhead_result(fname):
    type_2_time = {}
    with open(fname, 'r') as f:
        csv_f = csv.reader(f)

        for row in csv_f:
            (_,type,t1,t2) = row
            if type == 'sonata':
                if 'sonata' not in type_2_time:
                    type_2_time['sonata'] =[]
                # time in milliseconds
                type_2_time['sonata'].append(1000*(float(t2)-float(t1)))

            else:
                if 'dns' not in type_2_time:
                    type_2_time['dns'] =[]
                type_2_time['dns'].append(1000*(float(t2)-float(t1)))
    print [np.median(type_2_time[x]) for x in ['dns', 'sonata']]


def process_driver_overhead_result(fname):
    # update,310,1492376828.67471289634704589844,1492376828.86602807044982910156
    add_count_2_time = {}
    del_count_2_time = {}
    with open(fname, 'r') as f:
        csv_f = csv.reader(f)
        for row in csv_f:
            (type,count,t1,t2) = row
            count = int(count)
            if type == 'update':
                if count not in add_count_2_time:
                    add_count_2_time[count] = []
                add_count_2_time[count].append(1000*(float(t2)-float(t1)))
            else:
                if count not in del_count_2_time:
                    del_count_2_time[count] = []
                del_count_2_time[count].append(1000*(float(t2)-float(t1)))

    for count in add_count_2_time:
        add_count_2_time[count] = np.median(add_count_2_time[count])

    for count in del_count_2_time:
        del_count_2_time[count] = np.median(del_count_2_time[count])

    print add_count_2_time, del_count_2_time




if __name__ == '__main__':
    fname_parser = 'data/parser_overhead.log'
    fname_driver = 'data/driver_overhead.log'
    process_parser_overhead_result(fname_parser)
    process_driver_overhead_result(fname_driver)
