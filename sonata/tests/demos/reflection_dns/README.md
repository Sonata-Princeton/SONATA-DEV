<<<<<<< HEAD
# Macro-Benchmarking
=======
# Reflection DNS Attack
>>>>>>> ed5e51020f2e3bd404976f03db6f65179a98d03e

## Running the experiment

1. SSH into the vagrant vm or machine
```bash
$ cd ~/dev
```

2. Running the setup. Following command cleans up the results directory for macro-benchmarking.
Cleans up any previously running processes and kicks off the test app.

```bash
<<<<<<< HEAD
$ rm -rf sonata/tests/macro_bench/results  && sudo sh cleanup.sh && sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD $SPARK_HOME/bin/spark-submit sonata/tests/macro_bench/test_app.py
```
=======
$ sudo sh cleanup.sh && sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD $SPARK_HOME/bin/spark-submit sonata/tests/demos/reflection_dns/test_app.py
```
You can modify the queries by editting the file: `sonata/tests/demos/reflection_dns/test_app.py`
>>>>>>> ed5e51020f2e3bd404976f03db6f65179a98d03e

3. Send Traffic

```bash
<<<<<<< HEAD
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
=======
$ sudo python sonata/tests/demos/reflection_dns/send.py
```

## Visualization
To visualuze the traffic at the input and the span port, run
```bash
$ python sonata/tests/demos/reflection_dns/graph/animate_logs.py
```
The experiment runs for 30 seconds, sending attack traffic for 10 seconds starting at t=5 seconds. 
For more details, check out our demo video: https://youtu.be/mXlNMfByp0M
>>>>>>> ed5e51020f2e3bd404976f03db6f65179a98d03e
