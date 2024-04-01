import socket
import time
from functions import send_node
from logs import log_ip, log_protocol, sniffing_log, blocked_data

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

arp_mac = {node1_ip : router_mac, node2_ip : node2_mac, node3_ip: node3_mac}

blocked_ips = []
blocked_protocol = []
ips = ""
protocols = ""
for i in blocked_ips:
    ips+= ", "  + i
for i in blocked_protocol:
    protocols+= ", "  + i

log_ip(ips, "initial")

def add_blocked_ip(ip):
    blocked_ips.append(ip)
    print("ADDED")
    print(blocked_ips)
    log_ip(ip, "add")
    main()

def remove_blocked_ip(ip):
    if ip in blocked_ips:
        blocked_ips.remove(ip)
        log_ip(ip, "remove")
        print("REMOVED")
        print(blocked_ips)
    else:
        print("NOT FOUND")
        print(blocked_ips)
    main()

def add_blocked_protocol(protocol):
    blocked_protocol.append(protocol)
    print("ADDED")
    print(blocked_protocol)
    log_protocol(protocol, "add")
    main()

def remove_blocked_protocol(protocol):
    if protocol in blocked_protocol:
        blocked_protocol.remove(protocol)
        log_protocol(protocol, "remove")
        print("REMOVED")
        print(blocked_protocol)
    else:
        print("NOT FOUND")
        print(blocked_protocol)
    main()


def main ():
    option = input("Choose 1, 2, 3, 4 or 5: "  + 
                   "\n1) Add Blocked IP to Firewall" + 
                   "\n2) Remove Blocked IP from Firewall" +
                   "\n3) Add Blocked Protocol to Firewall" + 
                   "\n4) Remove Blocked Protocol From Firewall" +
                    "\n5) Send/Receive Packet: \n")
    while int(option) not in [1,2,3, 4, 5]:
        option = input("Choose 1, 2, 3, 4 or 5:" + 
                       "\n1) Add Blocked IP to Firewall" + 
                       "\n2) Remove Blocked IP from Firewall" +
                       "\n3) Add Blocked Protocol to Firewall" + 
                        "\n4) Remove Blocked Protocol From Firewall" + 
                        "\n5) Send/Receive Packet: \n")
    option = int(option)

    if option == 1:
        ip = input("Enter IP Address: ")
        while ip != node1_ip and ip != node2_ip:
            ip = input("Enter IP Address:")
        add_blocked_ip(ip)
        
    elif option == 2:
        ip = input("Enter IP Address: ")
        while ip != node1_ip and ip != node2_ip:
            ip = input("Enter IP Address:")
        remove_blocked_ip(ip)
    elif option == 3:
        protocol = input("Enter Protocol: ")
        while protocol != "0" and protocol!="1":
            protocol = input("Enter Protocol:")
        add_blocked_protocol(protocol)
    elif option == 4:
        protocol = input("Enter Protocol: ")
        while protocol != "0" and protocol!="1":
            protocol = input("Enter Protocol:")
        remove_blocked_protocol(protocol)

    else:
        send_packet()
        receive_packet()   


def send_packet():
    print("\nOUTGOING PACKET:")
    ethernet_header = ""
    IP_header = ""
    packet = send_node(3, node1_ip, node2_ip, node3_ip, node3_mac, None, arp_mac, ethernet_header, IP_header)
    node3.send(bytes(packet, "utf-8"))
    intra3.send(bytes(packet, "utf-8"))
    receive_packet()


def receive_packet():      
    while True:
        node3.settimeout(1)
        try:
            # receive from router
            received_message = node3.recv(1024)
            received_message = received_message.decode("utf-8")
            received_message = received_message.split(',')

            sorc_mac = received_message[0]
            dest_mac = received_message[1]
            payload_length = received_message[2]
            sorc_ip = received_message[3]
            dest_ip =  received_message[4]
            protocol = received_message[5]
            data_length = received_message[6]
            data = received_message[7]
        except TimeoutError:
            received_message = intra3.recv(1024)
            received_message = received_message.decode("utf-8")
            received_message = received_message.split(',')

            sorc_mac = received_message[0]
            dest_mac = received_message[1]
            payload_length = received_message[2]
            sorc_ip = received_message[3]
            dest_ip =  received_message[4]
            protocol = received_message[5]
            data_length = received_message[6]
            data = received_message[7]

        protocol_flag = data[0]
        data = data[1:]

        if sorc_ip in blocked_ips and sorc_ip!=node3_ip:
            print("FIREWALL BLOCKED")
            blocked_data(sorc_ip)
            continue

        elif protocol in blocked_protocol and sorc_ip!=node3_ip:
            print("FIREWALL BLOCKED")
            blocked_data(protocol)
            continue
        
        # drop packet
        elif dest_mac != node3_mac and sorc_ip!=node3_ip:
            print("\nPACKET DROPPED")
        elif dest_ip == node2_ip and sorc_ip ==node1_ip:
            sniffing_log(data, sorc_ip, dest_ip, 3)
        elif dest_ip == node1_ip and sorc_ip == node2_ip:
            sniffing_log(data, sorc_ip, dest_ip, 3)

        else:
            print(sorc_ip)
            if sorc_ip =="0x2B" or dest_ip == "0x2B":
                print("\nINCOMING PACKET:")
                print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
                print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
                print("Protocol: " + protocol)
                print("Data length: " + data_length)
                print("Protocol flag:", protocol_flag)
                print("Data: " + data)

            # ping reply, unicast -> reply to router and node2
            if protocol == "0" and protocol_flag == "P":
                data = "R" + data
                ethernet_header = node3_mac + "," + arp_mac[sorc_ip]
                IP_header = node3_ip + "," + sorc_ip + "," + protocol

                payload = IP_header + "," + data_length + "," + data
                payload_length = len(payload) - 4
                packet = ethernet_header + "," + str(payload_length) + "," + payload
                node3.send(bytes(packet, "utf-8"))
                intra3.send(bytes(packet, "utf-8")) 

            elif protocol == "1" and protocol_flag == "K":
                print("EXIT")
            send_packet() 
       
        # receive from node2
        received_message = intra3.recv(1024)
        received_message = received_message.decode("utf-8")
        received_message = received_message.split(',')

        sorc_mac = received_message[0]
        dest_mac = received_message[1]
        payload_length = received_message[2]
        sorc_ip = received_message[3]
        dest_ip =  received_message[4]
        protocol = received_message[5]
        data_length = received_message[6]
        data = received_message[7]

        protocol_flag = data[0]
        data = data[1:]

        print("----")
        if sorc_ip in blocked_ips and sorc_ip!=node3_ip:
            print("FIREWALL BLOCKED")
            continue
        
        elif protocol in blocked_protocol and sorc_ip!=node3_ip:
            print("FIREWALL BLOCKED")
            continue
        # drop packet
        elif dest_mac != node3_mac and sorc_ip!=node3_ip:
            print("\nPACKET DROPPED")
        else:
            if sorc_ip =="0x2B" or dest_ip == "0x2B":
                print("\nINCOMING PACKET:")
                print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
                print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
                print("Protocol: " + protocol)
                print("Data length: " + data_length)
                print("Protocol flag:", protocol_flag)
                print("Data: " + data)

            # ping reply, unicast -> reply to router and node2
            if protocol == "0" and protocol_flag == "P":
                data = "R" + data
                ethernet_header = node3_mac + "," + arp_mac[sorc_ip]
                IP_header = node3_ip + "," + sorc_ip + "," + protocol

                payload = IP_header + "," + data_length + "," + data
                payload_length = len(payload) - 4
                packet = ethernet_header + "," + str(payload_length) + "," + payload

                node3.send(bytes(packet, "utf-8"))
                intra3.send(bytes(packet, "utf-8")) 
            elif protocol == "1" and protocol_flag == "K":
                print("EXIT")
            send_packet() 

main()
node3.close()