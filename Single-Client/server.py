import socket
import hashlib
import os
import random
import struct
import time

# Constants
CHUNK_SIZE = 1024
HOST = '127.0.0.1'
PORT = 5001

# Function to compute SHA256 checksum
def compute_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

# Server function
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("Server is listening...")

    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    # Receive file name
    file_name = conn.recv(1024).decode().strip()
    print(f"Receiving file: {file_name}")

    # Read the file and split into chunks
    with open(file_name, 'rb') as f:
        chunks = []
        seq_num = 0
        while chunk := f.read(CHUNK_SIZE):
            chunks.append((seq_num, chunk))
            seq_num += 1

    # Compute checksum
    checksum = compute_checksum(file_name)

    # Shuffle chunks to simulate out-of-order transmission
    random.shuffle(chunks)

    # Send each chunk with sequence number
    for seq_num, chunk in chunks:
        header = struct.pack("!I", seq_num)  # Convert sequence number to 4 bytes
        conn.sendall(header + chunk)
        time.sleep(0.01)  # Simulate network delay

    # Send END marker
    conn.sendall(b"END")

    # Send checksum
    time.sleep(1)  # Ensure checksum is sent after file data
    conn.sendall(checksum.encode())

    print(f"File sent successfully with {len(chunks)} chunks.")
    
    conn.close()
    server_socket.close()

# Run the server
if __name__ == "__main__":
    server()
