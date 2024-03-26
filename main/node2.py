import socket
import time
from functions import send_node
from logs import sniffing_log

# Initialise IP and MAC addresses
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

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node2.connect(router)

# arp table
router_mac = "R2"
node3_mac = "N3"
node1_ip = "0x1A"
node3_ip = "0x2B"

arp_mac = {node1_ip : router_mac, node3_ip : node3_mac}

def send_packet():
    print("\nOUTGOING PACKET:")
    ethernet_header = ""
    IP_header = ""

    packet = send_node(2, node1_ip, node3_ip, node2_ip, node2_mac, None, arp_mac, ethernet_header, IP_header)
    node2.send(bytes(packet, "utf-8"))
    node3.send(bytes(packet, "utf-8"))


def receive_packet():
    while True:
        # receive from router
        received_message = node2.recv(1024)
        received_message = received_message.decode("utf-8")
        sorc_mac = received_message[0:2]
        dest_mac = received_message[2:4]
        sorc_ip = received_message[4:8]
        dest_ip =  received_message[8:12]
        protocol = received_message[12:14]
        data_length = received_message[14:15]
        data = received_message[15:]

        # drop packet
        if dest_mac != node2_mac:
            print("\nPACKET DROPPED")

        # Sniffing Attack START
        if dest_ip == node3_ip and sorc_ip == node1_ip and dest_mac!="N2":
            print("\nINTERCEPTED PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)
            sniffing_log(data, sorc_ip, dest_ip, 2)
        elif dest_ip == node1_ip and sorc_ip == node3_ip and dest_mac!="N2":
            print("\nINTERCEPTED PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)
            sniffing_log(data, sorc_ip, dest_ip, 2)
        # Sniffing Attack END
        else:
            print("\nINCOMING PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node3
            if protocol == "0P":
                protocol = "0R"
                ethernet_header = node2_mac + arp_mac[sorc_ip]
                IP_header = node2_ip + sorc_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node2.send(bytes(packet, "utf-8"))
                node3.send(bytes(packet, "utf-8"))
            elif protocol == "1K":
                print("EXIT")
                # raise SystemExit
            # send new packet
            send_packet()
send_packet()
receive_packet()
node2.close()