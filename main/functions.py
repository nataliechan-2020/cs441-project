from logs import flag_ip_spoofing, log
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt(plaintext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    padtext = pad(plaintext, AES.block_size)
    ctext = cipher.encrypt(padtext)
    encodedctext= base64.b64encode(ctext)
    return encodedctext

def decrypt(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    decodedctext = base64.b64decode(ciphertext)
    padded_plaintext = cipher.decrypt(decodedctext)
    plaintext = unpad(padded_plaintext, AES.block_size)
    return plaintext

def save_key(key):
    with open("key.bin", "wb") as key_file:
        key_file.write(key)

def load_key():
    with open("key.bin", "rb") as key_file:
        return key_file.read()
    
# key = str.encode("1234567812345678")


def receive_router (received_message, node, compare, arp_mac):
    received_message = received_message.split(',')
    # print(received_message)

    sorc_mac = received_message[0]
    dest_mac = received_message[1]
    payload_length = received_message[2]
    sorc_ip = received_message[3]
    dest_ip = received_message[4]
    protocol = received_message[5]
    data_length = received_message[6]
    data = received_message[7]

    packet_dropped = False
    if node == 2:
        if dest_mac != compare:
            print("\n PACKET DROPPED")
            packet_dropped = True
    elif node ==3:
        if dest_ip != compare:
            print("\n PACKET DROPPED")
            packet_dropped = True 
    if packet_dropped == False:
        if (arp_mac[sorc_ip] != sorc_mac):
            flag_ip_spoofing(sorc_ip, dest_ip)
        else:
            log(sorc_ip, dest_ip, data)
            
        print("\nINCOMING PACKET {node}:".format(node=node))
        print("Source MAC address:", sorc_mac, "\nDestination MAC address:", dest_mac)
        print("MAC payload length:", payload_length)
        print("Source IP address:", sorc_ip, "\nDestination IP address:", dest_ip)
        print("Protocol:", protocol)
        print("Data length:", data_length)
        print("Protocol flag:", data[0])
        print("Data:", data[1:])
    
    return sorc_mac, sorc_ip, payload_length, dest_mac, dest_ip, protocol, data_length, data, packet_dropped

def send_node(node, ip1, ip2, current_ip, current_mac, router_mac, arp_mac, ethernet_header, IP_header):
    
    data = input("Enter data: ")
    data_length = len(data)
    while data_length > 251:
        print("[ERROR] Data too large")
        data = input("Enter data: ")
        data_length = len(data)

    protocol = input("Enter protocol: ")
    while protocol != "0" and protocol != "1":
        print("[ERROR] Wrong protocol inputed")
        protocol = input("Enter protocol: ")

    dest_ip = input("Enter destination IP: ")
    while dest_ip != ip1 and dest_ip != ip2:
        print("[ERROR] Wrong destination IP inputed")
        dest_ip = input("Enter destination IP: ")

    if protocol == "0":
        data = "P" + data
    else:
        data = "K" + data

    data_length = len(data)

    key = load_key()
   

    if node == 1:
        IP_header = IP_header + current_ip + "," + dest_ip + "," + protocol
        ethernet_header = ethernet_header + current_mac + "," + router_mac
    elif node ==2:
        print(ip1)
        # Spoofing START
        if dest_ip == ip1:
            spoofed_sorc_ip = ip2  
            dest_mac = arp_mac[ip1]
        
            IP_header = IP_header + spoofed_sorc_ip + "," + dest_ip + "," + protocol
            ethernet_header = ethernet_header + current_mac + "," + dest_mac
        else:
            IP_header = IP_header + current_ip + "," + dest_ip + "," + protocol
            ethernet_header = ethernet_header + current_mac + "," + arp_mac[dest_ip]
        # Spoofing ENDS
    else:
        IP_header = IP_header + current_ip + "," + dest_ip + "," + protocol
        ethernet_header = ethernet_header + current_mac + "," + arp_mac[dest_ip]
    
    print(data)
    protocol = data[0]
    data= data[1:]
    data = data.encode()
    data = encrypt(data, key)
    data = data.decode()
    payload = IP_header + "," + str(data_length) + "," + protocol + data
    payload_length = len(payload) - 4
    packet = ethernet_header + "," + str(payload_length) + "," + payload
    
    return packet