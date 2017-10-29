from scapy.all import *
import time

NORMAL_PACKET_COUNT = 10
ATTACK_PACKET_COUNT = 10

IFACE = "out-veth-1"


def create_normal_traffic():
    number_of_packets = NORMAL_PACKET_COUNT
    normal_packets = []

    for i in range(number_of_packets):
        sIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / "SONATA NORMAL"
        normal_packets.append(p)

    return normal_packets


def create_attack_traffic():
    number_of_packets = ATTACK_PACKET_COUNT
    dIP = '99.7.186.25'
    sIPs = []
    attack_packets = []

    for i in range(number_of_packets):
        sIPs.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))

    sport = 50
    dport = 70
    for sIP in sIPs:
        sport += 10
        dport += 10
        p = Ether() / IP(dst=dIP, src=sIP, len=100) / TCP(sport=sport, dport=dport) / "SONATA"
        # print p.summary()
        attack_packets.append(p)

    return attack_packets


def send_created_traffic():
    traffic_dict = {}
    attack = True

    total_duration = 60
    attack_duration = 50
    attack_start_time = 5

    for i in range(0, total_duration):
        traffic_dict[i] = []
        traffic_dict[i].extend(create_normal_traffic())
        if attack_start_time <= i < attack_start_time + attack_duration:
            traffic_dict[i].extend(create_attack_traffic())

    print "******************** Sending Normal Traffic *************************"
    for i in range(0, total_duration):
        # print "Sending traffic for ts: " + str(i)
        start = time.time()
        if attack_start_time <= i < attack_start_time + attack_duration and attack:
            attack = False
            print "******************** Sending Attack Traffic *************************"
        if i == attack_start_time + attack_duration:
            attack = False

        if not attack and i > attack_start_time + attack_duration:
            attack = True
            print "******************** Sending Normal Traffic *************************"

        sendp(traffic_dict[i], iface=IFACE, verbose=0)
        total = time.time() - start
        sleep_time = 1 - total
        print sleep_time
        if sleep_time > 0:
            time.sleep(sleep_time)


send_created_traffic()
