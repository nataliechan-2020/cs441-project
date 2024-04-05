import socket
import time
import threading
from functions import send_node, encrypt, decrypt, load_key, split_packet, details
from logs import sniffing_log

# Initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# Socket
node1 = socket.socket()

#intra-socket
intra1 = socket.socket() # binds to node 4
intra1.bind(("localhost", 3000))

# accept node 4
intra1.listen()
node4 = None

while (node4 == None):
    if (node4 == None):
        node4, address = intra1.accept()

# Connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router) 

# ARP table
router_mac = "R1"
node4_mac = "N4"
node2_ip = "0x2A"
node3_ip = "0x2B"
node4_ip = "0x1B"

#ARP Mac Table
arp_mac = {node4_ip: node4_mac, node2_ip: router_mac, node3_ip : router_mac}

# key = str.encode("1234567812345678")
# key = get_random_bytes(16) 

# Receive data from router
def from_router():
    key = load_key()
    # print("PRINTING")
    # print(key)
    try:
        while True:
            received_message = node1.recv(1024)
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

            if dest_mac != node1_mac:
                print("\nPACKET DROPPED")

            # log
            elif dest_ip == node2_ip and sorc_ip ==node3_ip:
                sniffing_log(data, sorc_ip, dest_ip, 1)
            elif dest_ip == node3_ip and sorc_ip == node2_ip:
                sniffing_log(data, sorc_ip, dest_ip, 1)
            
            else:
                print("\nINCOMING PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()

                    ethernet_header = node1_mac + "," + arp_mac[sorc_ip]
                    IP_header = node1_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    node1.send(bytes(packet, "utf-8")) # to router
                    try:
                        node4.send(bytes(packet, "utf-8")) # to node 4, if connected
                    except Exception as e:
                        print("NODE 4 NOT FOUND")

                elif protocol == "1" and protocol_flag == "K":
                    print("\nEXIT")
                    node1.close()
                    try:
                        node4.close()
                    except Exception as e:
                        print("NODE 3 NOT FOUND")
        
    except Exception as e:
        print("NODE 1 EXITED")

def from_node4():
    key = load_key()
    # print("PRINTING")
    # print(key)
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

            if dest_mac != node1_mac:
                print("\nPACKET DROPPED")

            # log
            elif dest_ip == node2_ip and sorc_ip ==node3_ip:
                sniffing_log(data, sorc_ip, dest_ip, 1)
            elif dest_ip == node3_ip and sorc_ip == node2_ip:
                sniffing_log(data, sorc_ip, dest_ip, 1)
            
            else:
                print("\nINCOMING PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()
                    
                    ethernet_header = node1_mac + "," + arp_mac[sorc_ip]
                    IP_header = node1_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    node4.send(bytes(packet, "utf-8"))
                    node1.send(bytes(packet, "utf-8"))
                        
                elif protocol == "1" and protocol_flag == "K":
                    print("\nEXIT")
                    node4.close()
                    node1.close()
        
    except Exception as e:
        print("NODE 4 NOT FOUND")

receive_from_router_thread = threading.Thread(target=from_router)
receive_from_node4_thread = threading.Thread(target=from_node4)
receive_from_router_thread.start()
receive_from_node4_thread.start()

# main thread, sending
while True:
    try:
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        packet = send_node(1, node2_ip, node3_ip, node4_ip, node1_ip, node1_mac, arp_mac, ethernet_header, IP_header)
        node1.send(bytes(packet, "utf-8")) # goes to router
        try:
            node4.send(bytes(packet, "utf-8")) # goes to node4 (cos its sent to all nodes in the network)
        except Exception as e:
            print("NODE 4 NOT FOUND")

    except Exception as e:
        print("NODE 1 EXITED")

