# TRUNCATE

A maximum of 100 bytes of the cloned packets is sent to the controller.

## Usage

### P4 Fabric

```bash
$ ./run.sh
```

### XTerm

within the mininet CLI enter:

```bash
$ xterm h1 h2 h3
```

### Traffic Sink

in the h2 terminal enter:

```bash
$ ./receive.py
```

### Controller

in the h3 terminal enter:

```bash
$ ./receive.py
```

### Traffic Source

in the h1 terminal enter:

```bash
$ ./send.py
```
