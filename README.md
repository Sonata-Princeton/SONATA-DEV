# End-2-end Testing with payload-based query


#Basics

* Clone the ```Sonata``` repository from Github:
```bash 
$ git clone https://github.com/Sonata-Princeton/SONATA-DEV.git
```

* Change the directory to ```Sonata```:
```bash
$ cd SONATA-DEV
```

* Now run the vagrant up command. This will read the Vagrantfile from the current directory and provision the VM accordingly:
```bash
$ vagrant up
```

The provisioning scripts will install all the required software (and their dependencies) to run the `Sonata` demo. Now ssh in to the VM:
```bash
$ vagrant ssh
```

### End-2-end Testing

* Express the queries for the test application (TODO: create a test directory for all test applications):
```bash
$ cd dev
$ 
```


* Inside the VM, run the cleanup script:
```bash
$ cd ~/dev
$ sudo sh cleanup.sh
```

* Set up `SPARK_HOME`:
```bash
$ export SPARK_HOME=/home/vagrant/spark/
```

* Start the runtime:
```bash
$ sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD $SPARK_HOME/bin/spark-submit runtime/test_app.py
```

This will start the runtime.
On start, runtime will determine the query partitioning & iterative refinement plan.
It will also start, (1) data plane driver, (2) packet parser, and (3) streaming driver.
It will use the final learned plan to generate partitioned queries and then pushes these
queries to respective drivers. 
Data plane driver will receive data processing pipelines from runtime. It then
compiles them into `.p4` source code and pushes it down to create a pipeline of tables
and registers in the data plane.
Similarly, streaming driver receives data processing pipeline from the runtime, and
it translates into `DStream` objects to run over `SPARK` cluster.



* Send the data to the data plane switch (TODO: make this test specific):
```bash
$ sudo python runtime/send.py
```
