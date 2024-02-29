import socket
import time
import threading

# initialise IP and MAC addresses
node2_ip = "0x2A"
node2_mac = "N2"

# sockets
node2 = socket.socket()
intra2 = socket.socket()
intra2.bind(("localhost", 2000))

# accept node 3
intra2.listen(2)
node3 = None

while (node3 == None):
    if (node3 == None):
        node3, address = intra2.accept()
        print("Node 3 online") 

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node2.connect(router)

# (WIP) keeping connection open:
#   code to refer -> server demo for packet setup and sending
#                 -> client demo for packet receival
#   MAC broadcast -> unicast (one-to-one), packet iteratively sent to each node in each network
#                 -> multiple packets with diff dest MACs (node3_mac, router2_mac)
#                 -> drop incoming packet if dest IP != node2_ip

# while True:

# (WIP) keeping connection open:

def send_to_node3(msg):
    node3.send(msg.encode())

def receive_from_node3():
    while True:
        received_message = node3.recv(1024)
        received_message = received_message.decode("utf-8")

        source_mac = received_message[0:17]
        destination_mac = received_message[17:34]
        source_ip = received_message[34:45]
        destination_ip =  received_message[45:56]
        message = received_message[56:]

        print("\nPacket integrity:")
        print("\ndestination MAC address matches node2 MAC address: {mac}".format(mac=(node2_mac == destination_mac)))
        print("\ndestination IP address matches node2 IP address: {mac}".format(mac=(node2_ip == destination_ip)))

        print("\nThe packed received:")
        print("\n Source MAC address: {source_mac}, Destination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
        print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
        print("\nMessage: " + message)

# Start a thread for receiving messages from Node 3
receive_thread = threading.Thread(target=receive_from_node3)
receive_thread.daemon = True
receive_thread.start()

# Main loop for sending messages to Node 3
while True:
    msg = input("Enter message to send to Node 3: ")
    send_to_node3(msg)