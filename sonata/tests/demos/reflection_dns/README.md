# Reflection DNS Attack

## Running the experiment

1. SSH into the vagrant vm or machine
```bash
$ cd ~/dev
```

2. Running the setup. Following command cleans up the results directory for macro-benchmarking.
Cleans up any previously running processes and kicks off the test app.

```bash
$ sudo sh cleanup.sh && sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD $SPARK_HOME/bin/spark-submit sonata/tests/demos/reflection_dns/test_app.py
```
You can modify the queries by editting the file: `sonata/tests/demos/reflection_dns/test_app.py`

3. Send Traffic

```bash
$ sudo python sonata/tests/demos/reflection_dns/send.py
```

## Visualization
To visualuze the traffic at the input and the span port, run
```bash
$ python sonata/tests/demos/reflection_dns/graph/animate_logs.py
```
The experiment runs for 30 seconds, sending attack traffic for 10 seconds starting at t=5 seconds. 
For more details, check out our demo video: https://youtu.be/mXlNMfByp0M
