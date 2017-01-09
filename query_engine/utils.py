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
        query.filter(keys=optr.keys,
                     values=optr.values,
                     filter_keys=optr.filter_keys,
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
    prev_keys = get_original_wo_mask(optr.prev_keys)
    keys = get_original_wo_mask(optr.keys)
    if optr.name == 'Filter':
        query.filter(keys=keys,
                     values=optr.values,
                     filter_keys=optr.filter_keys,
                     prev_keys=prev_keys,
                     prev_values=optr.prev_values,
                     func=optr.func)
    elif optr.name == "Map":
        query.map(keys=keys,
                  values=optr.values,
                  map_keys=optr.map_keys,
                  map_values=optr.map_values,
                  prev_keys=prev_keys,
                  prev_values=optr.prev_values,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=keys,
                     values=optr.values,
                     prev_keys=prev_keys,
                     prev_values=optr.prev_values,
                     func=optr.func)

    elif optr.name == "Distinct":
        query.distinct(keys=keys,
                       values=optr.values,
                       prev_keys=prev_keys,
                       prev_values=optr.prev_values)



def initialize_spark_query(p4_query, spark_query, qid):
    if len(p4_query.operators) > 0:
        hdrs = list(p4_query.operators[-1].out_headers)
    else:
        print "basic", p4_query.keys
        hdrs = p4_query.keys
    if p4_query.parse_payload: hdrs += ['payload']
    spark_query = (spark_query.filter(keys=['k'] + hdrs,
                                      filter_keys=('qid',),
                                      func=('eq',"'"+str(qid)+"'"))
                   .map(prev_keys=("p",), keys=("p[2:]",)))
    return False, spark_query


def copy_sonata_operators_to_p4(query, optr):
    if optr.name == 'Filter':
        query.filter(keys=optr.keys,
                     filter_keys=optr.filter_keys,
                     func=optr.funcs,
                     src=optr.src)
    elif optr.name == "Map":
        query.map(keys = optr.keys,
                  map_keys=optr.map_keys,
                  func=optr.func)
    elif optr.name == "Reduce":
        query.reduce(keys=optr.keys)

    elif optr.name == "Distinct":
        query.distinct(keys=optr.keys)