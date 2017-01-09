#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)

def get_original_wo_mask(lstOfFields):
    fields = []

    for field in lstOfFields:
        if '/' in field:
            fields.append(field.split('/')[0])
        else:
            fields.append(field)

    return fields

def copy_operators(query, optr):
    if optr.name == 'Filter':
        query.filter(filter_keys=optr.filter_keys,
                     filter_vals=optr.filter_vals,
                     func=optr.func,
                     src=optr.src)
    elif optr.name == "Map":
        query.map(keys=optr.keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=optr.keys,
                     values=optr.values,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=optr.keys,
                       values=optr.values)

def copy_sonata_operators_to_spark(query, optr):
    print "Adding spark operator", optr.name
    prev_keys = get_original_wo_mask(optr.prev_keys)
    keys = get_original_wo_mask(optr.keys)
    if optr.name == 'Filter':
        query.filter(filter_keys=optr.filter_keys,
                     filter_vals=optr.filter_vals,
                     func=optr.func)
    elif optr.name == "Map":
        query.map(keys=keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=keys)



def initialize_spark_query(p4_query, spark_query, qid):
    print "Initializing Spark Query Object"
    if len(p4_query.operators) > 0:
        hdrs = list(p4_query.operators[-1].out_headers)
    else:
        raise NotImplementedError
    if p4_query.parse_payload: hdrs += ['payload']
    print "Headers", hdrs
    spark_query.basic_headers = ['k'] + hdrs
    spark_query = (spark_query.filter(keys=spark_query.basic_headers,
                                      filter_keys=('qid',),
                                      func=('eq',"'"+str(qid)+"'")))
    return False, spark_query


def filter_payload(keys):
    return filter(lambda x: x!= 'payload', keys)


def copy_sonata_operators_to_p4(query, optr):
    print "Adding P4 operator", optr.name
    keys = filter_payload(optr.keys)
    if optr.name == 'Filter':
        query.filter(keys=keys,
                     filter_keys=optr.filter_keys,
                     func=optr.func,
                     src=optr.src)
    elif optr.name == "Map":
        query.map(keys = keys,
                  map_keys=optr.map_keys,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys)

    elif optr.name == "Distinct":
        query.distinct(keys=keys)