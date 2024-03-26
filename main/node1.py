import socket
import time
from functions import send_node
from logs import sniffing_log

# Initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# Socket
node1 = socket.socket()

# Connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router)  

# ARP table
router_mac = "R1"
node2_ip = "0x2A"
node3_ip = "0x2B"

def send_packet():
    while True:
        print("\nOUTGOING PACKET:")
        ethernet_header = ""
        IP_header = ""
        
        node1.settimeout(15)
        try:
            # Check if got receive any message
            received_message = node1.recv(1024)
            if received_message:
                received_message = received_message.decode("utf-8")
                data_size = received_message[14:15]

                if int(data_size) > 0:
                    receive_packet(received_message)
                    break
        except TimeoutError:
            packet = send_node(1, node2_ip, node3_ip, node1_ip, node1_mac, router_mac, None, ethernet_header, IP_header)
            node1.send(bytes(packet, "utf-8"))
            
            break
        break


def receive_packet(received_msg):
    print(received_msg)
    while True:
        # Receive data from router
        if received_msg== "":
            received_message = node1.recv(1024)
            received_message = received_message.decode("utf-8")
            sorc_mac = received_message[0:2]
            dest_mac = received_message[2:4]
            sorc_ip = received_message[4:8]
            dest_ip =  received_message[8:12]
            protocol = received_message[12:14]
            data_length = received_message[14:15]
            data = received_message[15:]
        else:
            sorc_mac = received_msg[0:2]
            dest_mac = received_msg[2:4]
            sorc_ip = received_msg[4:8]
            dest_ip =  received_msg[8:12]
            protocol = received_msg[12:14]
            data_length = received_msg[14:15]
            data = received_msg[15:]

        

        if dest_mac != node1_mac:
            print("\nPACKET DROPPED")
        elif dest_ip == node2_ip and sorc_ip ==node3_ip:
            sniffing_log(data, sorc_ip, dest_ip, 1)
        elif dest_ip == node3_ip and sorc_ip == node2_ip:
            sniffing_log(data, sorc_ip, dest_ip, 1)
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
                ethernet_header = node1_mac + router_mac
                IP_header = node1_ip + sorc_ip + protocol
                packet = ethernet_header + IP_header + data_length + data
                node1.send(bytes(packet, "utf-8"))
            elif protocol == "1K":
                print("EXIT")
            send_packet()  

send_packet()  
receive_packet("")

node1.close()
