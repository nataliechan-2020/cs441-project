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

# (WIP) keeping connection open
# while True:





