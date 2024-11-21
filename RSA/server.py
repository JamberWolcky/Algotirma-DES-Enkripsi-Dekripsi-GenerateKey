import socket
from threading import Thread
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from des import des_encrypt, des_decrypt

# Generate RSA Key Pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Serialize the public key
serialized_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Simpan koneksi dan kunci client
clients = {}

def handle_client(conn, client_id):
    # Kirim public key RSA ke client
    conn.send(serialized_public_key)
    print(f"Public key sent to {client_id}.")

    # Terima encrypted DES key dari client
    encrypted_des_key = conn.recv(2048)
    try:
        des_key = private_key.decrypt(
            encrypted_des_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()
        print(f"{client_id} DES key decrypted: {des_key}")
        
        # Simpan informasi client
        clients[client_id] = {
            'connection': conn, 
            'des_key': des_key
        }
    except Exception as e:
        print(f"Error decrypting DES key for {client_id}: {e}")
        conn.close()
        return

    while True:
        try:
            # Terima pesan dari client
            data = conn.recv(2048).decode()
            if not data or data == 'exit':
                break

            # Parse data
            target_client_id, encrypted_message = data.split(':', 1)
            
            # Dekripsi pesan
            cipher_bits = [int(bit) for bit in encrypted_message]
            decrypted_message = des_decrypt(cipher_bits, des_key)
            
            print(f"Message from {client_id} to {target_client_id}: {decrypted_message}")
            
            # Kirim pesan ke client tujuan
            if target_client_id in clients:
                target_conn = clients[target_client_id]['connection']
                target_des_key = clients[target_client_id]['des_key']
                
                # Enkripsi pesan untuk client tujuan
                response_message = f"{client_id}: {decrypted_message}"
                encrypted_response = des_encrypt(response_message, target_des_key)
                target_conn.send(f"{client_id}:{''.join(map(str, encrypted_response))}".encode())
            
        except Exception as e:
            print(f"Error handling message from {client_id}: {e}")
            break

    conn.close()
    del clients[client_id]
    print(f"{client_id} disconnected.")

def server_program():
    host = '127.0.0.1'
    port = 65432
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)
    print("Server is listening...")

    client_ids = ['Client1', 'Client2']
    for client_id in client_ids:
        conn, address = server_socket.accept()
        print(f"{client_id} connected from {address}")
        Thread(target=handle_client, args=(conn, client_id)).start()

if __name__ == "__main__":
    server_program()
