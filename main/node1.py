import socket
import time

# Initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# Socket
node1 = socket.socket()

# Connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router)  # router to accept connection request from node

# ARP table
router_mac = "R1"
node2_ip = "0x2A"
node3_ip = "0x2B"

# Flag to control outgoing packet sending
allow_outgoing_packet = True

while True:
    if allow_outgoing_packet:
        # Send new packet to router
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        data = input("Enter data: ")
        data_length = len(data)

        while data_length >= 10:
            print("[ERROR] Data too large")
            data = input("Enter data: ")
            data_length = len(data)

        protocol = input("Enter protocol: ")
        while protocol not in ["0P", "1K"]:
            print("[ERROR] Wrong protocol entered")
            protocol = input("Enter protocol: ")

        destination_ip = input("Enter destination IP: ")
        while destination_ip != node2_ip and destination_ip != node3_ip:
            print("[ERROR] Wrong destination IP entered")
            destination_ip = input("Enter destination IP: ")

        # Send to router
        IP_header = IP_header + node1_ip + destination_ip + protocol
        ethernet_header = ethernet_header + node1_mac + router_mac
        packet = ethernet_header + IP_header + str(data_length) + data
        node1.send(bytes(packet, "utf-8"))

        # Set flag to disallow sending outgoing packet until a response is received
        allow_outgoing_packet = False

        # Receive data from router
        received_message = node1.recv(1024)
        received_message = received_message.decode("utf-8")

        source_mac = received_message[0:2]
        destination_mac = received_message[2:4]
        source_ip = received_message[4:8]
        destination_ip = received_message[8:12]
        protocol = received_message[12:14]
        data_length = received_message[14:15]
        data = received_message[15:]

        print("\nINCOMING PACKET:")
        print("Source MAC address:", source_mac)
        print("Destination MAC address:", destination_mac)
        print("Source IP address:", source_ip)
        print("Destination IP address:", destination_ip)
        print("Protocol:", protocol)
        print("Data length:", data_length)
        print("Data:", data)

        # Set flag to allow sending outgoing packet after receiving incoming packet
        allow_outgoing_packet = True
