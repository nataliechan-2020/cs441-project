import socket
import time
import threading
from functions import send_node, encrypt, decrypt, load_key, split_packet, details, settings
from logs import log_ip, log_protocol, sniffing_log, blocked_data

# Initialise IP and MAC addresses
node4_ip = "0x1B"
node4_mac = "N4"

# Socket
node4 = socket.socket()
intra4 = socket.socket()

# Connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node4.connect(router)  

time.sleep(1)
node1 = ("localhost", 3000)
intra4.connect(node1) 

# ARP table
router_mac = "R1"
node1_mac = "N1"
node1_ip = "0x1A"
node2_ip = "0x2A"
node3_ip = "0x2B"

# key = str.encode("1234567812345678")
# key = get_random_bytes(16) 
key = load_key()

arp_mac = {node1_ip : node1_mac, node2_ip : router_mac, node3_ip: router_mac}

def from_router():
    try:
        while True:
            received_message = node4.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data = split_packet(received_message)
            protocol_flag = data[0]
            data = data[1:]

            try:
                # data = data.decode()
                data = decrypt(data, key)
                data = data.decode('utf-8')
            except Exception as e:
                print(data)

            # drop packet
            if dest_mac != node4_mac:
                print("\nPACKET DROPPED")

            else:
                print("\nINCOMING PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()
                    
                    ethernet_header = node4_mac + "," + arp_mac[sorc_ip]
                    IP_header = node4_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    node4.send(bytes(packet, "utf-8")) # to router
                    try:
                        intra4.send(bytes(packet, "utf-8"))  # to node2, if connected
                    except Exception as e:
                        print(e)
                        print("NODE 1 NOT FOUND")

                elif protocol == "1" and protocol_flag == "K":
                    print("EXIT")
                    node4.close()
                    try:
                        intra4.close()
                    except Exception as e:
                        print(e)
                        print("NODE 1 NOT FOUND")
    
    except Exception as e:
        print(e)
        print("NODE 4 EXITED")

# receive from node2
def from_node1():
    try:
        while True:
            received_message = intra4.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data = split_packet(received_message)
            protocol_flag = data[0]
            data = data[1:]

            try:
                # data = data.decode()
                data = decrypt(data, key)
                data = data.decode('utf-8')
            except Exception as e:
                print(data)
            
            # drop packet
            if dest_mac != node4_mac:
                print("\nPACKET DROPPED")

            else:
                print("\nINCOMING PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()

                    ethernet_header = node4_mac + "," + arp_mac[sorc_ip]
                    IP_header = node4_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    intra4.send(bytes(packet, "utf-8"))
                    node4.send(bytes(packet, "utf-8"))

                elif protocol == "1" and protocol_flag == "K":
                    print("EXIT")
                    node4.close()
                    intra4.close()
    
    except Exception as e:
        print(e)
        print("NODE 1 NOT FOUND")

receive_from_router_thread = threading.Thread(target=from_router)
receive_from_node1_thread = threading.Thread(target=from_node1)
receive_from_router_thread.start()
receive_from_node1_thread.start()

while True:
    try:
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        packet = send_node(1, node1_ip, node2_ip, node3_ip, node4_ip, node4_mac, arp_mac, ethernet_header, IP_header)
        node4.send(bytes(packet, "utf-8"))
        try:
            intra4.send(bytes(packet, "utf-8"))
        except Exception as e:
            print(e)
            print("NODE 1 NOT FOUND")
    
    except Exception as e:
        print(e)
        print("NODE 4 EXITED")