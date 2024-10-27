import socket

# Fungsi DES yang sudah ada
# Anda bisa paste kode DES yang sudah Anda berikan sebelumnya di sini.

def client_program():
    host = '127.0.0.1'  # alamat IP localhost
    port = 65432        # port yang digunakan server

    # Membuat socket
    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Membuat pesan dan key yang akan dikirim
    message = "Keamanan Informasi B"
    key = "abcd1234"

    # Mengirim pesan dan key ke server
    data_to_send = f"{key}|{message}"
    client_socket.send(data_to_send.encode())
    print("Pesan asli dan key berhasil dikirim ke server.")

    client_socket.close()

if __name__ == '__main__':
    client_program()
