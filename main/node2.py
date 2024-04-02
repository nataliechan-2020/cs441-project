import socket
import time
import threading
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

def receive_packet():
    while True:
        # receive from router
        received_message = node2.recv(1024)
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
            print("Protocol flag:", protocol_flag)
            print("Data: " + data)
            sniffing_log(data, sorc_ip, dest_ip, 2)
        
        elif dest_ip == node1_ip and sorc_ip == node3_ip and dest_mac!="N2":
            print("\nINTERCEPTED PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Protocol flag:", protocol_flag)
            print("Data: " + data)
            sniffing_log(data, sorc_ip, dest_ip, 2)
        # Sniffing Attack END
       
        else:
            print("\nINCOMING PACKET:")
            print("Source MAC address: {sorc_mac} \nDestination MAC address: {dest_mac}".format(sorc_mac=sorc_mac, dest_mac=dest_mac))
            print("Source IP address: {sorc_ip} \nDestination IP address: {dest_ip}".format(sorc_ip=sorc_ip, dest_ip=dest_ip))
            print("Protocol: " + protocol)
            print("Data length: " + data_length)
            print("Protocol flag:", protocol_flag)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node3
            if protocol == "0" and protocol_flag == "P":
                data = "R" + data
                ethernet_header = node2_mac + "," + arp_mac[sorc_ip]
                IP_header = node2_ip + "," + sorc_ip + "," +  protocol

                payload = IP_header + "," + data_length + "," + data
                payload_length = len(payload) - 4
                packet = ethernet_header + "," + str(payload_length) + "," + payload
                
                print(packet)
                node2.send(bytes(packet, "utf-8"))
                node3.send(bytes(packet, "utf-8"))
            
            elif protocol == "1" and protocol_flag == "K":
                print("EXIT")
                # raise SystemExit
            # send new packet
            # send_packet()

receive_thread = threading.Thread(target=receive_packet)
receive_thread.start()

# def send_packet():
while True:
    print("\nOUTGOING PACKET:")
    ethernet_header = ""
    IP_header = ""

    packet = send_node(2, node1_ip, node3_ip, node2_ip, node2_mac, None, arp_mac, ethernet_header, IP_header)
    node2.send(bytes(packet, "utf-8")) # goes to router
    node3.send(bytes(packet, "utf-8")) # goes to node3 (cos its sent to all nodes in the network)




# send_packet()
# receive_packet()
# node2.close()