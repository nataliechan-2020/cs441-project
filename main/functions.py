def receive_router (received_message, node, compare):
    sorc_mac = received_message[0:2]
    dest_mac = received_message[2:4]
    sorc_ip = received_message[4:8]
    dest_ip = received_message[8:12]
    protocol = received_message[12:14]
    data_length = received_message[14:15]
    data = received_message[15:]
    
    packet_dropped = False
    if node == 2:
        if dest_mac != compare:
            print("\n PACKET DROPPED")
            packet_dropped = True
    elif node ==3:
        if dest_ip != compare:
            print("\n PACKET DROPPED")
            packet_dropped = True 
    if packet_dropped == False:
        print("\nINCOMING PACKET {node}:".format(node=node))
        print("Source MAC address:", sorc_mac, "\nDestination MAC address:", dest_mac)
        print("Source IP address:", sorc_ip, "\nDestination IP address:", dest_ip)
        print("Protocol:", protocol)
        print("Data length:", data_length)
        print("Data:", data)
    
    return sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, data, packet_dropped

def send_node(node, ip1, ip2, current_ip, current_mac, router_mac, arp_mac, ethernet_header, IP_header):
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

    dest_ip = input("Enter destination IP: ")
    while dest_ip != ip1 and dest_ip != ip2:
        print("[ERROR] Wrong destination IP inputed")
        dest_ip = input("Enter destination IP: ")

    IP_header = IP_header + current_ip + dest_ip + protocol
    if node == 1:
        ethernet_header = ethernet_header + current_mac + router_mac
    else:
        ethernet_header = ethernet_header + current_mac + arp_mac[dest_ip]
    packet = ethernet_header + IP_header + str(data_length) + data

    return packet