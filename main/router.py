import socket
import threading
from functions import receive_router
from logs import clear_log, create_logfile

# Initialise IP and MAC addresses
router1_ip = "0x11"
router1_mac = "R1"
router2_ip = "0x21"
router2_mac = "R2"

create_logfile()
clear_log()

# Rate Limiting
def initialize_counter():
    count=[0]

    def count_times():
        count[0]+=1
        if count[0] >= 20:
            print("EXIT")
            raise SystemExit
        return count[0]
    return count_times
counter = initialize_counter()

def from_node1(node1, arp_socket, arp_mac, router2_mac):
    while True:
        try:
            # Receive from node1
            received_message = node1.recv(1024).decode("utf-8")
            print("-- NODE 1 ---")
            sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 1, None, arp_mac)

            # Forward packet to node2
            IP_header = sorc_ip + dest_ip + protocol
            ethernet_header = router2_mac + arp_mac[dest_ip]
            packet = ethernet_header + IP_header + data_length + data
            dest = arp_socket[node2_mac]
            dest.send(bytes(packet, "utf-8"))

            # Forward packet to node3
            dest = arp_socket[node3_mac]
            dest.send(bytes(packet, "utf-8"))

            
            print(counter())
        except socket.error as e:
            print("Socket error:", e)

def from_node2(node2, arp_socket, arp_mac, router1_mac):
    while True:
        try:
            # Receive from node2
            received_message = node2.recv(1024).decode("utf-8")
            print("-- NODE 2 --")
           
            sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 2, router2_mac, arp_mac)
            if packet_dropped == False:
                # Send packet back to node1
                IP_header = sorc_ip + dest_ip + protocol
                ethernet_header = router1_mac + arp_mac[dest_ip]
                packet = ethernet_header + IP_header + data_length + data
                dest = arp_socket[node1_mac]
                dest.send(bytes(packet, "utf-8"))
            
            print(counter())
        except socket.error as e:
            print("Socket error:", e)

def from_node3(node3, arp_socket, node1_ip, router1_mac):
    while True:
        try:
            # Receive from node3
            received_message = node3.recv(1024).decode("utf-8")
            print("-- NODE 3 --")
            sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 3, node1_ip, arp_mac)
            if packet_dropped == False:
                IP_header = sorc_ip + dest_ip + protocol
                ethernet_header = router1_mac + node1_mac
                packet = ethernet_header + IP_header + data_length + data
                dest = arp_socket[node1_mac]
                dest.send(bytes(packet, "utf-8"))
            
            print(counter())
        except socket.error as e:
            print("Socket error:", e)

# Socket (network 1)
router1 = socket.socket()
router1.bind(("localhost", 1200))
router1.listen(2)
node1, _ = router1.accept()

# Socket (network 2)
router2 = socket.socket()
router2.bind(("localhost", 2200))
router2.listen(4)
node2, _ = router2.accept()
node3, _ = router2.accept()

print("CONNECTED")

# arp table
node1_mac = "N1"
node2_mac = "N2"
node3_mac = "N3"
node1_ip = "0x1A"
node2_ip = "0x2A"
node3_ip = "0x2B"

arp_socket = {node1_mac: node1, node2_mac: node2, node3_mac: node3}
arp_mac = {node1_ip: node1_mac, node2_ip: node2_mac, node3_ip: node3_mac}

node1_thread = threading.Thread(target=from_node1, args=(node1, arp_socket, arp_mac, router2_mac))
node1_thread.start()

node2_thread = threading.Thread(target=from_node2, args=(node2, arp_socket, arp_mac, router1_mac))
node2_thread.start()

node3_thread = threading.Thread(target=from_node3, args=(node3, arp_socket, node1_ip, router1_mac))
node3_thread.start()
