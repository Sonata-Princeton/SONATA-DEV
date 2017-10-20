## Compiling Dataflow Queries for PISA Targets

Let us consider the query:
```python
# Threshold
Th = 10
# query ID
qid = 1
Q = (PacketStream(qid)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', Th))
     )
```
This query operates over packet fields, `tcp.flags` and `ipv4.dstIP`.

### Part 1: Execute all dataflow operators in user-space
We will first consider the case where all the data flow operators are executed in 
the user space. Thus, the query that needs to be executed in the data plane is shown 
below:
```python
# Threshold
Q = PacketStream(qid)
```

We have provided the P4 code (`part1.p4`) that:
* Extracts Fields `tcp.flags` and `ipv4.dstIP` from the packet.
* Clones the original packet and add a new header with fields: `qid`, `tcp.flags` 
and `ipv4.dstIP`; to the packet.
 
Question: Why do you think the field `qid` is added to the out header? 
Hint: see how packets are parsed by `receive.py`


#### Configuring the Match-Action Pipeline
We will describe how `part1.p4` executes these operations in the data plane. 

* It first specifies the `out_header` added to the cloned packet. 
It also specifies the number of bits required for each field.

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


* It also needs to define how headers are identified within a packet. 
Here, as we add the `out_header` at the top, thus the parser state function needs to 
extracts it before parsing the ethernet header. The parser also needs to extract the
`tcp.flags` and `ipv4.dstIP` fields from the packet (not shown here). 
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

* The P4 program needs to specify the order in which different tables should be applied. 
Here, the table `report_packet` is applied in the ingress to clone the packet and table 
`add_out_header` is applied at the egress to add `out_header` to the cloned packet. 
The metadata field `standard_metadata.instance_type` is used to differentiate between the 
original and the cloned packets at ingress. 
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

* Every incoming packet is cloned using the `clone_ingress_pkt_to_egress` primitive.

```
field_list report_packet_fields {
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

* After cloning, the `out_header` is added to the packet and the fields are updated using 
the `modify_field` primitive.
```
action do_add_out_header(){
	add_header(out_header);
	modify_field(out_header.qid, 1);
	modify_field(out_header.tcp_flags, tcp.flags);
	modify_field(out_header.ipv4_dstIP, ipv4.dstIP);
}

```

* P4 program only configures the match-action pipeline for the PISA target. 
The programmer can configure these pipelines using the target-specific CLI. 
For this program, we need to send commands to configure the default behavior of each table. 
The file `commands.txt` has the following commands. These commands are sent to the
switch at initialization. 
 ```
 table_set_default report_packet do_report_packet
 table_set_default add_final_header do_add_final_header
 mirroring_add 8001 12
 ```

#### Testing the Configured Pipeline
After configuring the match-action pipeline in the data plane to clone every packet and send it
over a span port, we will now test this pipeline. 

For this experiment, we use the topology shown below:
```
   +--------------------------------------------------------+
   |                                                        |
   |                       m-veth-2+--+out-veth-2--+Receiver|
   |                            +                           |
   |                            |                           |
   |                     +------+-----+                     |
   |                     |     12     |                     |
   |                     |            |                     |
   | m-veth-1+----------+11    S1   13+-----------+m-veth-3 |
   |     +               |            |               +     |
   |     |               +------------+               |     |
   |     |                   Switch                   |     |
   |     |                                            |     |
   |     | ip link                            ip link |     |
   |     |                                            |     |
   |     |                                            |     |
   |     |                                            |     |
   |     +                                            +     |
   | out-veth-1                                  out-veth-3 |
   |     +                                            +     |
   |     |                                            |     |
   |     |                                            |     |
   |     +                                            +     |
   |  send.py            Vagrant VM           Original Pkts |
   |                                                        |
   +--------------------------------------------------------+
```

* SSH into the vagrant vm (`vagrant ssh`)
```bash
$ cd ~/dev
```
* Run the following command to clean up any stored results and any previously running processes.
```bash
$ sudo sh cleanup.sh 
```

* Compile the P4 program
```bash
$ $P4C_BM_SCRIPT p4src/part1.p4 --json reduce.json
```

* Start the switch
```bash
$ sudo sh start.sh 
```

* Start the receiver script
```bash
$ python receive.py 1
```

* Start the sender script
```bash
$ python send.py
```

You will see the resulting output tuples in `receiver_1.log` file. Report the number of 
tuples (lines) in this log file.

### Part 2: Execute Filter operator in the data plane
In this part, we will consider query partitioning where `filter` operator is executed in the 
the data plane itself. 
```python
# Threshold
Q = (PacketStream(qid)
    .filter(filter_keys=('tcp.flags',), func=('eq', 2)))
```

#### Configuring the Match-Action Pipeline
Use the following guidelines to update the P4 code in `part2.p4` file for this query.
* Only the fields, `qid` and `ipv4.dstIP` should be added t the `out_header`. Can you 
reason why there is no need to report the field `tcp.flags` now?
* Add a metadata with field `clone`. The packet is cloned only when this field is set to one.
* Add a table to check whether the packet's `TCP SYN` flag is set to one, i.e. `tcp.flags==2`. 
Make sure the packets with `tcp.flags!=2` are not dropped.
* Update the ingress pipeline to make sure that only packets with `clone` field set to one are cloned.
* Update the `commands.txt` to add commands specifying the default action for the new 
filter table.

#### Testing the Configured Pipeline
Follow the same steps as described for part 1 for testing the configured match-action pipeline. 
The only difference is that now `receive.py` will take `2` as the argument and 
the output file's name will be `receiver_1.log`. Report the number of tuples (lines) in this 
log file. 

### Part 3: Execute Reduce operator in the data plane
In this part, we will consider query partitioning where `reduce` operator is also executed 
in the the data plane. 
```python
# Threshold
Th = 10
# query ID
qid = 1

Q = (PacketStream(qid)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     )
```

#### Configuring the Match-Action Pipeline
Use the following guidelines to update the P4 code in `part3.p4` file for this query.
* Create an `out_header` with fields: `qid`, `ipv4.dstIP`, `index`, and `count`. 
Can you reason why we add the `index` field to this header? Hint: see how receiver reports the
final aggregated value for each tuple. 
* Add a metadata with fields:  `clone`, `index`, and `count`. 
* Add a register for the `reduce` operation. Configure its `width` and `instance_count` attributes
for this register. 
* Add `field_list` and define the `field_list_calculation` function to compute the 
register index for the reduce operation. 
* Add a table that: 
  * Computes the register index and stores in `meta.index` field, 
  * Reads the register value for this index into `meta.value` field, 
  * Increments the `meta.value` field value by one, and 
  * Writes the updated value back to the register. 
* Update the ingress pipeline such that: 
    * Applies the `filter` operator over each packet, 
    * Applies the `reduce` operator for only packets with `tcp.flags==2`, and 
    * Clones only the first packet for each destination IP address.
* Update the `commands.txt` to add commands specifying the default action for the new tables.

How different will be the code executing `distinct` operator in the data plane?

#### Testing the Configured Pipeline
Follow the same steps as described for the part 1 for testing the configured match-action pipeline. 
The only difference is that now `receive.py` will take `3` as the argument and 
the output file's name will be `receiver_3.log`. Report the number of tuples (lines) in this 
log file. 

### Part 4: Execute all dataflow operators in the data plane
In this part, we will consider query partitioning where all the dataflow operators for this query 
are executed in the the data plane. 
```python
# Threshold
Th = 10
# query ID
qid = 1

Q = (PacketStream(qid)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', Th))
     )
```

#### Configuring the Match-Action Pipeline
Use the following guidelines to update the P4 code in `part4.p4` file for this query. Compared
to `part3.p4`, the only change required is: 
* Update the ingress pipeline such that only packets with `meta.count==Th` are cloned. 

#### Testing the Configured Pipeline
Follow the same steps as described for part 1 for testing the configured match-action pipeline. 
The only difference is that now `receive.py` will take `4` as the argument and 
the output file's name will be `receiver_4.log`. Report the number of tuples (lines) in this 
log file. 

Notes:
* Please refer to the [P4 language specification](https://p4lang.github.io/p4-spec/p4-14/v1.0.4/tex/p4.pdf) for more details on the P4 language itself.
* Please refer to the [fields_mapping](https://github.com/Sonata-Princeton/SONATA-DEV/blob/ma´ster/sonata/fields_mapping.json) file to understand how the field names for the sonata queries map to target-specific field names.
* ...
