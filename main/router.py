import socket

# initialise IP and MAC addresses
router1_ip = "0x11"
router1_mac = "R1"
router2_ip = "0x21"
router2_mac = "R2"

# socket (network 1)
router1 = socket.socket()
router1.bind(("localhost", 1200))

# socket (network 2)
router2 = socket.socket()
router2.bind(("localhost", 2200))

# from network 1
router1.listen(2)
node1 = None

while (node1 == None):
    if (node1 == None):
        node1, address = router1.accept()

# from network 2
router2.listen(4)
node2 = None
node3 = None

while (node2 == None or node3 == None):
    node, address = router2.accept()
    if (node3 == None):
        node3 = node
    elif (node2 == None):
        node2 = node
 
print("CONNECTED")

# arp table
node1_mac = "N1"
node2_mac = "N2"
node3_mac = "N3"
node1_ip = "0x1A"
node2_ip = "0x2A"
node3_ip = "0x2B"

arp_socket = {node1_mac : node1, node2_mac : node2, node3_mac : node3}
arp_mac = {node1_ip : node1_mac, node2_ip : node2_mac, node3_ip : node3_mac}

while True:
    # receive from node1 
    received_message = node1.recv(1024)
    received_message = received_message.decode("utf-8")
    
    source_mac = received_message[0:2]
    destination_mac = received_message[2:4]
    source_ip = received_message[4:8]
    destination_ip =  received_message[8:12]
    protocol = received_message[12:14]
    data_length = received_message[14:15]
    data = received_message[15:]
    
    print("\nINCOMING PACKET - NODE 1:")
    print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("Protocol: " + protocol)
    print("Data length: " + data_length)
    print("Data: " + data)

    # unicast -> forward packet to node2
    IP_header = source_ip + destination_ip + protocol
    ethernet_header = router2_mac + arp_mac[destination_ip]
    packet = ethernet_header + IP_header + data_length + data
    destination_socket = arp_socket[node2_mac]
    destination_socket.send(bytes(packet, "utf-8"))

    # unicast -> forward packet to node3
    destination_socket = arp_socket[node3_mac]
    destination_socket.send(bytes(packet, "utf-8"))

    # receive from node2
    received_message = node2.recv(1024)
    received_message =  received_message.decode("utf-8")
    
    source_mac = received_message[0:2]
    destination_mac = received_message[2:4]
    source_ip = received_message[4:8]
    destination_ip =  received_message[8:12]
    protocol = received_message[12:14]
    data_length = received_message[14:15]
    data = received_message[15:]
    
    # drop packet
    if destination_mac != router2_mac:
        print("\nPACKET DROPPED")
    else:
        print("\nINCOMING PACKET - NODE 2:")
        print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
        print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
        print("Protocol: " + protocol)
        print("Data length: " + data_length)
        print("Data: " + data)
    
        # forward packet to node1
        if destination_ip == node1_ip: 
            ethernet_header = router1_mac + node1_mac
            IP_header = source_ip + destination_ip + protocol
            packet = ethernet_header + IP_header + data_length + data
            destination_socket = arp_socket[node1_mac]
            destination_socket.send(bytes(packet, "utf-8"))

    # receive from node3
    received_message = node3.recv(1024)
    received_message =  received_message.decode("utf-8")
    
    source_mac = received_message[0:2]
    destination_mac = received_message[2:4]
    source_ip = received_message[4:8]
    destination_ip =  received_message[8:12]
    protocol = received_message[12:14]
    data_length = received_message[14:15]
    data = received_message[15:]

    # drop packet if dest IP != node1_ip
    if destination_ip != node1_ip: 
        print("\nPACKET DROPPED")
    else:
        print("\nINCOMING PACKET - NODE 3:")
        print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
        print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
        print("Protocol: " + protocol)
        print("Data length: " + data_length)
        print("Data: " + data)
            
        # forward packet to node1
        if destination_ip == node1_ip: 
            ethernet_header = router1_mac + node1_mac
            IP_header = source_ip + destination_ip + protocol
            packet = ethernet_header + IP_header + data_length + data
            destination_socket = arp_socket[node1_mac]
            destination_socket.send(bytes(packet, "utf-8")) 