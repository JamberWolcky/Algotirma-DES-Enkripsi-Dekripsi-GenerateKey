import socket
import pickle
from rsa import generate_keypair, hybrid_encrypt, hybrid_decrypt

def client_program():
    host = '127.0.0.1'
    port = 3000

    print("Generating RSA keypair...")
    public_key, private_key = generate_keypair()

    des_key = "client01"

    client_name = "client1"

    try:
        # Initialize socket dan koneksi
        client_socket = socket.socket()
        client_socket.connect((host, port))
        print("Connected to server")

        # Kirim public key ke server
        client_socket.send(pickle.dumps(public_key))
        print("Sent public key to server")

        # Terima public key lawan dari server
        other_client_public_key = pickle.loads(client_socket.recv(4096))
        print("Received other client's public key")

        # Tampilkan private key ke layar console setelah terhubung
        print(f"Private Key (d, n): {private_key}")

        message = input(" -> ")

        while message.lower().strip() != 'bye':
            if message:
                try:
                    encrypted_message, encrypted_des_key = hybrid_encrypt(
                        message,
                        des_key,
                        other_client_public_key
                    )

                    data_packet = {
                        'encrypted_message': encrypted_message,
                        'encrypted_des_key': encrypted_des_key,
                        'sender_public_key': public_key,
                        'sender_name': client_name
                    }

                    client_socket.send(pickle.dumps(data_packet))

                except Exception as e:
                    print(f"Error encrypting message: {e}")
                    continue

            try:
                encrypted_data = pickle.loads(client_socket.recv(4096))
                if encrypted_data:
                    # Verifikasi pengirim menggunakan public key
                    sender_public_key = encrypted_data['sender_public_key']
                    sender_name = encrypted_data['sender_name']  # Ambil nama pengirim

                    # Dekripsi pesan menggunakan private key sendiri
                    decrypted_message = hybrid_decrypt(
                        encrypted_data['encrypted_message'],
                        encrypted_data['encrypted_des_key'],
                        private_key
                    )

                    print(f'Received from {sender_name}: {decrypted_message}')

            except Exception as e:
                print(f"Error receiving/decrypting message: {e}")
                continue

            message = input(" -> ")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client_socket.close()
        print("Connection closed")

if __name__ == '__main__':
    client_program()