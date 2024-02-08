import socket
import time

# arbitrary client2 IP and MAC
client2_ip = "92.10.10.20"
client2_mac = "10:AF:CB:EF:19:CF"

# client2 socket
client2 = socket.socket()

# client2 connects to router
time.sleep(1)
router = ("localhost", 8200)
client2.connect(router)

# when connected to router, receives frames
while True:
    received_message = client2.recv(1024)
    received_message = received_message.decode("utf-8")

    source_mac = received_message[0:17]
    destination_mac = received_message[17:34]
    source_ip = received_message[34:45]
    destination_ip =  received_message[45:56]
    message = received_message[56:]

    print("\nPacket integrity:")
    print("\ndestination MAC address matches client 2 MAC address: {mac}".format(mac=(client2_mac == destination_mac)))
    print("\ndestination IP address matches client 2 IP address: {mac}".format(mac=(client2_ip == destination_ip)))

    print("\nThe packed received:")
    print("\n Source MAC address: {source_mac}, Destination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
    print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
    print("\nMessage: " + message)