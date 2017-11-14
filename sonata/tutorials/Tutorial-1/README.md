# Expressing Queries for Telemetry Applications

In this tutorial/assignment, we will learn how to express and test 
queries that detect:
* Newly-opened tcp connections. 
* DNS traffic asymmetry. 

## Detecting Newly Opened TCP Connections
Let us consider the case where a network operator may wish to detect hosts
that have too many recently opened TCP connections, as might occur in a 
[SYN flood attack](https://en.wikipedia.org/wiki/SYN_flood) or 
during [flash crowd events](https://www.cs.princeton.edu/~mfreed/docs/flash-imc11.pdf).

### Query
Network operators can use Sonata to express a query that reports hosts for
which the number of newly opened TCP connections (identified by packets with
`SYN` flags) exceed a pre-determined threshold. To detect packets with
`SYN` flags, it applies a `Filter` operator over the incoming packet stream
identified by the `qid` to check whether the TCP flag field has the `SYN` bit 
set to one. As the `tcp.flags` is a an eight bit field. So, the binary 
representation for `tcp.flags` field for SYN packets is `00000010`(i.e., its
decimal value is `2`). After filtering the `SYN` packets, operator can count 
the number of new connections for each host by using the two dataflow 
operators: `Map` and `Reduce`. `Map` operator selects the field `ipv4.dstIP` 
as the key and sets the value for each key as one. `Reduce` operator sums the 
value of all packets with the same key. After counting the number of newly 
opened TCP connections for each host, network operator can apply the `Filter` operator 
to only report the hosts for which the count exceeds the threshold `Th`. Finally, 
it reports the hosts that satisfy this query. 

```python
Q = (PacketStream(qid=1)
     .filter(filter_keys=('tcp.flags',), func=('eq', 2))
     .map(keys=('ipv4.dstIP',), map_values=('count',), func=('set', 1,))
     .reduce(keys=('ipv4.dstIP',), func=('sum',))
     .filter(filter_vals=('count',), func=('geq', Th))
     .map(keys=('ipv4.dstIP',))
     )
```


You can find the query for this application here: 
`sonata/examples/newly_opened_connections/test_app.py`.
 
### Query Plan
As we described 
[earlier](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/sonata/tutorials/introduction.md), Sonata's core hast two major components:
(1) runtime, and (2) query planner. Query planner uses the input queries,
data-plane target's constraints, and historical packet traces to determine
the query plan for refining and partitioning the input queries to minimize
the workload to the stream processor. In this tutorial, rather than learning
the query plan, we will manually specify query plans and see how Sonata's
runtime generates the corresponding data-plane and streaming configurations 
for each specified query plan.

One can manually specify the query plan by editing:
```python
config["final_plan"] = [(qid, r, p), ...]
```
Here, `qid` represents the query's unique identifier; `r` represents the refinement 
level where `r=0` is the coarsest refinement level, and `r=32` is the finest 
refinement level; and `p` represents the number of dataflow operators that Sonata
will execute in the data plane. For example, plan `(1,32,4)` indicates that the
first four dataflow operators for the query with `qid=1` at refinement level `/32` 
will be executed in the data plane. Also, query plan 
`config["final_plan"] = [(1,24,4), (1,32,4)]` indicates that the query with
`qid=1` will perform refinement by running the query at refinement level `/24`
by default and apply the query at refinement level `/32` for the refinement
level `32` for only those portions of the traffic that satisfy the query
at level `/24` in the previous window interval. Also, for both refinement
levels, Sonata will execute the first four operators in the data plane. 

We will test this application for three query plans:
* `config["final_plan"] = [(1,32,1)]`, i.e., only first dataflow operator 
(`Filter`) is executed in the data plane.
* `config["final_plan"] = [(1,32,4)]`, i.e., first four dataflow operators are 
executed in the data plane. 
* `config["final_plan"] = [(1,24,4), (1,32,4)]`, i.e., the query is first
executed at refinement level `/24` and the query at refinement level `/32`
is only applied over traffic that satisfies the query at level `/24` in the
previous window interval. 

### Testing
For testing this query, open two terminals:

#### Terminal 1: Start Sonata
* SSH into the vagrant VM :
```bash
$ vagrant ssh
```
* Change the directory:
```bash
$ cd ~/dev
```

* Edit the `config["final_plan"]` in 
`sonata/examples/newly_opened_connections/test_app.py` to manually select
 the query plan.
 
 Note: All paths unless specified otherwise are relative to the `~/dev` 
 directory. 
 
* Set the environment variable `SPARK_HOME`:
```bash
$ export SPARK_HOME=/home/vagrant/spark/
```

* Now start Sonata: 
```bash
$ sudo $SPARK_HOME/bin/spark-submit sonata/examples/newly_opened_connections/test_app.py
```

Note that the file 
`sonata/examples/newly_opened_connections/test_app.py` loads the query
for the newly-opened tcp connection application to the runtime. 
The runtime then uses the configured query plan to partition and refine 
the input query and send the partitioned queries to respective target 
drivers. For this assignment, 
we use [P4-BMV2 behavioral switch](https://github.com/p4lang/behavioral-model) 
as the data plane target and 
[Apache Spark Streaming](https://spark.apache.org/streaming/) 
as the streaming target. 

* You can check out the generated `P4` and `Spark` code here:
    * `sonata/examples/newly_opened_connections/generated_src/compiled.p4`
    * `sonata/examples/newly_opened_connections/generated_src/spark.py`

#### Terminal 2: Send Traffic
* SSH into the vagrant VM :
```bash
$ vagrant ssh
```
* Change the directory:
```bash
$ cd ~/dev
```
* Once the Sonata is ready, i.e., you see the `System Ready` message on
`Terminal 1`, send traffic:
```bash
$ sudo python sonata/examples/newly_opened_connections/send.py
```

* You can check the tuples reported to the stream processor and
the final output here:
  * `sonata/examples/newly_opened_connections/logs/emitter.log` 
  * `sonata/examples/newly_opened_connections/logs/final_output`
  
You will see some magic numbers like `10032` or `10024` etc. on the
terminal as well as the `emitter.log` files. These numbers are
generated by the `runtime` to identify queries after refinement.
For example, `10032` identifies query with `qid=1` at refinement
level `/32`.

* Finally, run the following command for clean up.
```bash
$ cd ~/dev
$ sudo sh cleanup.sh
```
Note: Make sure you run the cleanup script before restarting Sonata.

#### Questions:
##### Question 1: 
For each plan, report the number of tuples (i.e., number of lines) from 
the `emitter.log` file. Which plan reports least number of tuples to
the stream processor? Why does changing the query plan affects 
the number of lines in the `emitter.log` file?

##### Question 2: 
For each plan, report the host(s) that satisfies the query. Do different
plans identify the same victim host(s)? Why does changing the query plan 
not affect the host(s) that satisfies the query? 

#### Question 3:
For each plan, check the generated P4 code at
`sonata/examples/newly_opened_connections/generated_src/compiled.p4`,
and report the fields for the header, `out_header_10032`.
Note that `out_header_10032` is the one added to the cloned packet 
sent to the emitter via the monitoring port for query with `qid=1` at 
refinement level `/32`. Why does changing the query plan affects the 
`out_header_10032` fields?

## Detecting DNS Traffic Asymmetry
Let us now consider the case where the operator may wish to detect 
hosts for which the number of DNS responses 
received is significantly greater than the number of DNS requests sent. 
This might occur when the host is a victim of 
[DNS reflection attack](https://blog.cloudflare.com/reflections-on-reflections/).

## Query
Network operators can use Sonata to express two queries:
(1) Counts the number of DNS response messages received per host
(`n_resp` query), and (2) Counts the number of DNS request messages 
sent per host (`n_req` query). Both these queries will first filter
the DNS response and request packets, identified by the fields:
`udp.sport` and `udp.dport` respectively. They will then
use combination of `Map` and `Reduce` operators to count the
number of responses and requests for each host, identified by
the fields `ipv4.dstIP` and `ipv4.srcIP` respectively.

It can then join these two queries, and find the difference between
the number of responses and requests for each host. Finally, it
reports hosts for which this difference exceeds the threshold `Th`.

##### Question 4: 
Use the description above, to write the missing operators for the
`n_resp` and `n_req` queries in
`sonata/tutorials/Tutorial-1/dns_assymetry/test_app.py`.

## Query Plan
For this query, we will use the plan: 
`config["final_plan"] = [(1,32,4), (2,32,4)]`, i.e., we run all the dataflow
operators for the `n_resp` and `n_req` queries in the data plane at refinement
level `/32`. Note that we support the `Join` operation (for `qid=3`) at the 
stream processor. 

## Testing
Follow the same instructions as above to set the environment variables and
do cleanup before running Sonata for this application. 

#### Terminal 1: Start Sonata
After editing the `test_app.py` file, load the application with Sonata: 
```bash
$ sudo $SPARK_HOME/bin/spark-submit sonata/tutorials/Tutorial-1/dns_assymetry/test_app.py
```

#### Terminal 2: Send Traffic
Once Sonata is ready, i.e., you see the `System Ready` message on
`Terminal 1`, send traffic:
```bash
$ sudo python sonata/tutorials/Tutorial-1/dns_assymetry/send.py
```

#### Questions:
##### Question 5: 
Report the number of tuples (i.e., number of lines) from 
the `emitter.log` file.

##### Question 6: 
Report the host(s) that satisfies the query.

### Troubleshooting
* When you start the VM, all required environment variables are set by
default. You can check that by running the `env` command:
```bash
$ env
..
SPARK_HOME=/home/vagrant/spark/
JAVA_HOME=/usr/lib/jvm/java-8-oracle
HOME=/home/vagrant
PYTHONPATH=:/home/vagrant/dev:/home/vagrant/bmv2/mininet
...
```
If you see any `path` related errors while running the code, make sure 
your environment variables are set as shown above. 
* Before sending the traffic, make sure that Sonata is ready. You'll see 
the message `System Ready`, when it is ready. 
* Make sure you run the cleanup script before you reload Sonata.
* Make sure you add `,` at the end of each attribute of the dataflow operators.
For example, attribute `keys` should be defined as `keys=('ipv4.dstIP',)` and
not `keys=('ipv4.dstIP')`. 