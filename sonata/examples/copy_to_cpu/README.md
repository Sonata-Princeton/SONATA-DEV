# Copy to CPU

## Description

This program illustrates as simply as possible how to *send packets to CPU*
(e.g. to a controller).

The P4 program does the following:
- incoming packets are mirrored to the CPU port using the
  `clone_ingress_pkt_to_egress` action primitive
- packets mirrored to CPU are encapsulated with a custom `cpu_header` which
  includes 2 fields: `device` (1 byte, set to `0`) and `reason` (one byte, set
  to `0xab`)
- the original packet is dropped in the egress pipeline

Take a look at the [P4 code] (p4src/copy_to_cpu.p4). The program is very short
and should be easy to understand.  You will notice that we use a mirror session
id of `250` in the program. This number is not relevant in itself, but needs to
be consistent between the P4 program and the runtime application.

### Running the demo

We provide a small demo to let you test the program. It consists of the
following scripts:
- [run_switch.sh] (run_switch.sh): compile the P4 program and starts the switch,
  also configures the data plane by running the CLI [commands] (commands.txt)
- [receive.py] (receive.py): sniff packets on port 3 (veth7) and print a hexdump
  of them
- [send_one.py] (send_one.py): send one simple IPv4 packet on port 0 (veth1)

If you take a look at [commands.txt] (commands.txt), you'll notice the following
command: `mirroring_add 250 3`. This means that all the cloned packets with
mirror id `250` will be sent to port `3`, which is our de facto *CPU port*. This
is the reason why [receive.py] (receive.py) listens for incoming packets on port
`3`.

To run the demo:
- start the switch and configure the tables and the mirroring session: `sudo
  ./run_switch.sh`
- start the CPU port listener: `sudo python receive.py`
- send packets with `sudo python send_one.py`. Every time you send one packet,
  it should be displayed by the listener, encapsulated with our CPU header.

This is a very simple example obviously. Feel free to build upon it. For
example, instead of dropping the original packet, you could try to broadcast it
out of every non-ingress port to have a working L2 switch. You could also build
a L2 controller which receives CPU packets and modifies tables appropriately.
