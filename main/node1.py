import socket
import time

# initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# socket
node1 = socket.socket()

# connect to router
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router)

# (WIP) keeping connection open:
#   code to refer -> server demo for packet setup and sending
#                 -> client demo for packet receival
#   MAC broadcast -> unicast (one-to-one), packet sent to each node in each network
#                 -> only one other node in network aka router1

# while True: