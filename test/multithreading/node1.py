import socket
import threading

def receive_messages(conn):
    while True:
        data = conn.recv(1024).decode()
        print("\nReceived:", data)

router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router_socket.connect(('localhost', 8000))

receive_thread = threading.Thread(target=receive_messages, args=(router_socket,))
receive_thread.start()

while True:
    message = input("Node1 - Enter message: ")
    router_socket.sendall(message.encode())
