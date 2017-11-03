## Telemetry Applications

Some of the applications in this directory are described below:

|#| Application Name  | Description (Identify) |
| -|------------- | ------------- |
| 1|TCP New Conn | Hosts for which the number of newly opened TCP connections exceeds threshold.|
| 2|SSH Brute     | Hosts that receive similar-sized packets from more than threshold unique senders.|
| 3|SuperSpreader | Hosts that contact more than threshold unique destinations.|
| 4|Port Scan     | Hosts that send traffic over more than threshold destination ports.|
| 5|DDoS          | Hosts that receive traffic from more than threshold unique sources.|
| 6|Syn Flood     | Hosts for which the number of half-open TCP connections exceeds threshold Th. |
| 7|Completed Flow| Hosts for which the number of incomplete TCP connections exceeds threshold.|
| 8|Slowloris Attack | Hosts for which the average transfer rate per flow is below threshold.|
| 9|DNS Tunneling | Hosts for which new TCP connections are not created after DNS query.|
| 10|Zorro Attck | Hosts that receive “zorro” command after telnet brute force.|
| 11|Reflection DNS| Hosts that receive DNS response of type `RRSIG` from many unique senders without requests.|

### Queries
You can find the query for each of these applications in the 
`<app_name>/test_app.py` file. 

### Testing
For testing any of these queries, open two terminals:

#### Setup

For all the queries, we use the topology shown below:
```
   +--------------------------------------------------------+
   |                                                        |
   |                       m-veth-2+--+out-veth-2--+Emitter |
   |                            +                           |
   |                            |                           |
   |                     +------+-----+                     |
   |                     |     12     |                     |
   |                     |            |                     |
   | m-veth-1+----------+11    S1   13+-----------+m-veth-3 |
   |     +               |            |               +     |
   |     |               +------------+               |     |
   |     |               simple_switch                |     |
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
   |  send.py            Vagrant VM          Default Fwding |
   |                                                        |
   +--------------------------------------------------------+
```

#### Terminal 1: Start Sonata
* SSH into the vagrant VM :
```bash
$ vagrant ssh
```
* Change the directory:
```bash
$ cd ~/dev
```
 
* Set the environment variable `SPARK_HOME`:
```bash
$ export SPARK_HOME=/home/vagrant/spark/
```

* Now start Sonata: 
```bash
$ sudo $SPARK_HOME/bin/spark-submit sonata/examples/<app_name>/test_app.py
```

Note that the file 
`sonata/examples/<app_name>/test_app.py` loads query
for the specified application to the runtime. 
The runtime then uses the configured query plan to partition and refine 
the input query and send the partitioned queries to respective target 
drivers. For this setup, 
we use [P4-BMV2 behavioral switch](https://github.com/p4lang/behavioral-model) 
as the data plane target and 
[Apache Spark Streaming](https://spark.apache.org/streaming/) 
as the streaming target. 

* You can check out the generated `P4` and `Spark` code here:
    * `sonata/examples/<app_name>/generated_src/compiled.p4`
    * `sonata/examples/<app_name>/generated_src/spark.py`

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
$ sudo python sonata/examples/<app_name>/send.py
```

Feel free to update the `send.py` to send a different traffic pattern to
validate the queries.

* You can check the tuples reported to the stream processor and
the final output here:
  * `sonata/examples/<app_name>/logs/emitter.log` 
  * `sonata/examples/<app_name>/logs/final_output`

* Finally, run the following command for clean up.
```bash
$ cd ~/dev
$ sudo sh cleanup.sh
```

Notes: 

* Make sure you run the cleanup script before restarting Sonata.
* If you want to contribute, please consider adding a directory here 
for your new queries here and add the `test_app.py` and `send.py`
files as we did for other queries. That way we can quickly test the
new queries before merging them. 
