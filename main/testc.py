import socket
import threading
import time

node3_ip = "0x2B"
node3_mac = "N3"

# node3 will not communicate with node1_mac and node2_mac
# node3 is unlikely to communicate with router_ip

router_ip = "0x21" #
router_mac = "R2"
node1_ip = "0x1A"
node1_mac = "N1" #
node2_ip = "0x2A"
node2_mac = "N2" #

# connect to router
time.sleep(1)
router = ("localhost", 2200) # ip address: "localhost", port number: 2200
node3 = socket.socket()
node3.connect(router) 

def send():
    # sending
    print("\n-Outgoing Message-\n")

    data = input("Enter data: ")
    data_length = len(data)
    while data_length >= 10: # why 10 ah
        data = input("Data too large, please enter data for suitable size: ")
        data_length = len(data)

    protocol = str(input("Enter protocol: "))
    while protocol != "0" and protocol != "1":
        protocol = str(input("Wrong protocol, please enter either 0 or 1: "))

    destination_ip = input("Enter destination IP: ")
    while destination_ip != node1_ip and destination_ip != node2_ip:
        destination_ip = input("Wrong destination IP, please enter either 0x1A or 0x2A: ")

    # ethernet frame
    source_mac = node3_mac
    destination_mac = router_mac
    ethernet_header = source_mac + destination_mac
    ethernet_frame  = source_mac + destination_mac + str(data_length) + data

    # ip packet
    source_ip = node3_ip
    ip_header = source_ip + destination_ip + protocol
    ip_packet = source_ip + destination_ip + protocol + str(data_length) + data

    # packet
    packet = ethernet_header + ip_header + str(data_length) + data

    print(ethernet_frame)
    print(ip_packet)
    print(packet)

    node3.send(bytes(packet, "utf-8"))



def receive():
    # receiving
    message = node3.recv(1024).decode()

    source_mac = message[0:2]
    destination_mac = message[2:4]
    source_ip = message[4:8]
    destination_ip = message[8:12]
    protocol = message[12:13]
    data_length = message[13:14]
    data = message[14:]

    print("\n-Message Received-\n")
    print(data)

    if protocol ==  "0":
        new_source_mac = destination_mac
        new_destination_mac = source_mac
        new_source_ip = destination_ip
        new_destination_ip = source_ip
        new_protocol  = "1"
        packet = new_source_mac + new_destination_mac + new_source_ip + new_destination_ip + new_protocol + data_length + data
        node3.send(bytes(packet, "utf-8"))

thread1 = threading.Thread(target = send)
thread2 = threading.Thread(target = receive)
thread1.start()
thread2.start()

while True:
    pass

# source_mac|destination_mac|source_ip|destination_ip|protocol|data_length|data