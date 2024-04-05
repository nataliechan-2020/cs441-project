import socket
import time
import threading
from functions import send_node, encrypt, decrypt, load_key, split_packet, details, settings
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
node4_ip = "0x1B"

# key = str.encode("1234567812345678")
# key = get_random_bytes(16) 
key = load_key()

# next hop
arp_mac = {node1_ip : router_mac, node2_ip : node2_mac, node4_ip: router_mac}

# firewall
blocked_ips = []
blocked_protocol = []
ips = ""
protocols = ""
for i in blocked_ips:
    ips+= ", "  + i
for i in blocked_protocol:
    protocols+= ", "  + i

def add_blocked_ip(ip):
    blocked_ips.append(ip)
    print("ADDED")
    print(blocked_ips)
    log_ip(ip, "add")
    # main()

def remove_blocked_ip(ip):
    if ip in blocked_ips:
        blocked_ips.remove(ip)
        log_ip(ip, "remove")
        print("REMOVED")
        print(blocked_ips)
    else:
        print("NOT FOUND")
        print(blocked_ips)
    # main()

def add_blocked_protocol(protocol):
    blocked_protocol.append(protocol)
    print("ADDED")
    print(blocked_protocol)
    log_protocol(protocol, "add")
    # main()

def remove_blocked_protocol(protocol):
    if protocol in blocked_protocol:
        blocked_protocol.remove(protocol)
        log_protocol(protocol, "remove")
        print("REMOVED")
        print(blocked_protocol)
    else:
        print("NOT FOUND")
        print(blocked_protocol)
    # main()

# receive from router
def from_router():
    try:
        while True:
            received_message = node3.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data = split_packet(received_message)
            protocol_flag = data[0]
            data = data[1:]

            try:
                # data = data.decode()
                data = decrypt(data, key)
                data = data.decode('utf-8')
            except Exception as e:
                print(data)

            # firewall
            if sorc_ip in blocked_ips and sorc_ip!=node3_ip:
                print("FIREWALL BLOCKED")
                blocked_data(sorc_ip)
                continue
            elif protocol in blocked_protocol and sorc_ip!=node3_ip:
                print("FIREWALL BLOCKED")
                blocked_data(protocol)
                continue
            
            # drop packet
            # elif dest_mac != node3_mac and sorc_ip!=node3_ip:
            elif dest_mac != node3_mac and dest_ip!=node3_ip:
                print("\nPACKET DROPPED")

            # sniff
            elif dest_ip == node2_ip and sorc_ip ==node1_ip:
                sniffing_log(data, sorc_ip, dest_ip, 3)
            elif dest_ip == node1_ip and sorc_ip == node2_ip:
                sniffing_log(data, sorc_ip, dest_ip, 3)

            else:
                # print(sorc_ip)
                # if sorc_ip =="0x2B" or dest_ip == "0x2B":
                if dest_ip == node3_ip:
                    print("\nINCOMING PACKET:")
                    details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()

                    ethernet_header = node3_mac + "," + arp_mac[sorc_ip]
                    IP_header = node3_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    node3.send(bytes(packet, "utf-8")) # to router
                    try:
                        intra3.send(bytes(packet, "utf-8"))  # to node2, if connected
                    except Exception as e:
                        print("NODE 2 NOT FOUND")

                elif protocol == "1" and protocol_flag == "K":
                    print("EXIT")
                    node3.close()
                    try:
                        intra3.close()
                    except Exception as e:
                        print("NODE 2 NOT FOUND")
    
    except Exception as e:
        print("NODE 3 EXITED")
       
# receive from node2
def from_node2():
    try:
        while True:
            received_message = intra3.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data = split_packet(received_message)
            protocol_flag = data[0]
            data = data[1:]

            try:
                # data = data.decode()
                data = decrypt(data, key)
                data = data.decode('utf-8')
            except Exception as e:
                print(data)

            # firewall
            if sorc_ip in blocked_ips and sorc_ip!=node3_ip:
                print("FIREWALL BLOCKED")
                blocked_data(sorc_ip)
                continue
            elif protocol in blocked_protocol and sorc_ip!=node3_ip:
                print("FIREWALL BLOCKED")
                blocked_data(protocol)
                continue
            
            # drop packet
            # elif dest_mac != node3_mac and sorc_ip!=node3_ip:
            elif dest_mac != node3_mac and dest_ip!=node3_ip:
                print("\nPACKET DROPPED")

            # sniff
            elif dest_ip == node2_ip and sorc_ip ==node1_ip:
                sniffing_log(data, sorc_ip, dest_ip, 3)
            elif dest_ip == node1_ip and sorc_ip == node2_ip:
                sniffing_log(data, sorc_ip, dest_ip, 3)

            else:
                # if sorc_ip =="0x2B" or dest_ip == "0x2B":
                if dest_ip == node3_ip:
                    print("\nINCOMING PACKET:")
                    details(sorc_mac, sorc_ip, dest_mac, dest_ip, protocol, data_length, protocol_flag, data)
                if protocol == "0" and protocol_flag == "P":
                    protocol_flag = "R"
                    data = data.encode()
                    data = encrypt(data, key)
                    data = data.decode()
                    
                    ethernet_header = node3_mac + "," + arp_mac[sorc_ip]
                    IP_header = node3_ip + "," + sorc_ip + "," + protocol

                    payload = IP_header + "," + data_length + "," + protocol_flag + data
                    payload_length = len(payload) - 4
                    packet = ethernet_header + "," + str(payload_length) + "," + payload
                    
                    intra3.send(bytes(packet, "utf-8"))
                    node3.send(bytes(packet, "utf-8"))

                elif protocol == "1" and protocol_flag == "K":
                    print("EXIT")
                    node3.close()
                    intra3.close()
    
    except Exception as e:
        print("NODE 2 NOT FOUND")

# logs
log_ip(ips, "initial")

receive_from_router_thread = threading.Thread(target=from_router)
receive_from_node2_thread = threading.Thread(target=from_node2)
receive_from_router_thread.start()
receive_from_node2_thread.start()

while True:
    try:
        option = settings()
        while int(option) not in [1,2,3,4,5]:
            option = settings()
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
            print("\nOUTGOING PACKET:")
            ethernet_header = ""
            IP_header = ""
            packet = send_node(3, node1_ip, node2_ip, node4_ip, node3_ip, node3_mac, arp_mac, ethernet_header, IP_header)
            node3.send(bytes(packet, "utf-8"))
            try:
                intra3.send(bytes(packet, "utf-8"))
            except Exception as e:
                print("NODE 2 NOT FOUND")
    except Exception as e:
        print("NODE 3 EXITED")