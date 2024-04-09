import socket
import time 

# arbitrary client1 IP and MAC
client1_ip = "92.10.10.15"
client1_mac = "32:04:0A:EF:19:CF"

# client1 socket
client1 = socket.socket()

# client1 connects to router
time.sleep(1)
router = ("localhost", 8200)
client1.connect(router)

# when connected to router, receives frames
while True:
    received_message = client1.recv(1024)
    received_message = received_message.decode("utf-8")

    source_mac = received_message[0:17]
    destination_mac = received_message[17:34]
    source_ip = received_message[34:45]
    destination_ip =  received_message[45:56]
    message = received_message[56:]

    print("\nPacket integrity:")
    print("\ndestination MAC address matches client 1 MAC address: {mac}".format(mac=(client1_mac == destination_mac)))
    print("\ndestination IP address matches client 1 IP address: {mac}".format(mac=(client1_ip == destination_ip)))

    print("\nThe packed received:")
    print("\n Source MAC address: {source_mac}, Destination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("\nMessage: " + message)