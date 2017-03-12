#!/usr/bin/env python
#  Author:
#  Marc Leef (mleef@cs.princeton.edu)

import threading, logging, time
from struct import *
from scapy.all import *
from kafka import KafkaConsumer


class PycapaConsumer(threading.Thread):
    """Kafka consumer that consumes packet data from 'pycapa'
    Attributes:
        daemon (bool): Specifies if this thread is a daemon.
        gh_format (string): Format for global headers from 'pycapa'.
        ph_format (string): Format for packet headers from 'pycapa'.
        gh_struct (struct.Struct): Struct to be used for global header unpacking.
        ph_struct (struct.Struct): Struct to be used for packet header unpacking.
        gh_size (int): Size of global header in bytes.
        ph_size (int): Size of packet header in bytes.
    """

    daemon = True

    # Pack formats specified by 'pycapa'
    gh_format = 'IHHIIII'
    ph_format = 'IIII'

    # To unpack packet headers
    gh_struct = struct.Struct(gh_format)
    ph_struct = struct.Struct(ph_format)

    # Header lengths for proper processing
    gh_size = calcsize(gh_format)
    ph_size = calcsize(ph_format)

    def __init__(self, topic):
        """Constructor
        Args:
            topic (string): Topic to consume messages from and subscribe to.
        """

        threading.Thread.__init__(self)
        self.topic = topic

    def unpack_global_header(self, raw_packet):
        """Extracts global headers from raw packet bytes
        Args:
            raw_packet (string): Raw packet bytes from 'pycapa'.
        Returns:
            tuple: Containing extracted fields.
        """
        return self.gh_struct.unpack(raw_packet[:self.gh_size])

    def unpack_packet_header(self, raw_packet):
        """Extracts packet headers from raw packet bytes
        Args:
            raw_packet (string): Raw packet bytes from 'pycapa'.
        Returns:
            tuple: Containing extracted fields.
        """
        return self.ph_struct.unpack(raw_packet[self.gh_size:self.gh_size + self.ph_size])

    def assemble_packet(self, raw_packet):
        """Assembles scapy packet from raw packet bytes
        Args:
            raw_packet (string): Raw packet bytes from 'pycapa'.
        Returns:
            scapy.Ether: Ethernet packet.
        """
        return Ether(raw_packet[self.gh_size + self.ph_size:])

    def run(self):
        """Subscribes to specified topic and assembles packet tuples.

        """

        try:
            consumer = KafkaConsumer(bootstrap_servers='localhost:9092')
            consumer.subscribe([self.topic])

            for message in consumer:
                raw_packet = message.value

                # Extract headers added by 'pycapa'
                gh = self.unpack_global_header(raw_packet)
                ph = self.unpack_packet_header(raw_packet)

                # Extract actual packet data
                packet = self.assemble_packet(raw_packet)

                # Initialize tuple values
                src_ip = ''
                dst_ip = ''
                proto = ''
                num_bytes = ''
                src_port = ''
                dst_port = ''
                src_mac = packet.src
                dst_mac = packet.dst

                # Extract IP layer information
                if (IP in packet):
                    src_ip = str(packet[IP].src)
                    dst_ip = str(packet[IP].dst)
                    proto = str(packet[IP].proto)
                    num_bytes = packet[IP].len

                # Extract TCP/UDP specific information
                if (TCP in packet):
                    src_port = packet[TCP].sport
                    dst_port = packet[TCP].dport
                elif (UDP in packet):
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport

                # Assemble final output tuple
                output_tuple = (packet.time, src_ip, src_port, dst_ip, dst_port, num_bytes, proto, src_mac, dst_mac)
                print output_tuple

        except Exception as e:
            print "Error consuming packets from Kafka: " + repr(e)


def main():
    consumerThread = PycapaConsumer('packets')
    consumerThread.start()
    # Consume for one minute
    time.sleep(60)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
main()
