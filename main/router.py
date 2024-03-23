import socket
import threading
# Initialise IP and MAC addresses
router1_ip = "0x11"
router1_mac = "R1"
router2_ip = "0x21"
router2_mac = "R2"

def receive_from_node1(node1, arp_socket, arp_mac, router2_mac):
    while True:
        try:
            # Receive from node1
            received_message = node1.recv(1024).decode("utf-8")
            print("NODE 1 TEST")
            print(received_message)
            
            sorc_mac = received_message[0:2]
            dest_mac = received_message[2:4]
            sorc_ip = received_message[4:8]
            dest_ip = received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]
            
            print("\nINCOMING PACKET - NODE 1:")
            print("Source MAC address:", sorc_mac, "\nDestination MAC address:", dest_mac)
            print("Source IP address:", sorc_ip, "\nDestination IP address:", dest_ip)
            print("Protocol:", protocol)
            print("Data length:", data_length)
            print("Data:", data)

            # Forward packet to node2
            IP_header = sorc_ip + dest_ip + protocol
            ethernet_header = router2_mac + arp_mac[dest_ip]
            packet = ethernet_header + IP_header + data_length + data
            dest = arp_socket[node2_mac]
            dest.send(bytes(packet, "utf-8"))

            # Forward packet to node3
            dest = arp_socket[node3_mac]
            dest.send(bytes(packet, "utf-8"))

        except socket.error as e:
            print("Socket error:", e)

def receive_from_node2(node2, arp_socket, arp_mac, router1_mac):
    while True:
        try:
            # Receive from node2
            received_message = node2.recv(1024).decode("utf-8")
            print("NODE 2 TEST")
            print(received_message)
            
            sorc_mac = received_message[0:2]
            dest_mac = received_message[2:4]
            sorc_ip = received_message[4:8]
            dest_ip = received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]

            if dest_mac != router2_mac:
                print("\n PACKET DROPPED")
            else:
                print("\nINCOMING PACKET - NODE 2:")
                print("Source MAC address:", sorc_mac, "\nDestination MAC address:", dest_mac)
                print("Source IP address:", sorc_ip, "\nDestination IP address:", dest_ip)
                print("Protocol:", protocol)
                print("Data length:", data_length)
                print("Data:", data)

                # Send packet back to node1
                IP_header = sorc_ip + dest_ip + protocol
                ethernet_header = router1_mac + arp_mac[dest_ip]
                packet = ethernet_header + IP_header + data_length + data
                dest = arp_socket[node1_mac]
                dest.send(bytes(packet, "utf-8"))
        except socket.error as e:
            print("Socket error:", e)

def receive_from_node3(node3, arp_socket, node1_ip, router1_mac):
    while True:
        try:
            # Receive from node3
            received_message = node3.recv(1024).decode("utf-8")
            
            sorc_mac = received_message[0:2]
            dest_mac = received_message[2:4]
            sorc_ip = received_message[4:8]
            dest_ip = received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]

            # drop packet if dest IP != node1_ip
            if dest_ip != node1_ip: 
                print("\nPACKET DROPPED")
            else:
                print("\nINCOMING PACKET - NODE 3:")
                print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
                print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
                print("Protocol: " + protocol)
                print("Data length: " + data_length)
                print("Data: " + data)

            
                ethernet_header = router1_mac + node1_mac
                IP_header = sorc_ip + dest_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                dest = arp_socket[node1_mac]
                dest.send(bytes(packet, "utf-8"))
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

# ARP table
node1_mac = "N1"
node2_mac = "N2"
node3_mac = "N3"
node1_ip = "0x1A"
node2_ip = "0x2A"
node3_ip = "0x2B"

arp_socket = {node1_mac: node1, node2_mac: node2, node3_mac: node3}
arp_mac = {node1_ip: node1_mac, node2_ip: node2_mac, node3_ip: node3_mac}

receive_node1_thread = threading.Thread(target=receive_from_node1, args=(node1, arp_socket, arp_mac, router2_mac))
receive_node1_thread.start()

receive_node2_thread = threading.Thread(target=receive_from_node2, args=(node2, arp_socket, arp_mac, router1_mac))
receive_node2_thread.start()

receive_node3_thread = threading.Thread(target=receive_from_node3, args=(node3, arp_socket, node1_ip, router1_mac))
receive_node3_thread.start()
