import base64
import argparse
import os
import sys
import codecs
from scapy.utils import *
from scapy.layers.l2 import Ether
from scapy.layers.dns import DNS
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6

#Sources:
#https://vnetman.github.io/pcap/python/pyshark/scapy/libpcap/2018/10/25/analyzing-packet-captures-with-python-part-1.html
#https://medium.com/a-bit-off/scapy-ways-of-reading-pcaps-1367a05e98a8\

INPUT_PCAP = "./mitschnitt.pcapng"

def process_pcap(file_name):
    print("Opening pcapfile...")
    packets = rdpcap(file_name)
    index = 1
    hidden_message = ""
    last_message = ""
    for packet in packets:
        print("Index: %d" % index)
        if packet.haslayer(DNS) and packet.haslayer(IPv6) and packet.getlayer(IPv6).dst == "fd15:4ba5:5a2b:1004:dc60:bf9c:674e:e8b6":
            dns_layer = packet.getlayer(DNS)
            dns_answers = packet.answers
            #print(type(dns_answers))
            dns_answers_splitted = str(dns_answers).split(" ")

            if "c2.mlwreprvt.de" not in str(dns_answers):
                print("c2.mlwreprvt.de not found.")
                continue

            str_match = [s for s in dns_answers_splitted if "rdata" in s][0]
            covert_data = str_match.split(":")[3]
            print(covert_data)
            
            if covert_data == last_message:
                print("Daten schon vorhanden")
                continue
            
            #print(dir(dns_answers))
            for c in codecs.decode(covert_data, 'hex'):
                print("DATA RECEIVED: %c " % chr(c))
                hidden_message = hidden_message + chr(c)

            last_message = covert_data
            #layer = packet.getlayer(IPv6)
            #print(dir(layer))
            #print(layer.dst)

        index = index + 1

    print("Hiddden-Message: %s" % hidden_message)
    message_decoded = base64.b64decode(hidden_message)
    message_reversed = str(message_decoded)[::-1]
    print(message_reversed)
    
def process_pcap_old(file_name):
    print('Opening {}...'.format(file_name))

    count = 0
    interesting_packet_count = 0
    
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        count += 1
        
        ether_pkt = Ether(pkt_data)
        if 'type' not in ether_pkt.fields:
            # LLC frames will have 'len' instead of 'type'.
            # We disregard those
            continue

        if ether_pkt.type != 0x0800:
            # disregard non-IPv4 packets
            continue

        ip_pkt = ether_pkt[IP]
        if ip_pkt.proto != 6:
            # Ignore non-TCP packet
            continue

        interesting_packet_count += 1

    print('{} contains {} packets ({} interesting)'.format(file_name, count, interesting_packet_count))

if __name__ == '__main__':
    file_name = INPUT_PCAP
    if not os.path.isfile(file_name):
        print('"{}" does not exist'.format(file_name), file=sys.stderr)
        sys.exit(-1)

    process_pcap(file_name)
    sys.exit(0)
