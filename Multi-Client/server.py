import socket
import threading
import os
import hashlib
import struct
import random
import time

# Constants
CHUNK_SIZE = 1024
HEADER_SIZE = 8  # 4 bytes for sequence number + 4 bytes for client ID
HOST = '127.0.0.1'
PORT = 5001
DROP_PROBABILITY = 0.1  # Simulate 10% packet drop

# Function to compute SHA256 checksum
def compute_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

# Function to handle client connection
def handle_client(client_socket, client_id):
    try:
        # Receive file name
        file_name = client_socket.recv(1024).decode()
        if not file_name:
            return

        print(f"[Client {client_id}] Uploading file: {file_name}")

        # Save received file
        received_file_path = f"received_{client_id}_{file_name}"
        with open(received_file_path, 'wb') as f:
            while True:
                chunk = client_socket.recv(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)

        # Compute checksum
        checksum = compute_checksum(received_file_path)
        print(f"[Client {client_id}] File received. Checksum: {checksum}")

        # Read file and send back in chunks
        with open(received_file_path, 'rb') as f:
            seq_num = 0
            while chunk := f.read(CHUNK_SIZE):
                header = struct.pack("!II", seq_num, client_id)  # Sequence num + Client ID
                if random.random() > DROP_PROBABILITY:  # Simulate random packet drop
                    client_socket.sendall(header + chunk)
                else:
                    print(f"[Client {client_id}] Dropped packet {seq_num}")
                seq_num += 1

        # Send "END" marker
        client_socket.sendall(b"END")

        # Send checksum
        client_socket.sendall(checksum.encode())

        print(f"[Client {client_id}] File transfer complete!")

    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")
    finally:
        client_socket.close()

# Start server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    client_id = 1
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[New Connection] Client {client_id} from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        client_thread.start()
        client_id += 1

if __name__ == "__main__":
    start_server()
