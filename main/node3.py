import socket
import time

# initialise IP and MAC addresses
node3_ip = "0x2B"
node3_mac = "N3"

# socket
node3 = socket.socket()

# connect to router
time.sleep(1)
router = ("localhost", 2200)
node3.connect(router)

# (WIP) keeping connection open
# while True:


