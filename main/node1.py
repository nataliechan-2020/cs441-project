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

def send_outgoing_packet(node1_mac):
    while True:
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        
        node1.settimeout(15)
        # received_msg = node1.recv(1024)
        try:
            received_msg = node1.recv(1024)
            if received_msg:
                msg = received_msg.decode("utf-8")
                data_size = msg[14:15]

                if int(data_size) > 0:
                    receive_incoming_packet(node1_mac, msg)
                    break
        except TimeoutError:
            # print("Timeout: No data received within the specified time")
            # print("HELLO")
            data = input("Enter data: ")
            data_length = len(data)
            while data_length >= 10:
                print("[ERROR] Data too large")
                data = input("Enter data: ")
                data_length = len(data)

            protocol = input("Enter protocol: ")
            while protocol != "0P" and protocol != "1K":
                print("[ERROR] Wrong protocol inputed")
                protocol = input("Enter protocol: ")

            destination_ip = input("Enter destination IP: ")
            while destination_ip != node2_ip and destination_ip != node3_ip:
                print("[ERROR] Wrong destination IP inputed")
                destination_ip = input("Enter destination IP: ")

            # Send to router
            IP_header = IP_header + node1_ip + destination_ip + protocol
            ethernet_header = ethernet_header + node1_mac + router_mac
            packet = ethernet_header + IP_header + str(data_length) + data
            node1.send(bytes(packet, "utf-8"))

            # Once data is sent, break out of the loop
            break
        break


def receive_incoming_packet(node1_mac, received_msg):
    print(received_msg)
    while True:
        # Receive data from router
        if received_msg== "":
            received_message = node1.recv(1024)
            received_message = received_message.decode("utf-8")
            source_mac = received_message[0:2]
            destination_mac = received_message[2:4]
            source_ip = received_message[4:8]
            destination_ip =  received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]

            print("Received message from router:", received_message)
        else:
            print("hello")
            source_mac = received_msg[0:2]
            destination_mac = received_msg[2:4]
            source_ip = received_msg[4:8]
            destination_ip =  received_msg[8:12]
            protocol = received_msg[12:14]
            data_length = received_msg[14:15]
            data = received_msg[15:]

        if destination_mac != node1_mac:
            print("\nPACKET DROPPED")
   
        else:
            print("\nINCOMING PACKET:")
            print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
            print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node3
            if protocol == "0P":
                protocol = "0R"
                ethernet_header = node1_mac + router_mac
                IP_header = node1_ip + source_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node1.send(bytes(packet, "utf-8"))
                node1.send(bytes(packet, "utf-8"))


            send_outgoing_packet(node1_mac)  # After receiving, allow sending another packet

send_outgoing_packet(node1_mac)  # Initial sending
receive_incoming_packet(node1_mac, "")

# Close the connection
node1.close()
