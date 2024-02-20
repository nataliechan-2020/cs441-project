import socket
import time

# initialise IP and MAC addresses
router1_ip = "0x11"
router1_mac = "R1"
router2_ip = "0x21"
router2_mac = "R2"

# socket (network 1)
router1 = socket.socket()
router1.bind(("localhost", 1200))

# socket (network 2)
router2 = socket.socket()
router2.bind(("localhost", 2200))

# from network 1
router1.listen(2)
node1 = None

while (node1 == None):
    if (node1 == None):
        node1, address = router1.accept()
        print("Node 1 online") 

# from network 2
router2.listen(4)
node2 = None
node3 = None

while (node2 == None or node3 == None):
    node, address = router2.accept()
    
    if (node2 == None):
        node2 = node
        print("Node 2 online")
    
    elif (node3 == None):
        node3 = node
        print("Node 3 online")

# (WIP) keeping connection open:
#   code to refer -> router demo for packet receival and sending
#   MAC broadcast (network 1) -> unicast (one-to-one), packet sent to each node in each network
#                             -> only one other node in network aka node1
#   MAC broadcast (network 2) -> unicast (one-to-one), packet sent to each node in each network
#                             -> multiple packets with diff dest MACs (node2_mac, node3_mac)
#                             -> drop incoming packet if dest IP != node1_ip OR router2_ip

# while True: