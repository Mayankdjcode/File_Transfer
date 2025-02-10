import socket
import hashlib
import os
import struct

# Constants
CHUNK_SIZE = 1024
HEADER_SIZE = 4  # 4 bytes for sequence number
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

    chunks = {}

    while True:
        # Ensure we receive exactly 4 bytes for the sequence number
        header = client_socket.recv(HEADER_SIZE)
        if not header or len(header) < HEADER_SIZE:
            #print("❌ Error: Incomplete sequence number received. Stopping reception.")
            break

        seq_num = struct.unpack("!I", header)[0]  # Extract sequence number

        # Receive file chunk
        chunk = client_socket.recv(CHUNK_SIZE)

        # Check if we received the END marker
        if chunk == b"END":
            break

        chunks[seq_num] = chunk

    # Receive checksum
    received_checksum = client_socket.recv(1024).decode().strip()

    # Ensure we received a valid checksum
    if not received_checksum:
        print("❌ Error: Did not receive checksum from the server.")
        client_socket.close()
        return

    # Sort chunks by sequence number
    sorted_chunks = [chunks[i] for i in sorted(chunks.keys())]

    # Save reconstructed file
    received_file_path = f"reconstructed_{file_name}"
    with open(received_file_path, 'wb') as f:
        for chunk in sorted_chunks:
            f.write(chunk)

    # Compute checksum of reconstructed file
    computed_checksum = compute_checksum(received_file_path)

    print(f"Received checksum: {received_checksum}")
    print(f"Computed checksum: {computed_checksum}")
    if received_checksum == computed_checksum:
        print("✅ Transfer Successful!")
    else:
        print("❌ Transfer Failed: Checksum mismatch!")

    client_socket.close()

# Run the client
if __name__ == "__main__":
    client("test.txt")
