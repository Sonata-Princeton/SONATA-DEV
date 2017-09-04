# Reflection DNS Attack

## Experiment Setup

Topology:
```
   +--------------------------------------------------------+
   |                                                        |
   |                       m-veth-2+--+out-veth-2--+Emitter |
   |                            +                           |
   |                            |                           |
   |                     +------+-----+                     |
   |                     |     12     |
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
   |  send.py            Vagrant VM              Bit Bucket |
   |                                                        |
   +--------------------------------------------------------+
```

## Running the experiment

1. SSH into the vagrant vm (`vagrant ssh`) or other machine
```bash
$ cd ~/dev
```

2. Run the following command to clean up any stored results and any previously running processes and laucnhes the test app.

```bash
$  sudo sh cleanup.sh && sudo $SPARK_HOME/bin/spark-submit sonata/examples/ssh_brute/test_app.py
```
You can modify the queries by editing the file: `sonata/tests/demos/reflection_dns/test_app.py`

3. In a separate terminal session, send traffic by running the following command.

```bash
$ cd ~/dev	
$ sudo python sonata/examples/ssh_brute/send.py
```

## Visualization
To visualuze the traffic at the input and the span port, run
```bash
$ cd ~/dev
$ python sonata/tests/demos/reflection_dns_new/graph/animate_logs.py
```
The experiment runs for 30 seconds sending attack traffic for 10 seconds starting at t=5 seconds. 
For more details, check out our demo video: https://youtu.be/mXlNMfByp0M
