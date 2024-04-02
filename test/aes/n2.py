import socket
import threading
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def receive_messages(conn):
    while True:
        data = conn.recv(1024).decode()
        # print("\nReceived:", data)
        decrypted = decrypt(data, key)
        print("\nThe decrypted data is:", decrypted.decode('utf-8'))

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

key = str.encode("1234567812345678")

router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router_socket.connect(('localhost', 8001))

receive_thread = threading.Thread(target=receive_messages, args=(router_socket,))
receive_thread.start()

while True:
    # key = get_random_bytes(16) 
    plaintext = input("Node2 - Enter message: ").encode()
    enc = encrypt(plaintext, key)
    router_socket.sendall(enc)


