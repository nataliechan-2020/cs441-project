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