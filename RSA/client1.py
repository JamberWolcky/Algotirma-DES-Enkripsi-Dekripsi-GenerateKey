import socket
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from des import des_encrypt, des_decrypt

def client1_program():
    host = '127.0.0.1'
    port = 65432
    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Receive RSA public key from server
    serialized_public_key = client_socket.recv(2048)
    public_key = serialization.load_pem_public_key(serialized_public_key)
    print(f"Received public key from server: {public_key}")

    # DES key
    des_key = "abcd1234"  # Unique key for this client

    # Encrypt DES key with RSA public key
    encrypted_des_key = public_key.encrypt(
        des_key.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    client_socket.send(encrypted_des_key)
    print("Encrypted DES key sent to server.")

    while True:
        print("\nMenu:")
        print("1. Send Message to Client2")
        print("2. Exit")
        choice = input("Choose an option: ")

        if choice == '2':
            client_socket.send('exit'.encode())
            break

        if choice == '1':
            message = input("Enter message for Client2: ")
            
            # Encrypt the message using DES
            encrypted_message = des_encrypt(message, des_key)
            
            # Send to server with target client
            client_socket.send(f"Client2:{''.join(map(str, encrypted_message))}".encode())
            print("Message sent to server.")

            # Wait for response
            data = client_socket.recv(2048).decode()
            sender, encrypted_response = data.split(':', 1)
            cipher_bits_response = [int(bit) for bit in encrypted_response]
            decrypted_response = des_decrypt(cipher_bits_response, des_key)
            print(f"Response from {sender}: {decrypted_response}")

    client_socket.close()


if __name__ == "__main__":
    client1_program()