#!/usr/bin/env python
#  Author:
#  Arpit Gupta (arpitg@cs.princeton.edu)
import query_engine.spark_queries as spark



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
    #print "Adding spark operator", optr.name
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

def copy_spark_operators_to_spark(query, optr):
    #print "Adding spark operator", optr.name
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

    elif optr.name == 'Join':
        #print "Before Joining", optr.join_query
        optr.in_stream = 'self.training_data.'
        new_join_query = spark.PacketStream(optr.join_query.qid)
        new_join_query.basic_headers = query.basic_headers
        for new_optr in optr.join_query.operators:
            copy_spark_operators_to_spark(new_join_query, new_optr)
        #print "After Updating the Join Query", new_join_query
        query.join(q=new_join_query, join_key = optr.join_key, in_stream = optr.in_stream)


def initialize_spark_query(p4_query, spark_query, qid):
    #print "Initializing Spark Query Object"
    if len(p4_query.operators) > 0:
        hdrs = list(p4_query.operators[-1].out_headers)
    else:
        raise NotImplementedError
    if p4_query.parse_payload: hdrs += ['payload']
    #print "Headers", hdrs
    spark_query.basic_headers = ['k'] + hdrs
    spark_query = spark_query.filter_init(qid=qid, keys=spark_query.basic_headers)
    return False, spark_query


def filter_payload(keys):
    return filter(lambda x: x!= 'payload', keys)


def copy_sonata_operators_to_p4(query, optr):
    #print "Adding P4 operator", optr.name
    keys = filter_payload(optr.keys)
    if optr.name == 'Filter':
        # TODO: get rid of this hardcoding
        if optr.func[0] != 'geq':
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