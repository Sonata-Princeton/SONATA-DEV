# Sonata: Query-Driven Streaming Network Telemetry

## Overview
Managing and securing networks requires collecting and analyzing measurement
data. Current telemetry systems do not make it easy to do so, typically because 
they separate data collection (e.g., packet capture or flow monitoring) from 
analysis, producing either too much data to answer a general question, or too
little data to answer a detailed question. 

<p align="center">
<img width="400" height="200" src="https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/overview.png">
</p>

Sonata is a streaming telemetry system that makes use of programmable data 
plane and scalable stream processor for scalability. It allows operators to 
directly express queries in a high-level declarative language without worrying 
about how and where the queries gets executed. Under the hood, it partitions 
each query into a portion that runs on the switch and another that runs on 
the streaming analytics platform. For each query, the data plane first 
processes the packet before emitting the intermediate result to the stream 
processor. Sonata's runtime then uses the result of each query to refine the 
subsequent packet processing.

## Declarative Query Interface
It allows network operators to apply intuitive dataflow operators over 
arbitrary combinations of packet fields. 

### Packet Fields
You can find the set of supported packet fields for expressing Sonata queries
[here](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/fields_mapping.json). 

### Dataflow Operators

| Operator| Description|
| ---------------------| -----------|
| Map(keys, map_keys, map_values,func)| Transform each tuple with function `func` applied over tuples identified by key(`map_keys`) or value (`map_values`) fields.|
| filter(filter_keys, filter_values,func)| Filter packets that satisfy predicate `func` applied over set of key (`filter_keys`) or value (`filter_vals`) fields|
| reduce(keys,func)| Emit result of function `func` applied on key (`keys`) over the input stream.|
| distinct(keys)| Emit tuples with unique combinations of key (`keys`) fields.|
| join(window, new_qid, query)| Join the output of `query` and assign `new_qid` to the resulting joined query. Also, specify whether the `join` operation is applied over the same window interval or over rolling windows.|



### Example Queries

#### Newly Opened TCP Connections
To detect a large number of newly opened TCP connections,
first applies a `filter` operation over the entire packet stream 
identified by query id `1` to
filter TCP packets with just the `SYN` flag set. It then counts the
number of packets observed for each host and reports the hosts
for which this count exceeds threshold `Th` in an epoch configured 
[here](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/config.json#L42-L44).
```python
n_syn = (PacketStream(qid=1)
         .filter(filter_keys=('tcp.flags',), func=('eq', 2))
         .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
         .reduce(keys=('ipv4.dstIP',), func=('sum',))
         .filter(filter_vals=('count',), func=('geq', Th))
         )
```

Note: `tcp.flags` is a an eight bit field. Binary representation for 
`tcp.flags` field for SYN packets is `00000010`, i.e. its decimal value
 is `2` Similarly, `FIN` packets will have `tcp.flags=1`, `ACK` packets 
 will have `tcp.flags=16` and so on. 

#### Slowloris Attacks
The application to detect a slowloris attack has two sub-queries
with query ids `1` and `2` respectively. One counts the number of unique 
connections by applying a `distinct` followed by a `reduce` operation. 
It only reports hosts for which the number of connections exceeds threshold 
`Th1`. The other counts the total bytes transferred for each host. It then 
joins these sub-queries to compute the average transmission rate per 
connection and reports hosts with an average rate below a threshold `Th2`.
```python
n_conns = (PacketStream(qid=1)
           .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
           .map(keys=('ipv4.dstIP', 'ipv4.srcIP', 'tcp.sport',))
           .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP', 'tcp.sport',))
           .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
           .reduce(keys=('ipv4.dstIP',), func=('sum',))
           .filter(filter_vals=('count',), func=('geq', Th1))
           )

n_bytes = (PacketStream(qid=2)
           .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
           .map(keys=('ipv4.dstIP', 'ipv4.totalLen',))
           .map(keys=('ipv4.dstIP',), map_values=('ipv4.totalLen',))
           .reduce(keys=('ipv4.dstIP',), func=('sum',))
           )

slowloris = (n_conns.join(window='same', new_qid=3, query=n_bytes)
             .map(map_values=('count2',), func=('div',))
             .filter(filter_keys=('count2',), func=('leq', Th2))
             )
```

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

### Core
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

### Drivers
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
 
### Emitter
The emitter consumes raw packets from the data-plane's monitoring port, parses 
the query-specific fields embedded in the packet, and sends the corresponding 
tuples to the stream processor. The emitter uses 
[Scapy](http://www.secdev.org/projects/scapy/) to extract the unique query 
identifier (`qid`) from packets. It uses this identifier determine how to 
parse the remainder of the query-specific fields embedded in the packet based 
on the configuration that the runtime provides for the corresponding `qid`.

For more details, please reach out to 
[Arpit Gupta](mailto:arpitg@cs.princeton.edu) to get a copy of the Sonata paper.
