/*
Copyright 2013-present Barefoot Networks, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

header_type ethernet_t {
    fields {
        dstAddr : 48;
        srcAddr : 48;
        etherType : 16;
    }
}

header_type intrinsic_metadata_t {
    fields {
        count: 8;
        recirculate_flag : 16;
    }
}

header_type mymeta_t {
    fields {
        f1 : 8;
    }
}
metadata mymeta_t mymeta;

header_type cpu_header_t {
    fields {
        count: 8;
        reason: 8;
    }
}

header cpu_header_t cpu_header;

parser start {
    return select(current(0, 64)) {
        0 : parse_cpu_header;
        default: parse_ethernet;
    }
}

header ethernet_t ethernet;
metadata intrinsic_metadata_t intrinsic_metadata;

parser parse_ethernet {
    extract(ethernet);
    return ingress;
}

parser parse_cpu_header {
    extract(cpu_header);
    return parse_ethernet;
}

action _drop() {
    drop();
}

action _nop() {
}

#define CPU_MIRROR_SESSION_ID_0                  250
#define CPU_MIRROR_SESSION_ID_1                  251

field_list copy_to_cpu_fields {
    standard_metadata;
    intrinsic_metadata;
}

action do_copy_to_cpu() {
    clone_ingress_pkt_to_egress(CPU_MIRROR_SESSION_ID_1, copy_to_cpu_fields);
}

table copy_to_cpu {
    actions {do_copy_to_cpu;}
    size : 1;
}


field_list copy_to_cpu_fields1 {
    standard_metadata;
    mymeta;
}

action do_recirculate_to_ingress() {
      add_to_field(mymeta.f1, 1);
      recirculate(copy_to_cpu_fields1);
}

table recirculate_to_ingress {
    actions { do_recirculate_to_ingress; }
    size : 1;
}

field_list copy_to_cpu_fields2 {
    standard_metadata;
    intrinsic_metadata;
}

action do_copy_to_cpu2() {
  clone_ingress_pkt_to_egress(CPU_MIRROR_SESSION_ID_0, copy_to_cpu_fields2);
}

table copy_to_cpu2 {
    actions { do_copy_to_cpu2; }
    size : 1;
}

table drop_table {
    actions {_drop;}
    size : 1;
}

control ingress {
    if(mymeta.f1 < 3) {
      apply(copy_to_cpu);
    }
    if(mymeta.f1 >= 3) {
      apply(copy_to_cpu2);
    }
}

action do_cpu_encap() {
    add_header(cpu_header);
    modify_field(cpu_header.count, 1);
    modify_field(cpu_header.reason, 0xab);
}

table redirect {
    reads { standard_metadata.instance_type : exact; }
    actions { do_cpu_encap; _nop; }
    size : 16;
}

control egress {
      apply(redirect);
      if (standard_metadata.instance_type != 1) {
        if(mymeta.f1 < 6) {
          apply(recirculate_to_ingress);
        }
        else {
          apply(drop_table);
        }
      }
}
