# Expressing Queries for Telemetry Applications 

In this part, we will learn how to express and test queries that detect:
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
representation for `tcp.flags` field for SYN packets is `00000010`(ie, its
decimal value is `2`). After filtering the `SYN` packets, operator can count 
the number of new connections for each host by using the two dataflow 
operators: `map` and `reduce`. `Map` operator selects the field `ipv4.dstIP` 
as the key and sets the value for each key as one. `Reduce` operator sums the 
value of all packets with the same key. After counting the number of newly 
opened TCP connections for each host, operator can apply the `Filter` operator 
to only report the hosts for which the count exceeds the threshold `Th`. Finally, 
it reports the hosts that satisfy this query. 

```python
Q = (PacketStream(qid)
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
As we described [earlier](), Sonata's core hast two major components:
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
* `config["final_plan"] = [(1,32,1)]`,
* `config["final_plan"] = [(1,32,4)]`, and
* `config["final_plan"] = [(1,24,4), (1,32,4)]`

For each plan, we will see the: 
* Generated P4 and Spark code, 
* Number of tuples reported to the stream processor
* Hosts that satisfy the query

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
 
* Set the environment variable `SPARK_HOME`:
```bash
$ export SPARK_HOME=/home/vagrant/spark/
```

* Now start Sonata: 
```bash
$ sudo $SPARK_HOME/bin/spark-submit sonata/examples/newly_opened_connections/test_app.py
```

Note that the file 
`sonata/examples/newly_opened_connections/test_app.py` loads query
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
* Once the Sonata is ready, i.e. you see the `System Ready` message on
`Terminal 1`, send traffic:
```bash
$ sudo python sonata/examples/newly_opened_connections/send.py
```

* You can check the tuples reported to the stream processor and
the final output here:
      * `sonata/examples/newly_opened_connections/logs/emitter.log`
      * `sonata/examples/newly_opened_connections/logs/final_output`

* Finally, run the following command for clean up.
```bash
$ cd ~/dev
$ sudo sh cleanup.sh
```
Note: Make sure you run the cleanup script before restarting Sonata.

#### Questions:
##### Question 1: 
For each plan, report the number of tuples (i.e., number of lines) from 
the `emitter.log` file.
##### Question 2: 
For each plan, report the host(s) that satisfies the query.

## Detecting DNS Traffic Asymmetry

## Query

## Query Plan

## Testing

#### Questions:
##### Question 1: 
For each plan, report the number of tuples (i.e., number of lines) from 
the `emitter.log` file.
##### Question 2: 
For each plan, report the host(s) that satisfies the query.


<!-- ### Detecting IoT Devices -->

<!-- #### Background -->
<!-- The DNS fingerprint for IoT devices is different from other  -->
<!-- Internet-connected such as laptops, servers, and mobile devices etc. -->
<!-- Most IoT devices query a limited number of unique domains. For example, -->
<!-- a `Nest` thermostat mostly sends DNS queries for the domain `nest.com`. -->
<!-- To identify IoT devices, one can write queries that count the total -->
<!-- number of DNS responses received and total number of distinct resolved  -->
<!-- IP addresses in the DNS response message for each host. It can report hosts  -->
<!-- that receive more than `Th1` total responses but for which the number of  -->
<!-- unique resolved IP addresses is less than `Th2`. -->

<!-- #### Expressing the Query -->
<!-- We will now describe a simple query one can express with Sonata to detect the presence of -->
<!-- IoT devices.  -->
<!-- * Identify hosts that receive **more** than `Th1` number of DNS responses. -->
<!-- * Identify hosts for which the number of **unique** resolved IP addresses (`dns.an.rdata`) -->
 <!-- is **less** than `Th2`. -->

<!-- #### Testing -->
<!-- To test your query, follow the steps below: -->
<!-- * Do cleanup -->
<!-- ````bash -->
<!-- $ cd ~/dev -->
<!-- $ sudo sh cleanup.sh -->
<!-- ```` -->

<!-- * Load the new application -->
<!-- ````bash -->
<!-- $ cd ~/dev -->
<!-- $ sudo $SPARK_HOME/bin/spark-submit sonata/tutorial/Part-2/sonata_app.py -->
<!-- ```` -->

<!-- * Use a separate terminal to send the traffic -->
<!-- ````bash -->
<!-- $ cd ~/dev	 -->
<!-- $ sudo python sonata/tutorial/Part-2/send.py -->
<!-- ```` -->
 <!--  -->
<!-- Check the log files here: `sonata/tutorial/Part-2/logs`. `emitter.log` records the  -->
<!-- tuple reported to the stream processor and `final_output` records the final output  -->
<!-- of the query. -->

### Troubleshooting
* Before sending the traffic, make sure that Sonata is ready. You'll see 
the message `System Ready`, when it is ready. 
* Make sure you run the cleanup script before you reload Sonata. 
* In case you see a `mysql-connector` not found error, follow the steps below to fix 
this problem:
    * Install the missing package:
    ```bash
    $ sudo -H pip install mysql-connector==2.1.4
    ```
    * Create a `sonata` database:
    ```bash
    $ sudo mysql -e "create database sonata;"
    ```
    * Add a table:
    ```bash
    $ sudo mysql -e "CREATE TABLE indexStore( id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, qid INT(6),  tuple VARCHAR(200), indexLoc INT(6) );"
    ```
    