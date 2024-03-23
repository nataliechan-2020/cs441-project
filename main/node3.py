import socket
import threading
import time

# initialise IP and MAC addresses
node3_ip = "0x2B"
node3_mac = "N3"

# sockets
node3 = socket.socket()
intra3 = socket.socket()

# connect to router, node2
time.sleep(1)
router = ("localhost", 2200)
node3.connect(router) 

time.sleep(1)
node2 = ("localhost", 2000)
intra3.connect(node2) 

# arp table
router_mac = "R2"
node2_mac = "N2"
node1_ip = "0x1A"
node2_ip = "0x2A"

arp_mac = {node1_ip : router_mac, node2_ip : node2_mac}


def send_outgoing_packet():
    # send new packet
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
    while protocol != "0P" and protocol != "1K":
        print("[ERROR] Wrong protocol inputed")
        protocol = input("Enter protocol: ")

    destination_ip = input("Enter destination IP: ")
    while destination_ip != node1_ip and destination_ip != node2_ip:
        print("[ERROR] Wrong destination IP inputed")
        destination_ip = input("Enter destination IP: ")

    # unicast -> to router and node2
    IP_header = IP_header + node3_ip + destination_ip + protocol
    ethernet_header = ethernet_header + node3_mac + arp_mac[destination_ip]
    packet = ethernet_header + IP_header + str(data_length) + data
    node3.send(bytes(packet, "utf-8"))
    intra3.send(bytes(packet, "utf-8"))


def receive_incoming_packet():   
    while True:
        # receive from router
        received_message = node3.recv(1024)
        received_message = received_message.decode("utf-8")

        source_mac = received_message[0:2]
        destination_mac = received_message[2:4]
        source_ip = received_message[4:8]
        destination_ip =  received_message[8:12]
        protocol = received_message[12:14]
        data_length = received_message[14:15]
        data = received_message[15:]

        # drop packet
        if destination_mac != node3_mac:
            print("\nPACKET DROPPED")
        else:
            print("\nINCOMING PACKET:")
            print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
            print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node2
            if protocol == "0P":
                protocol = "0R"
                ethernet_header = node3_mac + arp_mac[source_ip]
                IP_header = node3_ip + source_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node3.send(bytes(packet, "utf-8"))
                intra3.send(bytes(packet, "utf-8")) 

        # receive from node2
        received_message = intra3.recv(1024)
        received_message = received_message.decode("utf-8")

        source_mac = received_message[0:2]
        destination_mac = received_message[2:4]
        source_ip = received_message[4:8]
        destination_ip =  received_message[8:12]
        protocol = received_message[12:14]
        data_length = received_message[14:15]
        data = received_message[15:]

        # drop packet
        if destination_mac != node3_mac:
            print("\nPACKET DROPPED")
        else:
            print("\nINCOMING PACKET:")
            print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
            print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node2
            if protocol == "0P":
                protocol = "0R"
                ethernet_header = node3_mac + arp_mac[source_ip]
                IP_header = node3_ip + source_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node3.send(bytes(packet, "utf-8"))
                intra3.send(bytes(packet, "utf-8")) 

        send_outgoing_packet()  

send_outgoing_packet()
receive_incoming_packet()