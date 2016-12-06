## Testing the Data Plane Setup

The relevant files for testing the P4-based data plane setup are `fabric_manager/fabric_manager_test.py`, `query_engine/p4_queries.py`, and `examples/distinct_and_reduce/run_switch.sh`

1. In your local VM, run:
```shell
cd ~/dev
python fabric_manager/fabric_manager_test.py
```
This will create a high level query (see: https://github.com/Sonata-Princeton/SONATA-DEV/blob/master/fabric_manager/fabric_manager_test.py#L114), compile it to a low level p4 source code (`examples/distinct_and_reduce/p4src/test.p4`) and set of initial commands ((`examples/distinct_and_reduce/commands.txt`)

2. Start the Mininet env:
```shell
cd ~/dev/examples/distinct_and_reduce
sudo ./cleanup.sh && sudo ./run_switch.sh
```

3. Start the `Scapy`-based receiver:
```shell
cd ~/dev/examples/distinct_and_reduce
sudo python receive.py
```

4. Start the sender:
```shell
cd ~/dev/examples/distinct_and_reduce
sudo python send.py
```
