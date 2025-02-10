import socket
import os
import struct
import hashlib

# Constants
CHUNK_SIZE = 1024
HEADER_SIZE = 8
HOST = '127.0.0.1'
PORT = 5001

# Function to compute SHA256 checksum
def compute_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

# Client function
def client(file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    file_name = os.path.basename(file_path)
    client_socket.sendall(file_name.encode())

    # Send file to server
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            client_socket.sendall(chunk)

    # Receive chunks back
    chunks = {}
    while True:
        header = client_socket.recv(HEADER_SIZE)

        if not header or header == b"END":
            break

        seq_num, client_id = struct.unpack("!II", header)
        chunk = client_socket.recv(CHUNK_SIZE)
        chunks[seq_num] = chunk

    # Receive checksum
    received_checksum = client_socket.recv(1024).decode().strip()
    client_socket.close()

    # Reassemble file
    received_file_path = f"reconstructed_{file_name}"
    with open(received_file_path, 'wb') as f:
        for i in sorted(chunks.keys()):
            f.write(chunks[i])

    # Verify checksum
    computed_checksum = compute_checksum(received_file_path)
    print(f"Received checksum: {received_checksum}")
    print(f"Computed checksum: {computed_checksum}")
    if received_checksum == computed_checksum:
        print("✅ Transfer Successful!")
    else:
        print("❌ Transfer Failed: Checksum mismatch!")

if __name__ == "__main__":
    client("test.txt")
