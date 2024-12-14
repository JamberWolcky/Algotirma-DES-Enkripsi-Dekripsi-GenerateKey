import socket
import pickle

def server_program():
    host = '127.0.0.1'
    port = 3000

    print("Host:", host)
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)

    # Menyimpan koneksi client dan public key mereka
    clients = []
    client_keys = {}

    # Terima koneksi dari 2 client
    print("Waiting for clients...")
    for i in range(2):
        conn, address = server_socket.accept()
        client_name = f"client{i+1}"
        print(f"Connection from {client_name}: {address}")

        # Terima public key dari client
        client_public_key = pickle.loads(conn.recv(4096))
        client_keys[client_name] = client_public_key

        print(f"Received public key from {client_name}: {client_public_key}")

        clients.append((conn, client_name))

    # Kirim public key client2 ke client1 dan sebaliknya
    for i, (conn, client_name) in enumerate(clients):
        other_client_name = "client2" if client_name == "client1" else "client1"
        other_client_key = client_keys[other_client_name]  # Hanya kirim public key

        # Kirim public key lawan ke masing-masing client
        conn.send(pickle.dumps(other_client_key))
        print(f"Sent {other_client_name}'s public key to {client_name}")

    print("Key exchange completed. Starting message relay...")

    # Loop utama untuk meneruskan pesan
    while True:
        for conn, client_name in clients:
            try:
                # Terima data terenkripsi dalam bentuk biner tanpa decoding
                encrypted_data = conn.recv(4096)
                print(f"Received encrypted data from {client_name}: {encrypted_data}")
                if not encrypted_data:
                    continue

                # Tentukan penerima
                recipient_conn = clients[1][0] if client_name == "client1" else clients[0][0]

                # Teruskan data terenkripsi ke penerima tanpa encode/decode
                recipient_conn.send(encrypted_data)
                print(f"Forwarded encrypted message from {client_name} to {recipient_conn}")

            except Exception as e:
                print(f"Error handling message from {client_name}: {e}")
                continue

    server_socket.close()

if __name__ == '__main__':
    server_program()