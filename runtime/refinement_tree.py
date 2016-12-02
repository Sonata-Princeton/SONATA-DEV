#!/usr/bin/env python
#  Author:
#  Marc Leef (mleef@cs.princeton.edu)

from query_engine import *
from netaddr import *
from pyspark import SparkContext
from pyspark import SQLContext
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import DoubleType, IntegerType, StringType

# Schema to parse csv of packet tuples
packet_schema = StructType([
    StructField("ts", StringType()),
    StructField("te", StringType()),
    StructField("sIP", IntegerType()),
    StructField("sPort", IntegerType()),
    StructField("dIP", StringType()),
    StructField("dPort", IntegerType()),
    StructField("nBytes", IntegerType()),
    StructField("proto", IntegerType()),
    StructField("sMac", StringType()),
    StructField("dMac", StringType()),
])

# Standard set of packet tuple headers
BASIC_HEADERS = ["ts", "te", "sIP", "sPort", "dIP", "dPort", "nBytes",
                      "proto", "sMac", "dMac"]
BASIC_HEADERS_TUPLE = tuple(BASIC_HEADERS)


class RefinementTree(object):
    """
    RefinementTree structure
    """
    tree = {}

    def __init__(self):

        super(RefinementTree, self).__init__()

# Applies aggregation plan to rdd depending on operation type
def apply_aggregation_plan(rdd, plan):
    operation = plan.operation()
    if operation == "filter":
        rdd.filter(plan.execute())
    elif operation == "map":
        rdd.map(plan.execute)


class AggregationPlan(object):
    """
    Abstract Aggregation Plan Class
    """
    def __init__(self, field, target):
        self.field = field
        self.target = target

    def validate(self, field, target):
        """
        Verify field/target work for given plan.
        """
        return 0

    def operation(self):
        """
        Indicates operation this plan is intended to be used with.
        """
        return 0

    def __str__(self):
        """
        To string override.
        """
        return 0

    def execute(self):
        """
        Execute given plan.
        """
        return 0

    def compile(self, prev_fields):
        """
        Transforms plan to query_engine format.
        """
        return 0


class PrefixPlan(AggregationPlan):
    """
    Plan for IP prefix modification.
    Usage:
        plan = PrefixPlan("dIP", 16)
        stream_rdd.map(plan.execute())
    """

    def __init__(self, field, target):
        self.field = field
        self.validate(field, target)
        self.field_index = BASIC_HEADERS.index(field)
        self.prefix_length = str(target)

    def validate(self, field, target):
        if field not in ["dIP", "sIP"]:
            print(field + ": invalid field for given plan.")
            raise ValueError
        if type(target) != int:
            print(target + ": prefix length must be integer value.")
            raise ValueError

    def operation(self):
        return "map"

    def __str__(self):
        return "PrefixPlan: {} -> {}/{}".format(self.field, self.field, self.prefix_length)

    def execute(self):
        return lambda s: tuple(
            s[:self.field_index] + (str(IPNetwork(s[self.field_index] + '/'
                                                  + self.prefix_length).network),) + s[self.field_index + 1:])

    def compile(self, prev_fields):
        prev_fields_index = prev_fields.index(self.field)
        expr = (self.operation() + '(lambda ('
                + ','.join(str(x) for x in prev_fields)
                + '): ' + str(prev_fields[:prev_fields_index]).replace("\'", "")[:-1]
                + ', str(IPNetwork(' + self.field + ' + \'/' + self.prefix_length + '\').network), '
                + str(prev_fields[prev_fields_index + 1:]).replace("\'", "")[1:] + ')')
        return expr


class ContainmentPlan(AggregationPlan):
    """
    Plan for general filtering based on list inclusion.
    Usage:
        valid_ports = [8080, 57, 3000]
        plan = ContainmentPlan("sPort", valid_ports)
        stream_rdd.filter(plan.execute())
    """

    def __init__(self, field, target):
        self.field = field
        self.validate(field, target)
        self.field_index = BASIC_HEADERS.index(field)
        self.targets = target

    def validate(self, field, target):
        if field not in BASIC_HEADERS:
            print(field + ": invalid field for given plan.")
            raise ValueError
        if type(target) != list:
            print(target + ": containment collection must be a list.")
            raise ValueError

    def operation(self):
        return "filter"

    def __str__(self):
        return "ContainmentPlan: {} in {}".format(self.field, self.targets)

    def execute(self):
        return lambda s: s[self.field_index] in self.targets

    def compile(self, prev_fields):
        expr = (self.operation() + '(lambda ('
                + ','.join(str(x) for x in prev_fields)
                + '): ' + self.field + ' in ' + str(self.targets) + ')')
        return expr


class RangePlan(AggregationPlan):
    """
    Plan for general range based filtering (min and max are inclusive).
    Usage:
        plan = RangePlan("ts", (1440288784003, 1440288785333))
        stream_rdd.filter(plan.execute())
    """

    def __init__(self, field, target):
        self.field = field
        self.validate(field, target)
        self.field_index = BASIC_HEADERS.index(field)
        self.min = target[0]
        self.max = target[1]

    def validate(self, field, target):
        if field not in ["ts", "te", "sPort", "dPort", "nBytes"]:
            print(field + ": invalid field for given plan.")
            raise ValueError
        if len(target) != 2:
            print("Range plan target must be tuple specifying range [min, max].")
            raise ValueError
        if type(target[0]) != int or type(target[1]) != int:
            print("Range values must be integers.")
            raise ValueError

    def operation(self):
        return "filter"

    def __str__(self):
        return "RangePlan: {} <= {} <= {}".format(self.min, self.field, self.max)

    def execute(self):
        return lambda s: self.min <= int(s[self.field_index]) <= self.max

    def compile(self, prev_fields):
        expr = (self.operation() + '(lambda ('
                + ','.join(str(x) for x in prev_fields)
                + '): ' + str(self.min) + ' <= ' + self.field + ' <= ' + str(self.max) + ')')
        return expr


def print_plan_examples():
    # Sample data
    sample1 = ('1440288779703', '1440288783993', '124.122.214.202', '80', '2.25.18.83',
              '51276', '3036', '6', '31c89ff3858be410c061b0e2af198ab1', 'a4fe58752fb497105de64c7cf8071a17')
    sample2 = ('1440288783993','1440288783993','12.194.37.126','49397','52.227.17.169',
               '110','70','6','a8960ddaf645627de5f6c8ed115484c9','e39470a8b3f18469c5b269990e24c37f')
    samples = [sample1, sample2]

    # Original sample data
    print("Original Data: ")
    for sample in samples:
        print sample
    print

    # Example prefix modification plan
    prefix_plan = PrefixPlan("sIP", 24)
    print(prefix_plan)
    print(prefix_plan.compile(BASIC_HEADERS_TUPLE))
    print(map(prefix_plan.execute(), samples))
    print

    # Example containment plan using protocols
    d_macs = ['e39470a8b3f18469c5b269990e24c37f']
    containment_plan = ContainmentPlan("dMac", d_macs)
    print(containment_plan)
    print(containment_plan.compile(BASIC_HEADERS_TUPLE))
    print(filter(containment_plan.execute(), samples))
    print

    # Example range plan
    range_plan = RangePlan("nBytes", (50, 100))
    print(range_plan)
    print(range_plan.compile(BASIC_HEADERS_TUPLE))
    print(filter(range_plan.execute(), samples))
    print

if __name__ == "__main__":
    print_plan_examples()
    # sc = SparkContext("local", "Query Optimization")




