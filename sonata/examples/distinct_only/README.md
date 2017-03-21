# Distinct Only

## Description
Query:
```scala
victimIPs =
  pktStream
    .filter(p => p.proto == 17)
    .map(p => (p.dIP, p.sIP))
    .distinct
    ---------------------------
    .map((dIP, sIP) => (dIP, 1))
    .reduceByKey ( sum )
    .filter((dIP, count) => count >T)
    .map((dIP,count)=>dIP)
```

Instructions:
To run the demo:
- Start the receiver which is source for streaming platform and sink for data plane traffic: `sudo python receive.py`
- Start the stream processor: `spark-submit --master local[4] streaming_manager.py`
- Start the switch and configure the tables and the mirroring session: `sudo
  ./run_switch.sh`
- Send packets with `sudo python send.py`.
- For cleanup run these two commands: `ps -ef | grep streaming |  grep -v grep | awk '{print $2}' | xargs kill -9` & `sudo ./cleanup.sh`
