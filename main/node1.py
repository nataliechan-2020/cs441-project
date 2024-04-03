import socket
import time
import threading
from functions import send_node, decrypt, load_key, split_packet, details
from logs import sniffing_log

# Initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# Socket
node1 = socket.socket()

# Connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router)  

# ARP table
router_mac = "R1"
node2_ip = "0x2A"
node3_ip = "0x2B"
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
                # ping reply, unicast -> reply to router and node3
                if protocol == "0" and protocol_flag == "P":
                    data = "R" + data
                    ethernet_header = node1_mac + "," + router_mac
                    IP_header = node1_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    node1.send(bytes(packet, "utf-8"))
                elif protocol == "1" and protocol_flag == "K":
                    print("\nEXIT")
                    node1.close()
        
    except Exception as e:
        print("NODE 1 EXITED")


receive_thread = threading.Thread(target=from_router)
receive_thread.start()

# main thread, sending
while True:
    try:
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        
        packet = send_node(1, node2_ip, node3_ip, node1_ip, node1_mac, router_mac, None, ethernet_header, IP_header)
        node1.send(bytes(packet, "utf-8"))
    except Exception as e:
        print("NODE 1 EXITED")

