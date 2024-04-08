import socket
import threading
from functions import receive_router, save_key
from logs import clear_log, create_logfile
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import time

# Initialise IP and MAC addresses
router1_ip = "0x11"
router1_mac = "R1"
router2_ip = "0x21"
router2_mac = "R2"

create_logfile()
clear_log()
key = get_random_bytes(16) 
save_key(key)

# Rate Limiting
def initialize_counter():
    count=[0]

    def count_times():
        count[0]+=1
        if count[0] >= 20:
            print("EXIT")
            time.sleep(10)
            # raise SystemExit
        return count[0]
    return count_times
counter = initialize_counter()

def from_node1(node1, arp_socket, arp_mac, router2_mac):
    try:
        while True:
            try:
                # Receive from node1
                received_message = node1.recv(1024).decode("utf-8")
                print("\n-- NODE 1 ---")
                # print(received_message)
                sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 1, router1_mac, arp_mac)
                if packet_dropped == False:
                    # Forward packet to node2
                    IP_header = sorc_ip + "," + dest_ip + "," + protocol
                    # print(dest_ip)
                    ethernet_header = router2_mac + "," + arp_mac[dest_ip]
                    packet = ethernet_header + "," + payload_length + "," + IP_header + "," + data_length + "," + data
                    dest = arp_socket[node2_mac]
                    dest.send(bytes(packet, "utf-8"))

                    # Forward packet to node3
                    dest = arp_socket[node3_mac]
                    dest.send(bytes(packet, "utf-8"))
                print(counter())
            except Exception as  e:
                print("EXITED")
                break
    except socket.error as e:
        print("Socket error:", e)

def from_node2(node2, arp_socket, arp_mac, router1_mac):
    try:
        while True:
            try:
                # Receive from node2
                received_message = node2.recv(1024).decode("utf-8")
                print("\n-- NODE 2 --")
                # print(received_message)
                sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 2, router2_mac, arp_mac)
                if packet_dropped == False:
                    # Forward packet to node1
                    IP_header = sorc_ip + "," + dest_ip + "," + protocol
                    ethernet_header = router1_mac + "," +  arp_mac[dest_ip]
                    packet = ethernet_header + "," + payload_length + "," + IP_header + "," + data_length + "," + data
                    dest = arp_socket[node1_mac]
                    dest.send(bytes(packet, "utf-8"))
                    
                    # Forward packet to node4
                    dest = arp_socket[node4_mac]
                    dest.send(bytes(packet, "utf-8"))
                print(counter())
            except Exception as e:
                print("EXITED")
                break
    except socket.error as e:
        print("Socket error:", e)

def from_node3(node3, arp_socket, arp_mac, router1_mac):
    try:
        while True:
            try:
                # Receive from node3
                received_message = node3.recv(1024).decode("utf-8")
                print("\n-- NODE 3 --")
                sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 3, router2_mac, arp_mac)
                if packet_dropped == False:
                    # Forward packet to node1
                    IP_header = sorc_ip + "," + dest_ip + "," +  protocol
                    ethernet_header = router1_mac + "," + arp_mac[dest_ip]
                    packet = ethernet_header + "," + payload_length + "," + IP_header + "," + data_length + "," + data
                    dest = arp_socket[node1_mac]
                    dest.send(bytes(packet, "utf-8"))

                    # Forward packet to node4
                    dest = arp_socket[node4_mac]
                    dest.send(bytes(packet, "utf-8"))
                print(counter())
            except Exception as e:
                print("EXITED")
                break
    except socket.error as e:
        print("Socket error:", e)

def from_node4(node4, arp_socket, arp_mac, router2_mac):
    try:
        while True:
            try:
                # Receive from node4
                received_message = node4.recv(1024).decode("utf-8")
                print("\n-- NODE 4 ---")
                # print(received_message)
                sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data, packet_dropped = receive_router(received_message, 4, router1_mac, arp_mac)
                if packet_dropped == False:
                    # Forward packet to node2
                    IP_header = sorc_ip + "," + dest_ip + "," + protocol
                    # print(dest_ip)
                    ethernet_header = router2_mac + "," + arp_mac[dest_ip]
                    packet = ethernet_header + "," + payload_length + "," + IP_header + "," + data_length + "," + data
                    dest = arp_socket[node2_mac]
                    dest.send(bytes(packet, "utf-8"))

                    # Forward packet to node3
                    dest = arp_socket[node3_mac]
                    dest.send(bytes(packet, "utf-8"))
                print(counter())
            except Exception as  e:
                print("EXITED")
                break
    except socket.error as e:
        print("Socket error:", e)

# Socket (network 1)
router1 = socket.socket()
router1.bind(("localhost", 1200))
router1.listen(4)
print("Waiting for Node4 to connect...")
node4, _ = router1.accept()
print("Node4 connected.")
print("Waiting for Node1 to connect...")
node1, _ = router1.accept()
print("Node1 connected.")

# Socket (network 2)
router2 = socket.socket()
router2.bind(("localhost", 2200))
router2.listen(4)
print("Waiting for Node3 to connect...")
node3, _ = router2.accept()
print("Node3 connected.")
print("Waiting for Node2 to connect...")
node2, _ = router2.accept()
print("Node2 connected.")
print("ALL NODES CONNECTED")

# arp table
node1_mac = "N1"
node2_mac = "N2"
node3_mac = "N3"
node4_mac = "N4"
node1_ip = "0x1A"
node2_ip = "0x2A"
node3_ip = "0x2B"
node4_ip = "0x1B"

arp_socket = {node1_mac: node1, node2_mac: node2, node3_mac: node3, node4_mac: node4}
arp_mac = {node1_ip: node1_mac, node2_ip: node2_mac, node3_ip: node3_mac, node4_ip: node4_mac}

node1_thread = threading.Thread(target=from_node1, args=(node1, arp_socket, arp_mac, router2_mac))
node1_thread.start()

node2_thread = threading.Thread(target=from_node2, args=(node2, arp_socket, arp_mac, router1_mac))
node2_thread.start()

node3_thread = threading.Thread(target=from_node3, args=(node3, arp_socket, arp_mac, router1_mac))
node3_thread.start()

node4_thread = threading.Thread(target=from_node4, args=(node4, arp_socket, arp_mac, router2_mac))
node4_thread.start()
