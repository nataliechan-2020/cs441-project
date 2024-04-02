import socket
import time
import threading
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

def receive_packet():
    # print(received_msg)
    while True:
        # Receive data from router
        # if received_msg== "": 
        received_message = node1.recv(1024)
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

        # else:
        #     sorc_mac = received_msg[0]
        #     dest_mac = received_msg[1]
        #     payload_length = received_msg[2]
        #     sorc_ip = received_msg[3]
        #     dest_ip =  received_msg[4]
        #     protocol = received_msg[5]
        #     data_length = received_msg[6]
        #     data = received_msg[7]

        protocol_flag = data[0]
        data = data[1:]

        if dest_mac != node1_mac:
            print("\nPACKET DROPPED")
        # log
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
            print("Protocol flag:", protocol_flag)
            print("Data: " + data)

            # ping reply, unicast -> reply to router and node3
            if protocol == "0" and protocol_flag == "P":
                data = "R" + data
                ethernet_header = node1_mac + "," + router_mac
                IP_header = node1_ip + "," + sorc_ip + "," + protocol

                payload = IP_header + "," + data_length + "," + data
                # print(payload)
                payload_length = len(payload) - 4
                packet = ethernet_header + "," + str(payload_length) + "," + payload
                
                # print(packet)
                node1.send(bytes(packet, "utf-8"))
            elif protocol == "1" and protocol_flag == "K":
                print("EXIT")
            # send_packet()  


receive_thread = threading.Thread(target=receive_packet)
receive_thread.start()

# def send_packet():
# main thread, sending
# receive_packet("")
while True:
    print("\nOUTGOING PACKET:")
    ethernet_header = ""
    IP_header = ""
    
    packet = send_node(1, node2_ip, node3_ip, node1_ip, node1_mac, router_mac, None, ethernet_header, IP_header)
    node1.send(bytes(packet, "utf-8"))

    # node1.settimeout(15)
    # try:
        # Check if got receive any message
    

    # received_message = node1.recv(1024)
    # if received_message:
    #     received_message = received_message.decode("utf-8")
    #     received_message = received_message.split(',')
        
    #     data_size = received_message[6]

    #     if int(data_size) > 0:
    #         receive_packet(received_message)
    #         break
        
        # except TimeoutError:
        #     packet = send_node(1, node2_ip, node3_ip, node1_ip, node1_mac, router_mac, None, ethernet_header, IP_header)
        #     node1.send(bytes(packet, "utf-8"))
            
        #     break
        # break



# send_packet()  
# receive_packet("")

# node1.close()
