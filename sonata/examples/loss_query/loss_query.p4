/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_TCP = 6;

const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_NORMAL        = 0;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_INGRESS_CLONE = 1;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_EGRESS_CLONE  = 2;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_RECIRCULATE   = 4;

const bit<32> I2E_CLONE_SESSION_ID = 11;

#define IS_I2E_CLONE(std_meta) (std_meta.instance_type == BMV2_V1MODEL_INSTANCE_TYPE_INGRESS_CLONE)
#define IS_RECIRC(std_meta) (std_meta.instance_type == BMV2_V1MODEL_INSTANCE_TYPE_RECIRCULATE)

const bit<32> NUM_COUNTERS_PER_STAGE = 0x8000; // 2^15
const bit<4> INDEX_SIZE = 15; // ~32MB

const bit<5> EPOCH_POWER = 0; // ~2^N seconds. SET TO MATCH CONTROLLER.PY!

const bit<32> HASH_0 = 0xDEADBEEF;
const bit<32> HASH_1 = 0xABCABCAB;
const bit<32> HASH_2 = 0x01020304;
const bit<32> HASH_3 = 0x98765432;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct keys_t {
    bit<32> in_key0;
    bit<32> in_key1;
    bit<32> in_key2;
    bit<32> in_key3;
    bit<32> out_key0;
    bit<32> out_key1;
    bit<32> out_key2;
    bit<32> out_key3;
}

struct ipdata_t {
    bit<8> epoch;
    bit<16> count;
    bit<32> ip;
}

header out_header_t {
    bit<48> pkt_timestamp;
    bit<8> ingress_stage;
    bit<32> ingress_key;
    bit<8> egress_stage;
    bit<32> egress_key;
    bit<8> epoch;
}

struct metadata {
    keys_t      keys;

    bit<8>      epoch;

    bit<4>      curr_stage;
    bit<1>      inserted;
    bit<1>      new;
    bit<1>      reset;

    ipdata_t    ip_data;
    bit<56>     ip_data_raw;
    bit<16>     collision_count;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    tcp_t        tcp;
    out_header_t out_header;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
    out headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_TCP: parse_tcp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

// 0xfffff = 2^20 = 1048576

register<bit<48>>(1) start_timestamp;
register<bit<32>>(88) test;

register<bit<56>>(NUM_COUNTERS_PER_STAGE) counts_0;
register<bit<56>>(NUM_COUNTERS_PER_STAGE) counts_1;
register<bit<56>>(NUM_COUNTERS_PER_STAGE) counts_2;
register<bit<56>>(NUM_COUNTERS_PER_STAGE) counts_3;
register<bit<16>>(NUM_COUNTERS_PER_STAGE) collision_counts;

control Stage0(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_0() {
        meta.curr_stage = 0;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action hit_0() {
        hdr.out_header.ingress_key = meta.keys.in_key0;
        hdr.out_header.ingress_stage = 0;
        meta.inserted = 1;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        counts_0.write(meta.keys.in_key0, meta.ip_data_raw);
        hit_0();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        counts_0.write(meta.keys.in_key0, meta.ip_data_raw);
        hit_0();
    }

    apply {
        set_current_stage_0();

        counts_0.read(meta.ip_data_raw, meta.keys.in_key0);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Stage1(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_1() {
        meta.curr_stage = 1;
    }

    action hit_1() {
        hdr.out_header.ingress_stage = 1;
        hdr.out_header.ingress_key = meta.keys.in_key1;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        counts_1.write(meta.keys.in_key1, meta.ip_data_raw);
        hit_1();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        counts_1.write(meta.keys.in_key1, meta.ip_data_raw);
        hit_1();
    }


    apply {
        set_current_stage_1();

        counts_1.read(meta.ip_data_raw, meta.keys.in_key1);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Stage2(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_2() {
        meta.curr_stage = 2;
    }

    action hit_2() {
        hdr.out_header.ingress_stage = 2;
        hdr.out_header.ingress_key = meta.keys.in_key2;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        counts_2.write(meta.keys.in_key2, meta.ip_data_raw);
        hit_2();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        counts_2.write(meta.keys.in_key2, meta.ip_data_raw);
        hit_2();
    }

    apply {

        // # PER STAGE
        set_current_stage_2();

        // #4: check register value
        counts_2.read(meta.ip_data_raw, meta.keys.in_key2);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Stage3(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_3() {
        meta.curr_stage = 3;
    }

    action hit_3() {
        hdr.out_header.ingress_stage = 3;
        hdr.out_header.ingress_key = meta.keys.in_key3;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        counts_3.write(meta.keys.in_key3, meta.ip_data_raw);
        hit_3();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        counts_3.write(meta.keys.in_key3, meta.ip_data_raw);
        hit_3();
    }

    apply {
        // # GLOBAL FOR ALL STAGES
        // #1: get epoch ID
        set_current_stage_3();


        // #4: check register value
        counts_3.read(meta.ip_data_raw, meta.keys.in_key3);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Stage4_Collisions(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_4() {
        meta.curr_stage = 4;
    }

    action hit_4() {
        hdr.out_header.ingress_stage = 4;
        hdr.out_header.ingress_key = (bit<32>) meta.epoch;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action update() {
        collision_counts.read(meta.collision_count, (bit<32>) meta.epoch);
        meta.collision_count = meta.collision_count + 1;
        collision_counts.write((bit<32>) meta.epoch, meta.collision_count);
    }

    apply {
        set_current_stage_4();

        update();
        if (meta.inserted != 1) {
            hit_4();
        }
    }
}

control MyIngress(inout headers hdr,
  inout metadata meta,
  inout standard_metadata_t standard_metadata) {

  action get_hashes() {
      hash(meta.keys.in_key0,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_0},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.out_key0,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_0},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.in_key1,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_1},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.out_key1,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_1},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.in_key2,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_2},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.out_key2,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_2},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.in_key3,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_3},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15

      hash(meta.keys.out_key3,
          HashAlgorithm.crc32,
          (bit<32>) 0,
          {hdr.ipv4.srcAddr,
              meta.epoch,
              HASH_3},
          (bit<16>) 0x8fff); // matches NUM_COUNTERS_PER_STAGE = 2^15
  }

  action set_epoch() {
        start_timestamp.read(hdr.out_header.pkt_timestamp, 0);
        meta.epoch = (standard_metadata.ingress_global_timestamp[27:20] - hdr.out_header.pkt_timestamp[27:20]) >> EPOCH_POWER;
        hdr.out_header.pkt_timestamp = standard_metadata.ingress_global_timestamp;
    }

    action start_experiment() {
        meta.reset = 1;
        start_timestamp.write(0, standard_metadata.ingress_global_timestamp);
    }

    apply {

        meta.reset = 0;

        if (hdr.ipv4.version == 0) { // begin simulation
            start_experiment();
        }
        if (meta.reset != 1) {
            set_epoch();
            get_hashes();
            if (hdr.ipv4.isValid()) {
                Stage0.apply(hdr, meta, standard_metadata);
                if (meta.inserted != 1) {
                    Stage1.apply(hdr, meta, standard_metadata);
                }
                if (meta.inserted != 1) {
                    Stage2.apply(hdr, meta, standard_metadata);
                }
                if (meta.inserted != 1) {
                    Stage3.apply(hdr, meta, standard_metadata);
                }
                Stage4_Collisions.apply(hdr, meta, standard_metadata);
            }
        }
        standard_metadata.egress_spec = 12;
        hdr.out_header.setValid();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

register<bit<56>>(NUM_COUNTERS_PER_STAGE) egress_counts_5;
register<bit<56>>(NUM_COUNTERS_PER_STAGE) egress_counts_6;
register<bit<56>>(NUM_COUNTERS_PER_STAGE) egress_counts_7;
register<bit<56>>(NUM_COUNTERS_PER_STAGE) egress_counts_8;
register<bit<16>>(NUM_COUNTERS_PER_STAGE) egress_collision_counts;

control Egress_Stage5(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_5() {
        meta.curr_stage = 5;
    }

    action hit_5() {
        hdr.out_header.egress_stage = 5;
        hdr.out_header.egress_key = meta.keys.out_key0;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        egress_counts_5.write(meta.keys.out_key0, meta.ip_data_raw);
        hit_5();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        egress_counts_5.write(meta.keys.out_key0, meta.ip_data_raw);
        hit_5();
    }

    apply {
        set_current_stage_5();

        egress_counts_5.read(meta.ip_data_raw, meta.keys.out_key0);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Egress_Stage6(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_6() {
        meta.curr_stage = 6;
    }

    action hit_6() {
        hdr.out_header.egress_stage = 6;
        hdr.out_header.egress_key = meta.keys.out_key1;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        egress_counts_6.write(meta.keys.out_key1, meta.ip_data_raw);
        hit_6();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        egress_counts_6.write(meta.keys.out_key1, meta.ip_data_raw);
        hit_6();
    }

    apply {
        set_current_stage_6();

        egress_counts_6.read(meta.ip_data_raw, meta.keys.out_key1);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Egress_Stage7(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_7() {
        meta.curr_stage = 7;
    }

    action hit_7() {
        hdr.out_header.egress_stage = 7;
        hdr.out_header.egress_key = meta.keys.out_key2;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        egress_counts_7.write(meta.keys.out_key2, meta.ip_data_raw);
        hit_7();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        egress_counts_7.write(meta.keys.out_key2, meta.ip_data_raw);
        hit_7();
    }

    apply {
        set_current_stage_7();

        egress_counts_7.read(meta.ip_data_raw, meta.keys.out_key2);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Egress_Stage8(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_8() {
        meta.curr_stage = 8;
    }

    action hit_8() {
        hdr.out_header.egress_stage = 8;
        hdr.out_header.egress_key = meta.keys.out_key3;
        meta.inserted = 1;
    }

    action extract_reg() {
        meta.ip_data.epoch = meta.ip_data_raw[55:48];
        meta.ip_data.count = meta.ip_data_raw[47:32];
        meta.ip_data.ip = meta.ip_data_raw[31:0];
    }

    action compile_reg() {
        meta.ip_data_raw[55:48] = meta.ip_data.epoch;
        meta.ip_data_raw[47:32] = meta.ip_data.count;
        meta.ip_data_raw[31:0] = meta.ip_data.ip;
    }

    action replace() {
        meta.ip_data.epoch = meta.epoch;
        meta.ip_data.count = 1;
        meta.ip_data.ip = hdr.ipv4.srcAddr;
        compile_reg();
        egress_counts_8.write(meta.keys.out_key3, meta.ip_data_raw);
        hit_8();
        meta.new = 1;
    }

    action update() {
        meta.ip_data.count = meta.ip_data.count + 1;
        compile_reg();
        egress_counts_8.write(meta.keys.out_key3, meta.ip_data_raw);
        hit_8();
    }

    apply {
        set_current_stage_8();

        egress_counts_8.read(meta.ip_data_raw, meta.keys.out_key3);
        extract_reg();

        if (meta.epoch - meta.ip_data.epoch > 1) { // old epoch, replace
            replace();
        } else if (hdr.ipv4.srcAddr == meta.ip_data.ip) { // same IP, count
            update();
        } else {
            meta.inserted = 0;
        }
    }
}

control Egress_Stage9_Collisions(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action set_current_stage_9() {
        meta.curr_stage = 9;
    }

    action hit_9() {
        hdr.out_header.egress_stage = 9;
        hdr.out_header.egress_key = (bit<32>) meta.epoch;
        meta.inserted = 1;
    }

    action update() {
        egress_collision_counts.read(meta.collision_count, (bit<32>) meta.epoch);
        meta.collision_count = meta.collision_count + 1;
        collision_counts.write((bit<32>) meta.epoch, meta.collision_count);
    }

    apply {
        set_current_stage_9();

        update();

        if (meta.inserted != 1) {
            hit_9();
        }
    }
}

control MyEgress(inout headers hdr,
 inout metadata meta,
 inout standard_metadata_t standard_metadata) {

    action clear_inserted() {
        meta.inserted = 0;
    }

    action epoch_header() {
        hdr.out_header.epoch = meta.epoch;
    }

    apply {
        clear_inserted();
        if (meta.reset != 1) {
            Egress_Stage5.apply(hdr, meta, standard_metadata);
            if (meta.inserted != 1) {
                Egress_Stage6.apply(hdr, meta, standard_metadata);
            }
            if (meta.inserted != 1) {
                Egress_Stage7.apply(hdr, meta, standard_metadata);
            }
            if (meta.inserted != 1) {
                Egress_Stage8.apply(hdr, meta, standard_metadata);
            }
            Egress_Stage9_Collisions.apply(hdr, meta, standard_metadata);
            if (meta.new != 1) {
                mark_to_drop(standard_metadata);
            }
        }
        test.write(0, meta.keys.in_key0);
        test.write(1, meta.keys.out_key0);
        test.write(2, hdr.out_header.ingress_key);
        test.write(3, hdr.out_header.egress_key);
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply {
       update_checksum(
           hdr.ipv4.isValid(),
           { hdr.ipv4.version,
             hdr.ipv4.ihl,
             hdr.ipv4.diffserv,
             hdr.ipv4.totalLen,
             hdr.ipv4.identification,
             hdr.ipv4.flags,
             hdr.ipv4.fragOffset,
             hdr.ipv4.ttl,
             hdr.ipv4.protocol,
             hdr.ipv4.srcAddr,
             hdr.ipv4.dstAddr},
             hdr.ipv4.hdrChecksum,
             HashAlgorithm.csum16);
   }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.out_header);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
    ) main;