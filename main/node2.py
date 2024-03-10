import socket
import time
# import threading

# initialise IP and MAC addresses
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
        print("Node 3 online") 

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node2.connect(router)

# arp table
router_mac = "R2"
node3_mac = "N3"
node1_ip = "0x1A"
node3_ip = "0x2B"

# Start a thread for receiving messages from Node 3
# receive_thread = threading.Thread(target=receive_from_node3)
# receive_thread.daemon = True
# receive_thread.start()

while True:
    # receive from router
    received_message = node2.recv(1024)
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

        # unicast -> reply to router
        ethernet_header = node2_mac + router_mac
        IP_header = node2_ip + source_ip + protocol
        packet = ethernet_header + IP_header + data_length + data
        node2.send(bytes(packet, "utf-8"))  

        # unicast -> reply to node3
        ethernet_header = node2_mac + node3_mac
        IP_header = node2_ip + source_ip + protocol
        packet = ethernet_header + IP_header + data_length + data
        node3.send(bytes(packet, "utf-8")) 

    # send new packet
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
            if(destination_ip == router1_ip or destination_ip == router2_ip or destination_ip == node1_ip or destination_ip == node3_ip): 
                # unicast -> to router
                source_ip = node2_ip
                source_mac = node2_mac
                destination_mac = router_mac
                IP_header = IP_header + source_ip + destination_ip + protocol
                ethernet_header = ethernet_header + source_mac + destination_mac
                packet = ethernet_header + IP_header + str(data_length) + data
                node2.send(bytes(packet, "utf-8"))  

                # unicast -> to node3
                destination_mac = node3_mac
                IP_header = IP_header + source_ip + destination_ip + protocol
                ethernet_header = ethernet_header + source_mac + destination_mac
                packet = ethernet_header + IP_header + str(data_length) + data
                node3.send(bytes(packet, "utf-8"))
            else:
                print("Wrong destination IP inputed")