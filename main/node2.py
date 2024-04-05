import socket
import time
import threading
from functions import send_node, encrypt, decrypt, load_key, split_packet, details
from logs import sniffing_log

# Initialise IP and MAC addresses
node2_ip = "0x2A"
node2_mac = "N2"

# sockets
node2 = socket.socket() # binds to router
intra2 = socket.socket() # binds to node 3
intra2.bind(("localhost", 2000))

# accept node 3
intra2.listen(2)
node3 = None

while (node3 == None):
    if (node3 == None):
        node3, address = intra2.accept()

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node2.connect(router)

# arp table
router_mac = "R2"
node3_mac = "N3"
node1_ip = "0x1A"
node3_ip = "0x2B"
node4_ip = "0x1B"

arp_mac = {node1_ip : router_mac, node3_ip : node3_mac, node4_ip : router_mac}
# key = str.encode("1234567812345678")
# key = get_random_bytes(16) 

# receive from router
def from_router():
    try:
        while True:
            key = load_key()
            received_message = node2.recv(1024)
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
            # if dest_mac != node2_mac:
            #     print("\nPACKET DROPPED")

            # sniff
            if dest_ip == node3_ip and sorc_ip == node1_ip and dest_mac!="N2":
                print("\nINTERCEPTED PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                sniffing_log(data, sorc_ip, dest_ip, 2)
            elif dest_ip == node1_ip and sorc_ip == node3_ip and dest_mac!="N2":
                print("\nINTERCEPTED PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                sniffing_log(data, sorc_ip, dest_ip, 2)
            elif dest_mac != node2_mac:
                print("\nPACKET DROPPED")
            else:
                print("\nINCOMING PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()

                    ethernet_header = node2_mac + "," + arp_mac[sorc_ip]
                    IP_header = node2_ip + "," + sorc_ip + "," +  protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    node2.send(bytes(packet, "utf-8")) # to router
                    try:
                        node3.send(bytes(packet, "utf-8")) # to node 3, if connected
                    except Exception as e:
                        print("NODE 3 NOT FOUND")

                elif protocol == "1" and protocol_flag == "K":
                    print("\nEXIT")
                    node2.close()
                    try:
                        node3.close()
                    except Exception as e:
                        print("NODE 3 NOT FOUND")

    except Exception as e:
        print("NODE 2 EXITED")

# receive from node3
def from_node3():
    try:
        while True:
            key = load_key()
            received_message = node3.recv(1024)
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
            # if dest_mac != node2_mac:
            #     print("\nPACKET DROPPED")

            # sniffing attack
            if dest_ip == node3_ip and sorc_ip == node1_ip and dest_mac!="N2":
                print("\nINTERCEPTED PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                sniffing_log(data, sorc_ip, dest_ip, 2)
            elif dest_ip == node1_ip and sorc_ip == node3_ip and dest_mac!="N2":
                print("\nINTERCEPTED PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                sniffing_log(data, sorc_ip, dest_ip, 2)
            elif dest_mac != node2_mac:
                print("\nPACKET DROPPED")
            else:
                print("\nINCOMING PACKET:")
                details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()
                    
                    ethernet_header = node2_mac + "," + arp_mac[sorc_ip]
                    IP_header = node2_ip + "," + sorc_ip + "," +  protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    node3.send(bytes(packet, "utf-8"))
                    node2.send(bytes(packet, "utf-8"))
                
                elif protocol == "1" and protocol_flag == "K":
                    print("\nEXIT")
                    node2.close()
                    node3.close()

    except Exception as e:
        print("NODE 3 NOT FOUND")

receive_from_router_thread = threading.Thread(target=from_router)
receive_from_node3_thread = threading.Thread(target=from_node3)
receive_from_router_thread.start()
receive_from_node3_thread.start()

while True:
    try: 
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        packet = send_node(2, node1_ip, node3_ip, node4_ip, node2_ip, node2_mac, arp_mac, ethernet_header, IP_header)
        node2.send(bytes(packet, "utf-8")) # goes to router
        try:
            node3.send(bytes(packet, "utf-8")) # goes to node3 (cos its sent to all nodes in the network)
        except Exception as e:
            print("NODE 3 NOT FOUND")

    except Exception as e:
        print("NODE 2 EXITED")