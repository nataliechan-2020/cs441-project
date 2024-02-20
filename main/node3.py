import socket
import time

# initialise IP and MAC addresses
node3_ip = "0x2B"
node3_mac = "N3"

# sockets
node3 = socket.socket()
intra3 = socket.socket()

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node3.connect(router)

# connect to node 2
time.sleep(1)
intra2 = ("localhost", 2000)
intra3.connect(intra2)

# (WIP) keeping connection open:
#   code to refer -> server demo for packet setup and sending
#                 -> client demo for packet receival
#   MAC broadcast -> unicast (one-to-one), packet iteratively sent to each node in each network
#                 -> multiple packets with diff dest MACs (node2_mac, router2_mac)
#                 -> drop incoming packet if dest IP != node3_ip

# while True: