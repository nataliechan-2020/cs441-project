import socket
import threading

def handle_node(conn, node_name, other_conn):
    while True:
        data = conn.recv(1024).decode()
        if not data:
            print(f"{node_name} disconnected.")
            break
        print(f"Received from {node_name}: {data}")
        other_conn.sendall(data.encode())

node1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
node1_socket.bind(('localhost', 8000))
node1_socket.listen(1)
print("Waiting for Node1 to connect...")
node1_conn, node1_addr = node1_socket.accept()
print("Node1 connected.")

node2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
node2_socket.bind(('localhost', 8001))
node2_socket.listen(1)
print("Waiting for Node2 to connect...")
node2_conn, node2_addr = node2_socket.accept()
print("Node2 connected.")

node1_thread = threading.Thread(target=handle_node, args=(node1_conn, "Node1", node2_conn))
node1_thread.start()

node2_thread = threading.Thread(target=handle_node, args=(node2_conn, "Node2", node1_conn))
node2_thread.start()
