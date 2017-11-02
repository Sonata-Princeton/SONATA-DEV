## Compiling Dataflow Queries for PISA Targets

Let us consider the query:
```python
# Threshold
Th = 10
Q = (PacketStream(qid=1)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', Th))
     )
```
This query operates over packet fields, `tcp.flags` and `ipv4.dstIP`.

As we discussed 
[earlier](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorial/introduction.md#overview),
Sonata partitions each query into a portion that runs on the switch (i.e., in data 
plane) and another that runs on the streaming analytics platform (i.e., in 
user-space). We will now consider four different plans for partitioning 
this query. For each plan, we will write the P4 code to process the
packet stream in the data plane itself and analyse the number of tuples
sent to the streaming platform for further processing. 

### Plan 1: Execute all dataflow operators in user-space
We will first consider the partitioning plan where all the dataflow operators 
are executed in user space. Thus, the portion of the query that needs to be 
executed in the data plane is shown below:
```python
Q = PacketStream(qid)
```

`PacketStream(qid)` represents stream of packet tuples with all fields 
required for the query with `qid=1`. For the example above, the query
requires processing packet fields `tcp.flags` and `ipv4.dstIP`. Thus,
if the partitioning plan is to execute all the dataflow operators in 
the user-space, then the packet processing pipeline in the data plane
must extract the fields: `tcp.flags` and `ipv4.dstIP` from each incoming
packet, clone each packet, and add a query-specific header with these
fields to the cloned packet. Note that cloning of the original packet
is required such that the default forwarding behavior of the switch
is unaffected by the telemetry queries.  

For this plan we have provided P4 code (`plan1.p4`) that:
* Extracts fields `tcp.flags` and `ipv4.dstIP` from the packet.
* Clones the original packet and adds a new header with fields: 
`qid`, `tcp.flags` and `ipv4.dstIP` to the packet.

##### Question 1: Why do you think the field `qid` is added to the out header?
Hint: see how packets are parsed by `receive.py`

#### Configuring the Match-Action Pipeline
We will describe how `plan1.p4` executes these operations in the data plane.

* It first specifies the format of `out_header_t` headers; `out_header` is 
an instance of header type `out_header_t`.  

```
header_type out_header_t {
	fields {
		qid : 16;
		tcp_flags: 8;
		ipv4_dstIP : 32;
	}
}
header out_header_t out_header;
```


* It also needs to define how packet headers are parsed.
Here, as we add the `out_header` at the top, thus the parser state function 
needs to extract it before parsing the ethernet header. The parser also needs 
to extract the `tcp.flags` and `ipv4.dstIP` fields from the packet (not shown 
here).

```
parser start {
	return select(current(0, 64)) {
		0 : parse_out_header;
		default: parse_ethernet;
	}
}

parser parse_out_header {
	extract(out_header);
	return parse_ethernet;
}
```

* The P4 program needs to specify the order in which different tables should 
be applied. Here, the table `report_packet` is applied to each packet on 
ingress to clone the packet. In the egress pipeline, table `add_out_header` 
adds an `out_header` only to the cloned packets. The metadata field 
`standard_metadata.instance_type` is used to differentiate between the 
original and the cloned packets in the egress pipeline.

```
control ingress {
	apply(report_packet);
}

control egress {
	if (standard_metadata.instance_type == 0) {
		// original packet, apply forwarding
	}

	else if (standard_metadata.instance_type == 1) {
	    apply(add_out_header);
	}
}
```

* Every incoming packet is cloned using the `clone_ingress_pkt_to_egress` 
primitive.

```
field_list report_packet_fields {
    standard_metadata;
}

action do_report_packet(){
	clone_ingress_pkt_to_egress(8001, report_packet_fields);
}

table report_packet {
	actions {
		do_report_packet;
	}
	size : 1;
}
```

* After cloning, the `out_header` is added to the packet and the fields are 
updated using the `modify_field` primitive.

```
action do_add_out_header(){
	add_header(out_header);
	modify_field(out_header.qid, 1);
	modify_field(out_header.tcp_flags, tcp.flags);
	modify_field(out_header.ipv4_dstIP, ipv4.dstIP);
}

```

* A P4 program only specifies the match-action pipeline for a PISA target. 
Separately, the programmer must specify actual values to match on and specific 
actions to take using a target-specific command line interface (CLI) or other 
interface. For this program, we need to send commands to configure the default 
behavior of each table and to specify the mirroring port. The file 
`commands.txt` contains the following commands. These commands are sent to 
the switch at initialization.

```
 table_set_default report_packet do_report_packet
 table_set_default add_out_header do_add_out_header
 mirroring_add 8001 12
```

Here, `12` is the port id for the monitoring port as shown in the figure above. 

#### Notes
* For P4 language questions, please refer to the [P4 language specification](https://p4lang.github.io/p4-spec/p4-14/v1.0.4/tex/p4.pdf) for more details.
* The receiver identifies packets for different plans using
  the `qid` field. Make sure you set the qid as instructed for
  each plan.

#### Testing the Configured Pipeline
After configuring the match-action pipeline to clone every packet and 
send it over a monitoring port, we will now test this program.

For this part, we use the topology shown below:
```
   +--------------------------------------------------------+
   |                                                        |
   |                     +------------+                     |
   |                     |            |                     |
   | m-veth-1+----------+11    S1   12+-----------+m-veth-2 |
   |     +               |            |               +     |
   |     |               +------------+               |     |
   |     |                   Switch                   |     |
   |     |                                            |     |
   |     | ip link                            ip link |     |
   |     |                                            |     |
   |     |                                            |     |
   |     |                                            |     |
   |     +                                            +     |
   | out-veth-1                                  out-veth-2 |
   |     +                                            +     |
   |     |                                            |     |
   |     |                                            |     |
   |     +                                            +     |
   |  send.py            Vagrant VM                Receiver |
   |                                                        |
   +--------------------------------------------------------+
```


Open three terminals

##### Terminal 1: Start Software Switch

SSH into the vagrant vm (`vagrant ssh`)
```bash
$ cd ~/dev/sonata/tutorial
```

Compile the P4 program to `plan.json`
```bash
$ source scripts/env.sh
$ $P4C_BM_SCRIPT Part-1/plan1/plan1.p4 --json Part-1/plan1/plan.json
```

You should see the following messages after compiling the P4 program:
```
parsing successful
semantic checking successful
Header type standard_metadata_t not byte-aligned, adding padding
Generating json output to /home/vagrant/dev/sonata/tutorial/Part-1/plan1/plan.json
```

Always make sure that the compilation  message shows `parsing` and 
`semantic checking` successful. 

Start the switch
```bash
$ sudo sh scripts/run_switch.sh Part-1/plan1
```

##### Terminal 2: Receiver
Start the receiver script
```bash
$ cd ~/dev
$ sudo python sonata/tutorial/Part-1/receive.py
```

##### Terminal 3: Sender
Start the sender script
```bash
$ cd ~/dev
$ sudo python sonata/tutorial/Part-1/send.py
```

##### Question 2: How many tuples (lines) were reported from the data plane?
You can find the resulting output tuples in `~/dev/sonata/tutorial/Part-1/receiver.log` file.

##### Cleanup
Run the following command to clean up any stored results and any previously running processes.
```bash
$ cd ~/dev
$ sudo sh cleanup.sh
```


### Plan 2: Execute Filter operator in the data plane
We will now consider a query partitioning plan where `filter` operators are now executed in the
the data plane itself.  Rather than reporting all of the packet tuples from the network, the switch
now needs only to report packet tuples that satisfy the filter predicate below.
```python
# Threshold
Q = (PacketStream(qid=2)
    .filter(filter_keys=('tcp.flags',), func=('eq', 2)))
```
#### Filter Operator => P4 Table
Filter operators are quite simple, stateless operators. Filter operators
apply a predicate to a tuple and return only those tuples that satisfy
the predicate.  We can implement this operator in the data plane as a match-action table in P4.
The predicate becomes the match condition, and the action yields or suppresses the tuple
for further processing in the dataflow query.  In a P4 program, one can `drop` a packet to suppress further
processing or `nop` to yield the tuple to the next table in the pipeline.

#### Configuring the Match-Action Pipeline
Use the following guidelines to update the P4 code in `plan2.p4` file for this query.
* Only the fields, `qid` and `ipv4.dstIP` should be added to the `out_header`. Set the `qid` in `out_header` to `2`. Can you
reason why there is no need to report the field `tcp.flags` now?
* Add a metadata `meta_app_data` with field `yield`. The packet is cloned only when this field is set to one.
* Add a table to check whether the packet's `TCP SYN` flag is set to one, i.e. `tcp.flags==2`.
Make sure the packets with `tcp.flags!=2` are not dropped.
* Update the ingress pipeline to make sure that only packets with `yield` field set to one are cloned.
* Update the `commands.txt` to specify the default action for the new filter table.
Also, add a command to specify the action when  `tcp.flags==2`.

#### Testing the Configured Pipeline
Follow the same steps from plan 1 (replacing references to `plan1` with `plan2`) to test the configured match-action pipeline.

##### Question 3: How many tuples were reported this time?  Why (or not) are the results different?
If you did not run `cleanup.sh` after completing `plan1`, your log may contain too many entries.

### Plan 3: Execute Reduce operator in the data plane
We will consider a query partitioning plan where `reduce` operators are also executed
in the the data plane.

```python
Q = (PacketStream(qid=3)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     )
```

#### Reduce Operator => P4 Register and Table
Reduce operators are more complicated to implement in a P4 program.  P4 supports
stateful operations across packets through the register primitive.  Each register is
a hash table with configurable width and height (`instance_count`). To support a reduce
operation in the data plane, we can compute an index into the hash table, store the value
as metadata, perform the function applied, and then update the hash table with the result.
These actions can be performed in a match-action table.

Since reduce operators return aggregated values, this aggregation must occur with respect to time.
Sonata reports aggregated results with respect to a time window (`W`).  At the end of a window, `receiver.py`
must retrieve the aggregated values from the registers in the data plane.  For each window, only one packet
per index need be reported to `receiver.py` in order for it to retrieve all of the aggregated values at the end of
the window.

#### Configuring the Match-Action Pipeline
Use the following guidelines to update the P4 code in `plan3.p4` file for this query.
* Create an `out_header` with fields: `qid`, `ipv4.dstIP`, `index`. Set the `qid` in `out_header` to `3`.
* Add a metadata `meta_app_data` for the query with field `yield`. Add another metadata `meta_reduce` specific to
 the reduce operator with fields: `value` (32 bits) and `index` (16 bits).
* Add a register for the `reduce` operation. Configure its `width`
(same as the value field) and `instance_count` (=65,536) attributes.
* Add a `field_list` and define the `field_list_calculation` function to compute the
register index for the reduce operation.
* Add a table that:
  * Computes the register index and stores in `meta_reduce.index` field,
  * Reads the register value for this index into `meta_reduce.value` field,
  * Increments the `meta_reduce.value` field value by one, and
  * Writes the updated value back to the register.
* Update the ingress pipeline to:
    * Apply the `filter` operator over each packet,
    * Apply the `reduce` operator for only packets with `tcp.flags==2`, and
    * Clone only the first packet for each destination IP address.
* Update the `commands.txt` to add commands specifying the default action for the new tables.

#### Testing the Configured Pipeline
Follow the same steps from plan 1 (replacing references to `plan1` with `plan3`) to test the configured match-action pipeline.


##### Question 4: How many tuples were reported this time?  Why (or not) are the results different?
If you did not run `cleanup.sh` after completing `plan2`, your log may contain too many entries.

##### Question 5: How would you implement a `distinct` operator in the data plane?
Hint: Distinct is a special case of a reduce operator.


### Plan 4: Execute all dataflow operators in the data plane
We now consider a query partitioning plan where all the dataflow operators for this query
are executed in the the data plane.
```python
Q = (PacketStream(qid=4)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', Th))
     )
```

#### Filtering on a Threshold => P4 Control Flow
In `P4 14`, conditional logic may only be expressed in the control flow between tables.  Therefore, we must evaluate
filter predicates with a threshold in the control flow.  As an implementation decision, we choose to report a packet only
once in a time window: on the first packet that meets or exceeds a given threshold.  `receiver.py` will retrieve updated 
values at the end of the time window.

#### Configuring the Match-Action Pipeline
Use the following guidelines to update the P4 code in `plan4.p4` file for this query. Compared
to `plan3.p4`, the only change required is:
* Set the `qid` in `out_header` to `4`
* Update the ingress pipeline such that only packets with `meta_reduce.value==Th` are cloned.

#### Testing the Configured Pipeline
Follow the same steps from plan 1 (replacing references to 
`plan1` with `plan4`) to test the configured match-action pipeline.

##### Question 6: How many tuples were reported this time?  Why (or not) are the results different?
If you did not run `cleanup.sh` after completing `plan3`, your log may contain too many entries.