#define CPU_MIRROR_SESSION_ID                  250

parser start {
  return select(current(0, 64)) {
      0 : parse_outTuple_header;
      default: parse_ethernet;
  }
}

parser parse_outTuple_header {
    extract(outTuple_header);
    return parse_ethernet;
}

action _drop() {
    drop();
}

action _nop() {
    no_op();
}

table skip1 {
    actions {_nop;}
    size : 1;
}

table skip2 {
    actions {_nop;}
    size : 1;
}

table drop1 {
    actions {_drop;}
    size : 1;
}

table drop2 {
    actions {_drop;}
    size : 1;
}

table drop3 {
    actions {_drop;}
    size : 1;
}

action do_copy_to_cpu() {
    clone_ingress_pkt_to_egress(CPU_MIRROR_SESSION_ID, copy_to_cpu_fields);
}

table copy_to_cpu {
    actions {do_copy_to_cpu;}
    size : 1;
}
