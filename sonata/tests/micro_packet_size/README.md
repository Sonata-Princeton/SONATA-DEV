# Macro-Benchmarking

## Running the experiment

1. SSH into the vagrant vm or machine
```bash
$ cd ~/dev
```

2. Running the setup. Following command cleans up the results directory for macro-benchmarking.
Cleans up any previously running processes and kicks off the test app.

```bash
$ rm -rf sonata/tests/macro_bench/results  && sudo sh cleanup.sh && sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD $SPARK_HOME/bin/spark-submit sonata/tests/macro_bench/test_app.py
```

3. Send Traffic

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

![MacroBenchmarking](https://github.com/Sonata-Princeton/SONATA-DEV/blob/master/sonata/tests/macro_bench/graph/macro_n_packets.png)