# Macro-Benchmarking

## Running the experiment

1. SSH into the vagrant vm or machine
```bash
$ cd ~/dev
```

2. Cleanup Results Directory
```bash
$ rm -rf sonata/tests/macro_bench/results/*
```

3. Start Dataplane Driver
```bash
# Clean up
$ sudo sh cleanup.sh
```
```bash
# Start the driver
$ sudo PYTHONPATH=$PYTHONPATH:$PWD python sonata/dataplane_driver/dp_driver.py
```

4. Start the Application
```bash
sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD $SPARK_HOME/bin/s-submit sonata/tests/macro_bench/test_app.py
```

5. Send Data

```bash
$ sudo python sonata/tests/macro_bench/send.py
```

## Generating Graph

Once the data is generated after running the experiments in `sonata/tests/macro_bench/results`,
we can generate the traffic pattern graph by running following command from the machine.

```bash
$ python sonata/tests/macro_bench/graph/graph.py
```

The graph is generated in folder `sonata/tests/macro_bench/graph/macro_n_packets.eps`

The Graph generated looks like below:

![MacroBenchmarking](https://github.com/Sonata-Princeton/SONATA-DEV/blob/micro/sonata/tests/macro_bench/graph/macro_n_packets.png)