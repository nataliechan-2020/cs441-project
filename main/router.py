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
        print("Node 1 online") 

# from network 2
router2.listen(4)
node2 = None
node3 = None

while (node2 == None or node3 == None):
    node, address = router2.accept()
    if (node2 == None):
        node2 = node
        print("Node 2 online")
    elif (node3 == None):
        node3 = node
        print("Node 3 online")

# arp table
node1_mac = "N1"
node2_mac = "N2"
node3_mac = "N3"
node1_ip = "0x1A"
node2_ip = "0x2A"
node3_ip = "0x2B"

arp_socket = {node1_mac : node1, node2_mac : node2, node3_mac : node3}

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
    ethernet_header = router2_mac + node2_mac
    packet = ethernet_header + IP_header + data_length + data
    destination_socket = arp_socket[node2_mac]
    destination_socket.send(bytes(packet, "utf-8"))

    # unicast -> forward packet to node3
    ethernet_header = router2_mac + node3_mac
    packet = ethernet_header + IP_header + data_length + data
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
    
    print("\nINCOMING PACKET - NODE 2:")
    print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("Protocol: " + protocol)
    print("Data length: " + data_length)
    print("Data: " + data)

    # drop packet if dest IP != node1_ip
    if destination_ip != node1_ip:
        print("Packet dropped:")
        print("\nDestination IP address: {destination_ip}".format(destination_ip=destination_ip))
    
    # forward packet to node1
    elif destination_ip == node1_ip: 
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
    
    print("\nINCOMING PACKET - NODE 3:")
    print("Source MAC address: {source_mac} \nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("Source IP address: {source_ip} \nDestination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("Protocol: " + protocol)
    print("Data length: " + data_length)
    print("Data: " + data)

    # drop packet if dest IP != node1_ip
    if destination_ip != node1_ip: 
        print("Packet dropped:")
        print("\nDestination IP address: {destination_ip}".format(destination_ip=destination_ip))
    
    # forward packet to node1
    elif destination_ip == node1_ip: 
        ethernet_header = router1_mac + node1_mac
        IP_header = source_ip + destination_ip + protocol
        packet = ethernet_header + IP_header + data_length + data
        destination_socket = arp_socket[node1_mac]
        destination_socket.send(bytes(packet, "utf-8"))