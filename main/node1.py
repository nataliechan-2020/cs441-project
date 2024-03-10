import socket
import time

# initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# socket
node1 = socket.socket()

# connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router) # router to accept connection request from node

# arp table
router_mac = "R1"
node2_ip = "0x2A"
node3_ip = "0x2B"

while True:
    # send new packet to router
    print("\nOUTGOING PACKET:")
    ethernet_header = ""
    IP_header = ""
    data = input("Enter data: ")
    data_length = len(data)

    if data_length >= 10:
        print("Data too large")
    else:
        protocol = input("Enter protocol: ")
        if protocol != "0P" and protocol != "1K":
            print("Wrong protocol inputed")
        else:
            destination_ip = input("Enter destination IP: ")
            if(destination_ip == node2_ip or destination_ip == node3_ip): 
                source_ip = node1_ip
                source_mac = node1_mac
                destination_mac = router_mac

                IP_header = IP_header + source_ip + destination_ip + protocol
                ethernet_header = ethernet_header + source_mac + destination_mac
                packet = ethernet_header + IP_header + str(data_length) + data
                node1.send(bytes(packet, "utf-8"))  
            else:
                print("Wrong destination IP inputed")

    # receive data from router
    received_message = node1.recv(1024)
    received_message = received_message.decode("utf-8")

    source_mac = received_message[0:2]
    destination_mac = received_message[2:4]
    source_ip = received_message[4:8]
    destination_ip =  received_message[8:12]
    protocol = received_message[12:14]
    data_length = received_message[14:15]
    data = received_message[15:]

    print("\nINCOMING PACKET:")
    print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("Protocol: " + protocol)
    print("Data length: " + data_length)
    print("Data: " + data)

    # ping reply
    if protocol == "0P":
        protocol = "0R"
        ethernet_header = node1_mac + router_mac
        IP_header = node1_ip + source_ip + protocol
        packet = ethernet_header + IP_header + data_length + data
        node1.send(bytes(packet, "utf-8"))  
