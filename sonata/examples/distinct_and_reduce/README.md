# Distinct & Reduce

## Description
Query:
```scala
victimIPs =
  pktStream
    .filter(p => p.proto == 17)
    .map(p => (p.dIP, p.sIP))
    .distinct
    .map((dIP, sIP) => (dIP, 1))
    .reduceByKey ( sum )
    .filter((dIP, count) => count >T1)
    ----------------------------------
    .map((dIP,count)=>(dIP/16, count))
    .filter((dIP, count) => count >T2)
    .map((dIP,count)=>dIP)
```
Topology:
```
   +--------------------------------------------------------+
   |                         Mininet                        |
   |                +----------------------+                |
   |                |                      |                |
   |                |                      |                |
   |                |    +------------+    |                |
   |                |    |            |    |                |
   | m-veth-1+----------+11    S1   12+-----------+m-veth-2 |
   |     +          |    |            |    |          +     |
   |     |          |    +------------+    |          |     |
   |     |          |                      |          |     |
   |     |          |                      |          |     |
   |     | ip link  +----------------------+  ip link |     |
   |     |                                            |     |
   |     |                                            |     |
   |     |                                            |     |
   |     +                                            +     |
   | out-veth-1                                  out-veth-2 |
   |     +                                            +     |
   |     |                                            |     |
   |     |                                            |     |
   |     +                                            +     |
   |  send.py            Vagrant VM              receive.py |
   |                                                        |
   +--------------------------------------------------------+
```

Instructions:
To run the demo:
- Start the receiver which is source for streaming platform and sink for data plane traffic: `sudo python receive.py`
- Start the stream processor: `spark-submit --master local[4] streaming_manager.py`
- Start the switch and configure the tables and the mirroring session: `sudo
  ./run_switch.sh`
- Send packets with `sudo python send.py`.
- For cleanup run these two commands: `ps -ef | grep streaming |  grep -v grep | awk '{print $2}' | xargs kill -9` & `sudo ./cleanup.sh`


