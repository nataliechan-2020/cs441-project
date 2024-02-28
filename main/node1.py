import socket
import time

# 1) initialise IP and MAC addresses
node1_ip = "0x1A"
node1_mac = "N1"

# 2) socket
node1 = socket.socket()

# 3) connect to router on port 1200
time.sleep(1)
router = ("localhost", 1200)
node1.connect(router)
            



# (WIP) keeping connection open:
#   code to refer -> server demo for packet setup and sending
#                 -> client demo for packet receival
#   MAC broadcast -> unicast (one-to-one), packet sent to each node in each network
#                 -> only one other node in network aka router1


# 4) for RECEIVING frames from the router
# when connected to router, receives frames - from the router
while True:
    received_message = node1.recv(1024)
    received_message = received_message.decode("utf-8")

    source_mac = received_message[0:17]
    destination_mac = received_message[17:34]
    source_ip = received_message[34:45]
    destination_ip =  received_message[45:56]
    message = received_message[56:]

    print("\nPacket integrity:")
    print("\ndestination MAC address matches client 1 MAC address: {mac}".format(mac=(node1_mac == destination_mac)))
    print("\ndestination IP address matches client 1 IP address: {mac}".format(mac=(node1_ip == destination_ip)))

    print("\nThe packed received:")
    print("\n Source MAC address: {source_mac}, Destination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("\nMessage: " + message)


#5) Qn: the identation?
# server socket listens for router connection (router connects to this)
    node1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node1.bind(("localhost", 1200))
    node1.listen(2)

    # router MAC
    router_mac = "R1" # this is mac right? for the network node 1 is in?

    # node1 accepts router connection
    while True:
        routerConnection, address = node1.accept()
        if(routerConnection != None):
            print(routerConnection)
            break

    # after accepting, node1 sends frames to router
    while True:
        ethernet_header = ""
        IP_header = ""
        
        message = input("\nEnter the text message to send: ")
        destination_ip = input("Enter the IP of the clients to send the message to:\n1. 92.10.10.15\n2. 92.10.10.20\n3. 92.10.10.25\n")
        
        if(destination_ip == "0x11"): # this is router 1's IP right?
            source_ip = node1_ip
            IP_header = IP_header + source_ip + destination_ip
            
            source_mac = node1_mac
            destination_mac = router_mac 
            ethernet_header = ethernet_header + source_mac + destination_mac
            
            packet = ethernet_header + IP_header + message
            
            routerConnection.send(bytes(packet, "utf-8"))  
        else:
            print("Wrong client IP inputted")
        


#Qns: how do i test this? how to run this file?
# is the file supposed to look like this --> or 2 diff files for each node for the client & server programs?
# node is both a client & server  - to allow 2-directional sending & recieving -  means each node must be able to send & receive

    