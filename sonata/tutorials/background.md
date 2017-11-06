# Sonata: Query-Driven Streaming Network Telemetry

## Overview
Network operators routinely perform multiple measurement tasks to discover
various events in the network, such as degraded link performance and
network attacks. Many of these tasks require collecting and analyzing 
network statistics in real time. Current telemetry systems do not make it 
easy to do so, typically because they separate data collection (e.g., 
packet capture or flow monitoring) from analysis, producing either too 
much data to answer a general question, or too little data to answer a 
detailed question. 

<p align="center">
<img width="400" height="300" src="https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/overview.png">
</p>

In contrast, Sonata, a network telemetry system, exposes a query 
interface enabling joint collection and analysis of network traffic. 
It makes use of programmable data plane to reduce the workload
for the stream processor. It also allows operators to directly express 
queries in a high-level declarative language without worrying 
about how and where the queries gets executed. 

Under the hood, it *partitions* each query into a portion that runs on 
the switch and another that runs on the streaming analytics platform. For 
each query, the data plane first processes the packet before emitting the 
intermediate result to the stream processor. Sonata's runtime then uses 
the result of each query to *refine* the subsequent packet processing.

We will now describe the following in greater details:
* [Query Interface](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/background.md#sonatas-query-interface)
* [Query Partitioning](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/background.md#query-partitioning)
* [Dynamic Query Refinement](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/background.md#dynamic-query-refinement)
* [Sonata's Implementation](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/background.md#sonatas-implementation)

## Query Interface
Sonata's query interface allows network operators to express the queries 
for telemetry applications using familiar dataflow operators over 
arbitrary combinations of packet fields without worrying about how
and where the query gets executed.

### Extensible Packet Tuple Abstraction
Packets carry not only information in their header fields and payload, 
but also the meta information about the state of the underlying network, 
such as the time when a packet arrives at a switch or number of hops it 
traversed in the network. Sonata provides an intuitive interface for 
expressing queries over the union of fields extracted either in the data 
plane or in user space. This abstraction is inherently flexible because 
the list of fields in the packet tuples can incorporate new header and meta 
fields as the underlying data plane evolves, for example, reading the sizes 
of queues the packet encountered en route 
(see [INT](http://p4.org/wp-content/uploads/fixed/INT/INT-current-spec.pdf)).


Sonata has an extensible 
[parser](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/sonata_layers.py) 
that unifies the parsing capabilities of the available data-plane and 
streaming targets. The parser extracts from 
the raw packets all fields required to satisfy the set of input queries.
Sonata seeks to perform parsing in the data plane whenever possible
and directs packets to the stream processor for parsing only when 
necessary. In user space, Sonata employs extensible, user-defined 
parsing modules that extract fields for many standard protocols. You 
can find the set of supported packet fields for expressing Sonata queries
[here](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/fields_mapping.json). 

### Dataflow Operators
Network telemetry applications often require computing aggregate 
statistics over a subset of traffic and joining the results from multiple 
queries. Most of these tasks can be expressed using declarative queries 
that compose dataflow operators. Sonata's query interface allows it to 
abstract the details of **where** each query operator runs and **how** the 
underlying targets perform those operations. Sonata's query planner 
decides how and where to execute the input queries allowing Sonata to 
run identical queries over different choices of streaming or data-plane 
targets without modification. This feature ensures that the telemetry 
system is flexible and easy to maintain.

| Operator| Description|
| ---------------------| -----------|
| Map(keys, map_keys, map_values,func)| Transform each tuple with function `func` applied over tuples identified by key(`map_keys`) or value (`map_values`) fields.|
| Filter(filter_keys, filter_vals,func)| Filter packets that satisfy predicate `func` applied over set of key (`filter_keys`) or value (`filter_vals`) fields|
| Reduce(keys,func)| Emit result of function `func` applied on key (`keys`) over the input stream.|
| Distinct(keys)| Emit tuples with unique combinations of key (`keys`) fields.|
| Join(window, new_qid, query)| Join the output of `query` and assign `new_qid` to the resulting joined query. Also, specify whether the `join` operation is applied over the same window interval or over rolling windows.|

Table above describes the operators that Sonata supports over a
stream of packet tuples. Stateless operators such as `Filter` and 
`Map` emit results immediately after operating on an input tuple. 
Stateful operators such as `Reduce`, `Distinct`, and `Join` emit
results at the end of a time window of `W` seconds configured 
[here](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/config.json#L42-L44).

### Expressing Queries for Telemetry Applications
Network operators can express various queries for telemetry applications
using Sonata's query interface. We will describe the query for
one such application here. You can check out the queries for various
other applications 
[here](https://github.com/Sonata-Princeton/SONATA-DEV/tree/tutorial/sonata/examples). 

#### Newly Opened TCP Connections
A network operator may wish to detect hosts that have too many recently 
opened TCP connections, as might occur in a SYN flood. To detect a large 
number of newly opened TCP connections, first applies a `filter` operation 
over the entire packet stream identified by query id `1` to filter TCP 
packets with just the `SYN` flag set. It then counts the number of packets 
observed for each host and reports the hosts for which this count exceeds 
threshold `Th`.

```python
victims = (PacketStream(qid=1)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', Th))
     .map(keys=('ipv4.dstIP',)))
```

Note: `tcp.flags` is a an eight bit field. Binary representation for 
`tcp.flags` field for SYN packets is `00000010`, i.e., its decimal value
 is `2` Similarly, `FIN` packets will have `tcp.flags=1`, `ACK` packets 
 will have `tcp.flags=16` and so on. 

## Query Partitioning
Sonata uses Protocol Independent Switch Architecture (PISA) targets to 
reduce the workload for the stream processor. PISA targets support custom 
parsing and packet-processing pipelines, as well as general-purpose 
registers for stateful operations. These features provide opportunities 
for Sonata to use PISA targets to reduce the data that is ultimately sent 
to the stream processor. Sonata's query planner
takes various target-specific constraints, such as amount of register
memory available for stateful operations etc., before making a query 
partitioning decision. This partitioning decision is based on the 
solution to an integer linear program (ILP) that Sonata solves to 
determine a query plan.

For example, if the query planner decides it can only execute the
`Filter` operation for `Newly Opened TCP Connections` query. Then,
the portion of the query that executes in the data plane will be:
```python
victims = (PacketStream(qid=1)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
```

To execute this portion of the original query in the data plane, 
Sonata will generate a P4 code that performs the following actions:
* Extract the required `tcp.flags` and `ipv4.dstIP` fields from each packet,
* Filter packets with TCP SYN flag set, 
* Clone the filtered packet. Note that cloning is required to ensure that the 
default forwarding is not affected by the telemetry queries.
* Add a header to the cloned packet with fields `ipv4.dstIP` and `qid` 
before sending it out via the monitoring port.

## Dynamic Query Refinement
For certain queries and workloads, partitioning a subset of dataflow 
operators to the data plane does not reduce the workload on the stream 
processor enough. Sonata performs dynamic refinement to further reduce 
the load in these situations. 

To perform refinement, Sonata's runtime needs to identify the
key for refinement, i.e., refinement key. Any field that is hierarchical
and is used as a key in the stateful dataflow operations is a candidate
refinement key. The hierarchical structure allows Sonata to replace a 
more specific key with a coarser version without missing any traffic 
that satisfies the original query. For example, `ipv4.dstIP` has a 
hierarchical structure and is used as a key for aggregation in 
`Newly Opened TCP Connections` Query. As a result, the query planner 
selects the field `ipv4.dstIP` as a refinement key. 

After selecting the refinement key, Sonata's query planner modifies the 
input queries to start at a coarser level of granularity than specified 
in the original query. It then chooses a sequence of finer levels of 
granularity that reduces the load on the stream processor at the cost of 
additional delay in detecting the traffic that satisfies the original 
queries. The specific levels of granularity chosen and the sequence in 
which they are applied constitute a refinement plan. To compute an optimal 
refinement plan for a set of queries, Sonata's query planner estimates the 
cost of executing different refinement plans using historical training data.
It then solves an extended version of the query partitioning ILP that 
determines both partitioning and refinement plans to minimize the traffic 
at the stream processor.

## Sonata's Implementation
For each query, the Sonata's core generates partitioned and refined queries
and sends the partitioned queries to the respective *drivers*. The drivers then 
compile the parts of each query to the appropriate target. When packets arrive 
at a PISA target, it applies the packet-processing pipelines and mirrors the 
appropriate packets to a monitoring port, where a software *emitter* parses the 
packet and sends the corresponding tuples to the stream processor. The stream 
processor reports the results of the queries to the runtime, which then updates 
the data plane, via the data-plane driver, to perform refinement.

<p align="center">
<img width="400" height="300" src="https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/arch.png">
</p>

### [Core](https://github.com/Sonata-Princeton/SONATA-DEV/tree/tutorial/sonata/core)
The core has a query planner and a runtime. When a new switch connects or when 
re-training is required, the runtime interacts with the data-plane driver over 
a network socket to determine which operators it can execute in the data plane 
and the values of the data-plane constraints. It then passes these values to the 
query planner which uses the [Gurobi](http://www.gurobi.com/) ILP solver to solve the query planning ILP 
offline, generating partitioned and refined queries. The runtime sends partitioned 
and refined queries to the drivers over a network socket. It also tells the emitter 
the fields and their sizes to extract from packets for each query, identified by a 
`qid`. After the targets begin processing packets, the runtime receives query 
outputs from the stream processor at the end of every window. It then sends the 
updates to the data-plane drivers, which update table entries according 
to the dynamic refinement plan.

### [Drivers](https://github.com/Sonata-Princeton/SONATA-DEV/tree/tutorial/sonata/dataplane_driver)
Data-plane and streaming drivers compile the queries from the runtime to 
target-specific code. The data-plane drivers also interact with the target 
to execute commands on behalf of the runtime such as updating `filter` 
tables for dynamic refinement at the end of every window. Sonata implementation 
has drivers for two PISA targets: the 
[BMV2 P4 software switch](https://github.com/p4lang/behavioral-model), 
the standard behavioral model for evaluating P4 code; and the 
[Barefoot Tofino switch](https://barefootnetworks.com/products/brief-tofino/), 
a 6.5 Tbps hardware switch. The data-plane driver interacts with the target using
a [Thrift API](https://thrift.apache.org/).

Note: For propriety reasons, we have not made the driver for the Tofino switch 
public. Please reach out to us over [email](mailto:arpitg@cs.princeton.edu) to 
learn more about our driver for the Barefoot's Tofino switch. 
 
### [Emitter](https://github.com/Sonata-Princeton/SONATA-DEV/tree/tutorial/sonata/dataplane_driver/p4/emitter)
The emitter consumes raw packets from the data-plane's monitoring port, parses 
the query-specific fields embedded in the packet, and sends the corresponding 
tuples to the stream processor. The emitter uses 
[Scapy](http://www.secdev.org/projects/scapy/) to extract the unique query 
identifier (`qid`) from packets. It uses this identifier determine how to 
parse the remainder of the query-specific fields embedded in the packet based 
on the configuration that the runtime provides for the corresponding `qid`.

For more details, please reach out to 
[Arpit Gupta](mailto:arpitg@cs.princeton.edu) to get a copy of the Sonata paper.
