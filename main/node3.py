import socket
import time
from functions import send_node
from logs import log_ip

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

blocked_ips = []
# blocked_protocol = []
ips = ""
# protocols = ""
for i in blocked_ips:
    ips+= ", "  + i
# for i in blocked_protocol:
#     protocols+= ", "  + i

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


def main ():
    option = input("Choose 1, 2 or 3: "  + 
                   "\n1) Add Blocked IP to Firewall" + 
                   "\n2) Remove Blocked IP from Firewall" +
                    "\n3) Send/Receive Packet: \n")
    while int(option) not in [1,2,3]:
        option = input("Choose 1, 2 or 3:" + 
                       "\n1) Add Blocked IP to Firewall" + 
                       "\n2) Remove Blocked IP from Firewall" +
                       "\n3) Send/Receive Packet: \n")
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


def receive_packet():      

    while True:
        node3.settimeout(1)
        try:
            # receive from router
            received_message = node3.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac = received_message[0:2]
            dest_mac = received_message[2:4]
            sorc_ip = received_message[4:8]
            dest_ip =  received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]
        except TimeoutError:
            received_message = intra3.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac = received_message[0:2]
            dest_mac = received_message[2:4]
            sorc_ip = received_message[4:8]
            dest_ip =  received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]

        if sorc_ip in blocked_ips and sorc_ip!=node3_ip:
            print("FIREWALL BLOCKED")
            continue

        # drop packet
        if dest_mac != node3_mac and sorc_ip==node3_ip:
            print("\nPACKET DROPPED")
        else:
            print(sorc_ip)
            print("\nINCOMING PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node2
            if protocol == "0P":
                protocol = "0R"
                ethernet_header = node3_mac + arp_mac[sorc_ip]
                IP_header = node3_ip + sorc_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node3.send(bytes(packet, "utf-8"))
                intra3.send(bytes(packet, "utf-8")) 
    
        # receive from node2
        received_message = intra3.recv(1024)
        received_message = received_message.decode("utf-8")

        sorc_mac = received_message[0:2]
        dest_mac = received_message[2:4]
        sorc_ip = received_message[4:8]
        dest_ip =  received_message[8:12]
        protocol = received_message[12:14]
        data_length = received_message[14:15]
        data = received_message[15:]

        # drop packet
        if dest_mac != node3_mac and sorc_ip==node3_ip:
            print("\nPACKET DROPPED")
        else:
            print("\nINCOMING PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node2
            if protocol == "0P":
                protocol = "0R"
                ethernet_header = node3_mac + arp_mac[sorc_ip]
                IP_header = node3_ip + sorc_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node3.send(bytes(packet, "utf-8"))
                intra3.send(bytes(packet, "utf-8")) 

        send_packet() 

main()
node3.close()