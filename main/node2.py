import socket
import time

# initialise IP and MAC addresses
node2_ip = "0x2A"
node2_mac = "N2"

# socket
node2 = socket.socket()

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node2.connect(router)

# (WIP) keeping connection open
# while True:


